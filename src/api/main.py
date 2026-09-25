from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.data.loader import carregar_filmes
from src.data.ratings_matrix import carregar_ratings_1m, carregar_titulos_1m
from src.recommenders.collaborative import FiltragemColaborativa
from src.recommenders.content_recommender import filmes_parecidos
from src.services.catalog_service import buscar_filme
from src.services.home_service import fileiras_padrao, fileiras_recomendadas, montar_home
from src.services.perfil_service import guardar_notas, ler_notas

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UM_ANO = 60 * 60 * 24 * 365

app = FastAPI(title="MarioFlix")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "template")
# O navegador guarda CSS e JS em cache. Colocar a data de modificação na URL faz ele baixar o arquivo novo quando muda.
templates.env.globals["versao"] = lambda nome: int((STATIC_DIR / nome).stat().st_mtime)

FILMES = carregar_filmes()
FILMES_POR_ID = {f["movieId"]: f for f in FILMES}
MODELO = FiltragemColaborativa(carregar_ratings_1m(), carregar_titulos_1m())
FILEIRAS_PADRAO = fileiras_padrao(MODELO, FILMES_POR_ID)  # calculadas uma vez, ao ligar o servidor


@lru_cache(maxsize=128)
def _recomendadas_do_visitante(notas_do_cookie):
    # Guarda o resultado de cada conjunto de notas: quem só navega não recalcula a cada página.
    return fileiras_recomendadas(MODELO, ler_notas(notas_do_cookie), FILMES_POR_ID, FILEIRAS_PADRAO)


@app.get("/")
def home(request: Request):
    notas = ler_notas(request.cookies.get("notas"))
    contexto = montar_home(FILMES, _recomendadas_do_visitante(guardar_notas(notas)))
    contexto["assistidos"] = set(notas)
    return templates.TemplateResponse(request, "home.html", contexto)


@app.get("/filmes")
def listagem(request: Request):
    return templates.TemplateResponse(request, "listagem.html", {
        "filmes": FILMES,
        "assistidos": set(ler_notas(request.cookies.get("notas"))),
    })


@app.get("/filme/{movie_id}")
def detalhe(request: Request, movie_id: str):
    filme = buscar_filme(FILMES_POR_ID, movie_id)
    if not filme:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    notas = ler_notas(request.cookies.get("notas"))
    return templates.TemplateResponse(request, "detalhe.html", {
        "filme": filme,
        "parecidos": filmes_parecidos(filme, FILMES),
        "nota_usuario": notas.get(int(movie_id)),
        "assistidos": set(notas),
    })


@app.post("/avaliar/{movie_id}")
def avaliar(request: Request, movie_id: str, nota: int = Form(...)):
    """Guarda a nota do visitante no cookie (nota 0 remove a avaliação)."""
    if not buscar_filme(FILMES_POR_ID, movie_id):
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    if not 0 <= nota <= 5:
        raise HTTPException(status_code=422, detail="A nota vai de 1 a 5")

    notas = ler_notas(request.cookies.get("notas"))
    if nota == 0:
        notas.pop(int(movie_id), None)
    else:
        notas[int(movie_id)] = float(nota)

    resposta = RedirectResponse(f"/filme/{movie_id}", status_code=303)
    if notas:
        resposta.set_cookie("notas", guardar_notas(notas), max_age=UM_ANO, httponly=True, samesite="lax")
    else:
        resposta.delete_cookie("notas")
    return resposta
