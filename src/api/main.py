from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.data.loader import carregar_filmes
from src.recommenders.content_recommender import filmes_parecidos
from src.services.catalog_service import buscar_filme
from src.services.home_service import montar_home

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="MarioFlix")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "template")

FILMES = carregar_filmes()
FILMES_POR_ID = {f["movieId"]: f for f in FILMES}


@app.get("/")
def home(request: Request):
    contexto = montar_home(FILMES)
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
