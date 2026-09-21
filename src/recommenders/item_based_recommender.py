"""Filtragem colaborativa item-item: vizinhos de filme pelo comportamento de quem avaliou.

Diferente do content_recommender (que usa gênero), aqui a similaridade vem só
das notas em comum entre dois filmes — cosseno cru sobre os co-avaliadores.
Ver aula_03_slides, páginas 32-38.
"""

MIN_CO_AVALIACOES = 5
NOTA_MINIMA_SEMENTE = 4.0
MAX_SEMENTES = 30
LIMIT = 10


def _norma(notas):
    return sum(v * v for v in notas.values()) ** 0.5


def _cosseno_item(notas_filme_a, notas_filme_b, norma_a, norma_b):
    if norma_a == 0 or norma_b == 0:
        return None
    comuns = notas_filme_a.keys() & notas_filme_b.keys()
    if len(comuns) < MIN_CO_AVALIACOES:
        return None
    produto = sum(notas_filme_a[u] * notas_filme_b[u] for u in comuns)
    return produto / (norma_a * norma_b)


def recomendar(user_id, notas_por_usuario, notas_por_filme, filmes_por_id, limit=LIMIT):
    notas_alvo = notas_por_usuario.get(user_id)
    if not notas_alvo:
        return []

    sementes = sorted(
        (mid for mid, nota in notas_alvo.items() if nota >= NOTA_MINIMA_SEMENTE),
        key=lambda mid: notas_alvo[mid],
        reverse=True,
    )[:MAX_SEMENTES]
    vistos = notas_alvo.keys()

    # Norma de cada filme calculada uma única vez (evita refazer a conta pra
    # cada semente — era o principal gargalo com 1M de avaliações).
    normas = {
        movie_id: _norma(notas_por_filme[movie_id])
        for movie_id in {*filmes_por_id, *sementes}
        if movie_id in notas_por_filme
    }

    scores = {}
    for semente_id in sementes:
        notas_semente = notas_por_filme.get(semente_id)
        norma_semente = normas.get(semente_id)
        if not notas_semente or not norma_semente:
            continue
        for candidato_id in filmes_por_id:
            if candidato_id in vistos or candidato_id == semente_id:
                continue
            notas_candidato = notas_por_filme.get(candidato_id)
            norma_candidato = normas.get(candidato_id)
            if not notas_candidato or not norma_candidato:
                continue
            sim = _cosseno_item(notas_semente, notas_candidato, norma_semente, norma_candidato)
            if sim is not None and sim > 0:
                scores[candidato_id] = scores.get(candidato_id, 0.0) + sim

    ranking = sorted(scores.items(), key=lambda par: par[1], reverse=True)
    return [filmes_por_id[movie_id] for movie_id, _score in ranking[:limit]]
