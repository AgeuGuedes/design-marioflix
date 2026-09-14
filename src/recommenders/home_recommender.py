"""Seleção de filmes pra cada fileira da Home, a partir da nota/quantidade de Ratings."""
import random

LIMIT = 10
M_REFERENCIA_TOP10 = 20


def _media_global(filmes_avaliados):
    total_avaliacoes = sum(f["quantidade_avaliacoes"] for f in filmes_avaliados)
    soma_notas = sum(f["nota_media"] * f["quantidade_avaliacoes"] for f in filmes_avaliados)
    return soma_notas / total_avaliacoes if total_avaliacoes else 0


def _score_ponderado(filme, media_global, m):
    v = filme["quantidade_avaliacoes"]
    return (v / (v + m)) * filme["nota_media"] + (m / (v + m)) * media_global


def top10(filmes, limit=LIMIT):
    """Ranking pela média ponderada (fórmula IMDB): aproxima filmes com poucas
    avaliações da média global, em vez de simplesmente excluí-los."""
    elegiveis = [f for f in filmes if f["nota_media"] is not None and f["quantidade_avaliacoes"] > 0]
    media_global = _media_global(elegiveis)
    return sorted(
        elegiveis,
        key=lambda f: _score_ponderado(f, media_global, M_REFERENCIA_TOP10),
        reverse=True,
    )[:limit]


def top10_por_genero(filmes, genero, limit=LIMIT):
    """Baseline segmentado: mesmo ranking ponderado do top10(), restrito a um gênero."""
    elegiveis = [
        f for f in filmes
        if f["nota_media"] is not None and f["quantidade_avaliacoes"] > 0 and genero in f["genres_list"]
    ]
    media_global = _media_global(elegiveis)
    return sorted(
        elegiveis,
        key=lambda f: _score_ponderado(f, media_global, M_REFERENCIA_TOP10),
        reverse=True,
    )[:limit]


def mais_avaliados(filmes, limit=LIMIT):
    elegiveis = [f for f in filmes if f["quantidade_avaliacoes"] > 0]
    return sorted(elegiveis, key=lambda f: f["quantidade_avaliacoes"], reverse=True)[:limit]


def aleatorio(filmes, limit=LIMIT):
    return random.sample(filmes, min(limit, len(filmes)))
