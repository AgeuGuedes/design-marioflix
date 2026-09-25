"""Leitura do MovieLens 1M: as avaliações (pra montar a matriz usuário-item) e os títulos dos filmes."""
from pathlib import Path

import pandas as pd

ML_1M_DIR = Path(__file__).resolve().parent / "ml-1m"


def carregar_ratings_1m():
    """DataFrame com userId, movieId e rating (1.000.209 avaliações)."""
    # O arquivo separa os campos com "::". Lendo com ":" sobram colunas vazias, que ficam de fora.
    ratings = pd.read_csv(ML_1M_DIR / "ratings.dat", sep=":", header=None, usecols=[0, 2, 4],
                          names=["userId", "movieId", "rating"])
    return ratings.astype({"rating": float})


def carregar_titulos_1m():
    """Dicionário movieId -> título."""
    titulos = {}
    with open(ML_1M_DIR / "movies.dat", encoding="latin-1") as f:
        for linha in f:
            movie_id, titulo, _generos = linha.strip().split("::")
            titulos[int(movie_id)] = titulo
    return titulos
