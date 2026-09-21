"""Filtragem colaborativa item-item: vizinhos de filme pelo comportamento de quem avaliou.

Diferente do content_recommender (que usa gênero), aqui a similaridade vem só
das notas em comum entre dois filmes — cosseno cru sobre os co-avaliadores.
Ver aula_03_slides, páginas 32-38.
"""

MIN_CO_AVALIACOES = 5
NOTA_MINIMA_SEMENTE = 4.0
MAX_SEMENTES = 30
LIMIT = 10


def _cosseno_item(notas_filme_a, notas_filme_b):
    comuns = notas_filme_a.keys() & notas_filme_b.keys()
    if len(comuns) < MIN_CO_AVALIACOES:
        return None

    produto = sum(notas_filme_a[u] * notas_filme_b[u] for u in comuns)
    norma_a = sum(v * v for v in notas_filme_a.values()) ** 0.5
    norma_b = sum(v * v for v in notas_filme_b.values()) ** 0.5
    if norma_a == 0 or norma_b == 0:
        return None
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

    scores = {}
    for semente_id in sementes:
        notas_semente = notas_por_filme.get(semente_id)
        if not notas_semente:
            continue
        for candidato_id in filmes_por_id:
            if candidato_id in vistos or candidato_id == semente_id:
                continue
            notas_candidato = notas_por_filme.get(candidato_id)
            if not notas_candidato:
                continue
            sim = _cosseno_item(notas_semente, notas_candidato)
            if sim is not None and sim > 0:
                scores[candidato_id] = scores.get(candidato_id, 0.0) + sim

    ranking = sorted(scores.items(), key=lambda par: par[1], reverse=True)
    return [filmes_por_id[movie_id] for movie_id, _score in ranking[:limit]]
