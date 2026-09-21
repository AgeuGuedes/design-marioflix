"""Matriz usuário-item esparsa, a partir do MovieLens 1M (ratings.dat).

Guardada como dois dicionários (não como matriz densa): notas_por_usuario
para o lado user-user, notas_por_filme (o "inverso") para o lado item-item.

O MovieLens 1M usa os mesmos movieId do ml-latest-small (catálogo enriquecido
com pôster/elenco), então dá pra recomendar direto sobre o mesmo catálogo.
"""
from pathlib import Path

RATINGS_DAT = Path(__file__).resolve().parent / "ml-1m" / "ratings.dat"


def carregar_matriz_usuario_item():
    notas_por_usuario = {}
    notas_por_filme = {}

    with open(RATINGS_DAT, encoding="latin-1") as f:
        for linha in f:
            user_id, movie_id, rating, _timestamp = linha.strip().split("::")
            nota = float(rating)

            notas_por_usuario.setdefault(user_id, {})[movie_id] = nota
            notas_por_filme.setdefault(movie_id, {})[user_id] = nota

    return notas_por_usuario, notas_por_filme
