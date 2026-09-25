"""Filtragem colaborativa user-user, seguindo a Parte 2 do notebook KNN_user_items (Aula 03).

Vizinhos: cosseno bruto entre os vetores de notas dos usuários (ausência = 0).
Nota prevista: média do usuário + desvio ponderado dos vizinhos, limitada a [0,5; 5].
"""

K_VIZINHOS = 20
NOTA_MIN = 0.5
NOTA_MAX = 5.0
LIMIT = 10


def _media(notas):
    return sum(notas.values()) / len(notas)


def _norma(notas):
    return sum(v * v for v in notas.values()) ** 0.5


def vizinhos_usuario(user_id, notas_por_usuario, notas_por_filme, normas, k=K_VIZINHOS):
    """Os k usuários mais parecidos como (userId, similaridade), sem o próprio usuário."""
    notas_alvo = notas_por_usuario.get(user_id)
    if not notas_alvo:
        return []

    # Produto interno com todos os outros usuários de uma só passada, pelo índice invertido.
    produtos = {}
    for movie_id, nota in notas_alvo.items():
        for outro_id, nota_outro in notas_por_filme[movie_id].items():
            if outro_id != user_id:
                produtos[outro_id] = produtos.get(outro_id, 0.0) + nota * nota_outro

    similares = [(outro_id, p / (normas[user_id] * normas[outro_id])) for outro_id, p in produtos.items()]
    similares.sort(key=lambda par: par[1], reverse=True)
    return similares[:k]


def recomendar(user_id, notas_por_usuario, notas_por_filme, filmes_por_id, k=K_VIZINHOS, limit=LIMIT):
    """Prevê a nota de todo filme visto pelos vizinhos e não pelo usuário; devolve o Top-N do catálogo."""
    notas_alvo = notas_por_usuario.get(user_id)
    if not notas_alvo:
        return []

    medias = {uid: _media(notas) for uid, notas in notas_por_usuario.items()}
    normas = {uid: _norma(notas) for uid, notas in notas_por_usuario.items()}

    numerador, denominador = {}, {}
    for vizinho_id, sim in vizinhos_usuario(user_id, notas_por_usuario, notas_por_filme, normas, k):
        for movie_id, nota in notas_por_usuario[vizinho_id].items():
            if movie_id in notas_alvo:
                continue
            numerador[movie_id] = numerador.get(movie_id, 0.0) + sim * (nota - medias[vizinho_id])
            denominador[movie_id] = denominador.get(movie_id, 0.0) + abs(sim)

    predicoes = []
    for movie_id, num in numerador.items():
        if denominador[movie_id] == 0 or movie_id not in filmes_por_id:
            continue
        predicao = medias[user_id] + num / denominador[movie_id]
        predicoes.append((movie_id, max(NOTA_MIN, min(NOTA_MAX, predicao)), denominador[movie_id]))

    # Muitos filmes empatam no teto da escala: o peso dos vizinhos (suporte) desempata.
    predicoes.sort(key=lambda p: (p[1], p[2]), reverse=True)
    return [filmes_por_id[movie_id] for movie_id, _nota, _suporte in predicoes[:limit]]
