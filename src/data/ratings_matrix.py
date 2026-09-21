"""Matriz usuário-item esparsa, a partir do ratings.csv do MovieLens.

Guardada como dois dicionários (não como matriz densa): notas_por_usuario
para o lado user-user, notas_por_filme (o "inverso") para o lado item-item.
"""
import csv
from pathlib import Path

RATINGS_CSV = Path(__file__).resolve().parent / "ml-latest-small" / "ratings.csv"


def carregar_matriz_usuario_item():
    notas_por_usuario = {}
    notas_por_filme = {}

    with open(RATINGS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            user_id = row["userId"]
            movie_id = row["movieId"]
            nota = float(row["rating"])

            notas_por_usuario.setdefault(user_id, {})[movie_id] = nota
            notas_por_filme.setdefault(movie_id, {})[user_id] = nota

    return notas_por_usuario, notas_por_filme
