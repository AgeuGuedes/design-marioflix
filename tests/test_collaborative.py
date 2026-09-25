import pytest

from src.recommenders import item_based_recommender as item_item
from src.recommenders import user_based_recommender as user_user


def _inverter(notas_por_usuario):
    notas_por_filme = {}
    for user_id, notas in notas_por_usuario.items():
        for movie_id, nota in notas.items():
            notas_por_filme.setdefault(movie_id, {})[user_id] = nota
    return notas_por_filme


def _catalogo(*ids):
    return {i: {"movieId": i, "title": f"Filme {i}"} for i in ids}


def test_vizinhos_usuario_usa_cosseno_bruto():
    notas = {"A": {"1": 5, "2": 3}, "B": {"1": 5, "2": 3, "3": 4}, "C": {"1": 1, "4": 5}}
    normas = {uid: user_user._norma(n) for uid, n in notas.items()}

    vizinhos = user_user.vizinhos_usuario("A", notas, _inverter(notas), normas, k=2)

    assert [uid for uid, _ in vizinhos] == ["B", "C"]
    assert vizinhos[0][1] == pytest.approx(34 / (34 * 50) ** 0.5)
    assert vizinhos[1][1] == pytest.approx(5 / (34 * 26) ** 0.5)


def test_user_user_preve_nota_e_limita_ao_teto_da_escala():
    notas = {"A": {"1": 5, "2": 3}, "B": {"1": 5, "2": 3, "3": 4}, "C": {"1": 1, "4": 5}}

    recomendados = user_user.recomendar("A", notas, _inverter(notas), _catalogo("1", "2", "3", "4"), k=2)

    # Filme 4: 4 + (0,168 * 2) / 0,168 = 6 -> limitado a 5. Filme 3: vizinho B no próprio padrão -> 4.
    assert [f["movieId"] for f in recomendados] == ["4", "3"]


def test_user_user_nao_recomenda_filme_ja_visto():
    notas = {"A": {"1": 5}, "B": {"1": 5, "2": 4}}

    recomendados = user_user.recomendar("A", notas, _inverter(notas), _catalogo("1", "2"))

    assert [f["movieId"] for f in recomendados] == ["2"]


def test_item_item_soma_similaridade_dos_favoritos():
    notas = {"X": {"1": 5, "2": 5}, "Y": {"1": 4, "2": 4, "3": 1}, "T": {"1": 5}}

    recomendados = item_item.recomendar("T", notas, _inverter(notas), _catalogo("1", "2", "3"))

    # Filme 2: cos = 41 / sqrt(66 * 41) = 0,788; filme 3: cos = 4 / sqrt(66) = 0,492; o filme 1 já foi visto.
    assert [f["movieId"] for f in recomendados] == ["2", "3"]


def test_item_item_ignora_filmes_que_nao_sao_favoritos():
    notas = {"X": {"1": 5, "2": 5}, "T": {"1": 2}}

    assert item_item.recomendar("T", notas, _inverter(notas), _catalogo("1", "2")) == []


def test_usuario_desconhecido_nao_recebe_recomendacao():
    notas = {"A": {"1": 5}}

    assert user_user.recomendar("Z", notas, _inverter(notas), _catalogo("1")) == []
    assert item_item.recomendar("Z", notas, _inverter(notas), _catalogo("1")) == []
