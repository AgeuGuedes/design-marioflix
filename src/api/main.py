from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.data.loader import carregar_filmes
from src.data.ratings_matrix import carregar_matriz_usuario_item
from src.recommenders.content_recommender import filmes_parecidos
from src.recommenders.item_based_recommender import recomendar as recomendar_item_item
from src.recommenders.user_based_recommender import recomendar as recomendar_user_user
from src.services.catalog_service import buscar_filme
from src.services.home_service import USUARIO_DEMO, montar_home

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="MarioFlix")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "template")

FILMES = carregar_filmes()
FILMES_POR_ID = {f["movieId"]: f for f in FILMES}
NOTAS_POR_USUARIO, NOTAS_POR_FILME = carregar_matriz_usuario_item()

# Calculado uma única vez na subida do servidor: é sempre o mesmo usuário de
# exemplo, então recalcular a cada visita só desperdiçaria tempo de resposta.
FILEIRAS_RECOMENDADAS = [
    {
        "titulo": "Recomendados pra você",
        "filmes": recomendar_item_item(USUARIO_DEMO, NOTAS_POR_USUARIO, NOTAS_POR_FILME, FILMES_POR_ID),
    },
    {
        "titulo": "Quem tem gosto parecido com o seu curtiu",
        "filmes": recomendar_user_user(USUARIO_DEMO, NOTAS_POR_USUARIO, NOTAS_POR_FILME, FILMES_POR_ID),
    },
]


@app.get("/")
def home(request: Request):
    contexto = montar_home(FILMES, FILEIRAS_RECOMENDADAS)
    return templates.TemplateResponse(request, "home.html", contexto)


@app.get("/filmes")
def listagem(request: Request):
    return templates.TemplateResponse(request, "listagem.html", {
        "filmes": FILMES,
    })


@app.get("/filme/{movie_id}")
def detalhe(request: Request, movie_id: str):
    filme = buscar_filme(FILMES_POR_ID, movie_id)
    if not filme:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    return templates.TemplateResponse(request, "detalhe.html", {
        "filme": filme,
        "parecidos": filmes_parecidos(filme, FILMES),
    })
