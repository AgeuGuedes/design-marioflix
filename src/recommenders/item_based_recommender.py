"""Filtragem colaborativa item-item, seguindo a Parte 3 do notebook KNN_user_items (Aula 03).

Filmes vizinhos: cosseno bruto entre os vetores de notas recebidas (ausência = 0).
Para cada filme que o usuário curtiu (nota >= 4), somam-se as similaridades dos
seus k vizinhos; o resultado é um score de ranking, não uma nota prevista.
"""

K_VIZINHOS = 20
NOTA_MINIMA_SEMENTE = 4.0
LIMIT = 10


def _norma(notas):
    return sum(v * v for v in notas.values()) ** 0.5


def vizinhos_filme(movie_id, notas_por_usuario, notas_por_filme, normas, k=K_VIZINHOS):
    """Os k filmes mais parecidos como (movieId, similaridade), sem o próprio filme."""
    notas_alvo = notas_por_filme.get(movie_id)
    if not notas_alvo:
        return []

    # Produto interno com todos os outros filmes de uma só passada, pelo índice invertido.
    produtos = {}
    for user_id, nota in notas_alvo.items():
        for outro_id, nota_outro in notas_por_usuario[user_id].items():
            if outro_id != movie_id:
                produtos[outro_id] = produtos.get(outro_id, 0.0) + nota * nota_outro

    similares = [(outro_id, p / (normas[movie_id] * normas[outro_id])) for outro_id, p in produtos.items()]
    similares.sort(key=lambda par: par[1], reverse=True)
    return similares[:k]


def recomendar(user_id, notas_por_usuario, notas_por_filme, filmes_por_id, k=K_VIZINHOS, limit=LIMIT):
    notas_alvo = notas_por_usuario.get(user_id)
    if not notas_alvo:
        return []

    normas = {mid: _norma(notas) for mid, notas in notas_por_filme.items()}
    favoritos = [mid for mid, nota in notas_alvo.items() if nota >= NOTA_MINIMA_SEMENTE]

    score, n_favoritos = {}, {}
    for semente_id in favoritos:
        for candidato_id, sim in vizinhos_filme(semente_id, notas_por_usuario, notas_por_filme, normas, k):
            if candidato_id in notas_alvo or sim <= 0:
                continue
            score[candidato_id] = score.get(candidato_id, 0.0) + sim
            n_favoritos[candidato_id] = n_favoritos.get(candidato_id, 0) + 1

    ranking = sorted(
        (mid for mid in score if mid in filmes_por_id),
        key=lambda mid: (score[mid], n_favoritos[mid]),
        reverse=True,
    )
    return [filmes_por_id[mid] for mid in ranking[:limit]]
