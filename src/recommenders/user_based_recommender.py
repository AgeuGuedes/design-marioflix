"""Filtragem colaborativa user-user: vizinhos por similaridade de cosseno centralizada.

Centraliza pela média de cada usuário antes de comparar (cosseno cru engana,
já que todas as notas são positivas). Ver aula_03_slides, páginas 15-20 e 26-28.
"""

MIN_CO_AVALIACOES = 5
K_VIZINHOS = 20
LIMIT = 10


def _media(notas):
    return sum(notas.values()) / len(notas)


def _cosseno_centralizado(notas_a, media_a, notas_b, media_b):
    comuns = notas_a.keys() & notas_b.keys()
    if len(comuns) < MIN_CO_AVALIACOES:
        return None

    produto = soma_a2 = soma_b2 = 0.0
    for filme in comuns:
        da = notas_a[filme] - media_a
        db = notas_b[filme] - media_b
        produto += da * db
        soma_a2 += da * da
        soma_b2 += db * db

    if soma_a2 == 0 or soma_b2 == 0:
        return None
    return produto / (soma_a2 ** 0.5 * soma_b2 ** 0.5)


def vizinhos(user_id, notas_por_usuario, medias, k=K_VIZINHOS):
    notas_alvo = notas_por_usuario.get(user_id)
    if not notas_alvo:
        return []
    media_alvo = medias[user_id]

    similares = []
    for outro_id, notas_outro in notas_por_usuario.items():
        if outro_id == user_id:
            continue
        sim = _cosseno_centralizado(notas_alvo, media_alvo, notas_outro, medias[outro_id])
        if sim is not None and sim > 0:
            similares.append((outro_id, sim))

    similares.sort(key=lambda par: par[1], reverse=True)
    return similares[:k]


def recomendar(user_id, notas_por_usuario, filmes_por_id, limit=LIMIT):
    """Prevê a nota de cada filme não visto (fórmula da página 26) e ordena por ela."""
    notas_alvo = notas_por_usuario.get(user_id)
    if not notas_alvo:
        return []

    medias = {uid: _media(notas) for uid, notas in notas_por_usuario.items()}
    media_alvo = medias[user_id]
    vistos = notas_alvo.keys()

    vizinhos_similares = vizinhos(user_id, notas_por_usuario, medias)
    if not vizinhos_similares:
        return []

    predicoes = {}
    for movie_id in filmes_por_id:
        if movie_id in vistos:
            continue

        numerador = denominador = 0.0
        for vizinho_id, sim in vizinhos_similares:
            notas_vizinho = notas_por_usuario[vizinho_id]
            if movie_id not in notas_vizinho:
                continue
            desvio = notas_vizinho[movie_id] - medias[vizinho_id]
            numerador += sim * desvio
            denominador += abs(sim)

        if denominador > 0:
            predicao = media_alvo + numerador / denominador
            predicoes[movie_id] = max(1.0, min(5.0, predicao))

    ranking = sorted(predicoes.items(), key=lambda par: par[1], reverse=True)
    return [filmes_por_id[movie_id] for movie_id, _nota in ranking[:limit]]
