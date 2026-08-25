"""Seleção de filmes pra cada fileira da Home, a partir da nota/quantidade de Ratings."""
import random

LIMIT = 10
MIN_AVALIACOES_TOP10 = 20


def top10(filmes, limit=LIMIT):
    elegiveis = [
        f for f in filmes
        if f["nota_media"] is not None and f["quantidade_avaliacoes"] >= MIN_AVALIACOES_TOP10
    ]
    return sorted(elegiveis, key=lambda f: f["nota_media"], reverse=True)[:limit]


def mais_avaliados(filmes, limit=LIMIT):
    elegiveis = [f for f in filmes if f["quantidade_avaliacoes"] > 0]
    return sorted(elegiveis, key=lambda f: f["quantidade_avaliacoes"], reverse=True)[:limit]


def aleatorio(filmes, limit=LIMIT):
    return random.sample(filmes, min(limit, len(filmes)))
