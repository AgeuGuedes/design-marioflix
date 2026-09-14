"""Recomendação baseada em conteúdo: vetor multi-hot de gêneros + similaridade de cosseno."""
import math

LIMIT = 10


def _vocabulario_generos(filmes):
    return sorted({genero for f in filmes for genero in f["genres_list"]})


def _vetor_generos(filme, vocabulario):
    generos_do_filme = set(filme["genres_list"])
    return [1 if genero in generos_do_filme else 0 for genero in vocabulario]


def _cosseno(a, b):
    produto = sum(x * y for x, y in zip(a, b))
    norma_a = math.sqrt(sum(x * x for x in a))
    norma_b = math.sqrt(sum(y * y for y in b))
    if norma_a == 0 or norma_b == 0:
        return 0
    return produto / (norma_a * norma_b)


def filmes_parecidos(filme, filmes, limit=LIMIT):
    vocabulario = _vocabulario_generos(filmes)
    vetor_base = _vetor_generos(filme, vocabulario)

    pontuados = [
        (candidato, _cosseno(vetor_base, _vetor_generos(candidato, vocabulario)))
        for candidato in filmes
        if candidato["movieId"] != filme["movieId"]
    ]
    pontuados = [par for par in pontuados if par[1] > 0]
    pontuados.sort(key=lambda par: par[1], reverse=True)
    return [candidato for candidato, _score in pontuados[:limit]]
