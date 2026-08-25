"""
Camada de dados: junta Filme + Atores/Diretor (TMDB) com Usuário + Ratings (MovieLens).

Schema:
    Filme --- Atores / Diretor      (filmes_completo.csv, via scraping do TMDB)
    Usuario --- Ratings --- Filme   (ml-latest-small/ratings.csv, MovieLens)
"""
import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
FILMES_CSV = DATA_DIR / "filmes_completo.csv"
RATINGS_CSV = DATA_DIR / "ml-latest-small" / "ratings.csv"

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w342"
BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/w1280"

GENEROS_PT = {
    "Action": "Ação",
    "Adventure": "Aventura",
    "Animation": "Animação",
    "Children": "Infantil",
    "Comedy": "Comédia",
    "Crime": "Crime",
    "Documentary": "Documentário",
    "Drama": "Drama",
    "Fantasy": "Fantasia",
    "Film-Noir": "Film-Noir",
    "Horror": "Terror",
    "IMAX": "IMAX",
    "Musical": "Musical",
    "Mystery": "Mistério",
    "Romance": "Romance",
    "Sci-Fi": "Ficção Científica",
    "Thriller": "Suspense",
    "War": "Guerra",
    "Western": "Faroeste",
    "(no genres listed)": "Sem gênero",
}


def traduzir_generos(genres: str) -> str:
    partes = [GENEROS_PT.get(g, g) for g in genres.split("|")]
    return " • ".join(partes)


def carregar_ratings():
    """Usuário -> Ratings -> Filme: agrega nota média e nº de avaliações por filme."""
    soma = {}
    contagem = {}

    with open(RATINGS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            movie_id = row["movieId"]
            nota = float(row["rating"])
            soma[movie_id] = soma.get(movie_id, 0.0) + nota
            contagem[movie_id] = contagem.get(movie_id, 0) + 1

    return {
        movie_id: {
            "nota_media": round(total / contagem[movie_id], 1),
            "quantidade_avaliacoes": contagem[movie_id],
        }
        for movie_id, total in soma.items()
    }


def carregar_filmes():
    ratings_por_filme = carregar_ratings()

    with open(FILMES_CSV, newline="", encoding="utf-8") as f:
        filmes = list(csv.DictReader(f))

    for filme in filmes:
        filme["hue"] = abs(hash(filme["title"])) % 360
        filme["genres_list"] = filme["genres"].split("|")
        filme["genres_pt"] = traduzir_generos(filme["genres"])
        filme["poster_url"] = POSTER_BASE_URL + filme["poster"] if filme.get("poster") else None
        filme["backdrop_url"] = BACKDROP_BASE_URL + filme["backdrop"] if filme.get("backdrop") else None

        stats = ratings_por_filme.get(filme["movieId"], {"nota_media": None, "quantidade_avaliacoes": 0})
        filme["nota_media"] = stats["nota_media"]
        filme["quantidade_avaliacoes"] = stats["quantidade_avaliacoes"]

    return filmes
