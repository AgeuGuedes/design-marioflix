import numpy as np
import pandas as pd
import pytest

from src.recommenders.collaborative import FiltragemColaborativa


def _ratings(notas):
    """notas: {usuario: {filme: nota}} -> DataFrame userId, movieId, rating."""
    linhas = [(u, f, float(r)) for u, filmes in notas.items() for f, r in filmes.items()]
    return pd.DataFrame(linhas, columns=["userId", "movieId", "rating"])


@pytest.fixture
def modelo_usuarios():
    # A e B avaliam parecido; C é diferente.
    return FiltragemColaborativa(_ratings({
        1: {1: 5, 2: 3},
        2: {1: 5, 2: 3, 3: 4},
        3: {1: 1, 4: 5},
    }))


@pytest.fixture
def modelo_itens():
    return FiltragemColaborativa(_ratings({
        1: {1: 5, 2: 5},
        2: {1: 4, 2: 4, 3: 1},
        3: {1: 5},
    }))


def test_vizinhos_usuario_usa_cosseno_e_descarta_o_proprio_usuario(modelo_usuarios):
    vizinhos = modelo_usuarios.vizinhos_usuario(1, k=2)

    assert [uid for uid, _ in vizinhos] == [2, 3]
    assert vizinhos[0][1] == pytest.approx(34 / (34 * 50) ** 0.5)
    assert vizinhos[1][1] == pytest.approx(5 / (34 * 26) ** 0.5)


def test_media_do_usuario_ignora_filmes_nao_avaliados(modelo_usuarios):
    assert modelo_usuarios.medias_usuario[3] == pytest.approx(3.0)


def test_prever_nota_parte_da_media_e_soma_o_desvio_dos_vizinhos(modelo_usuarios):
    # Filme 3: só o usuário 2 viu, e deu 4 (a média dele) -> desvio 0 -> fica na média do usuário 1.
    assert modelo_usuarios.prever_nota_usuario(1, 3, k=2) == pytest.approx(4.0)


def test_prever_nota_e_limitada_ao_teto_da_escala(modelo_usuarios):
    # Filme 4: só o usuário 3 viu, com desvio +2 -> 4 + 2 = 6, limitado a 5.
    assert modelo_usuarios.prever_nota_usuario(1, 4, k=2) == 5.0


def test_prever_nota_de_filme_desconhecido_e_nan(modelo_usuarios):
    assert np.isnan(modelo_usuarios.prever_nota_usuario(1, 999, k=2))


def test_recomendar_usuario_ordena_pela_nota_prevista(modelo_usuarios):
    rec = modelo_usuarios.recomendar_usuario(1, n=10, k=2)

    assert rec.movieId.tolist() == [4, 3]
    assert rec.nota_prevista.tolist() == pytest.approx([5.0, 4.0])


def test_recomendar_usuario_nao_recomenda_filme_ja_visto():
    modelo = FiltragemColaborativa(_ratings({1: {1: 5}, 2: {1: 5, 2: 4}}))

    assert modelo.recomendar_usuario(1, k=1).movieId.tolist() == [2]


def test_vizinhos_filme_usa_o_publico_que_avaliou(modelo_itens):
    vizinhos = modelo_itens.vizinhos_filme(1, k=2)

    assert [mid for mid, _ in vizinhos] == [2, 3]
    assert vizinhos[0][1] == pytest.approx(41 / (66 * 41) ** 0.5)
    assert vizinhos[1][1] == pytest.approx(4 / 66 ** 0.5)


def test_vizinhos_de_filme_desconhecido_sao_vazios(modelo_itens):
    assert modelo_itens.vizinhos_filme(999) == []


def test_recomendar_itemitem_soma_a_similaridade_dos_favoritos(modelo_itens):
    rec = modelo_itens.recomendar_itemitem(3, k=2)

    # O usuário 3 só curtiu o filme 1 (nota 5); o filme 1, já visto, não volta.
    assert rec.movieId.tolist() == [2, 3]
    assert rec.score.tolist() == pytest.approx([41 / (66 * 41) ** 0.5, 4 / 66 ** 0.5])
    assert rec.n_favoritos.tolist() == [1, 1]


def test_recomendar_itemitem_ignora_filmes_que_nao_sao_favoritos():
    modelo = FiltragemColaborativa(_ratings({1: {1: 5, 2: 5}, 2: {1: 2}}))

    assert modelo.recomendar_itemitem(2, k=1).empty


def test_vizinhos_por_notas_acha_usuarios_parecidos_de_quem_nao_esta_na_matriz(modelo_usuarios):
    # Visitante com as mesmas notas do usuário 1: o próprio usuário 1 é o vizinho mais parecido.
    vizinhos = modelo_usuarios.vizinhos_por_notas({1: 5.0, 2: 3.0}, k=2)

    assert [uid for uid, _ in vizinhos] == [1, 2]
    assert vizinhos[0][1] == pytest.approx(1.0)
    assert vizinhos[1][1] == pytest.approx(34 / (34 * 50) ** 0.5)


def test_recomendar_usuario_por_notas_nao_recomenda_o_que_o_visitante_ja_avaliou(modelo_usuarios):
    rec = modelo_usuarios.recomendar_usuario_por_notas({1: 5.0, 2: 3.0}, k=2)

    assert rec.movieId.tolist() == [3]
    assert rec.nota_prevista.tolist() == pytest.approx([4.0])


def test_recomendar_usuario_por_notas_limita_a_nota_ao_teto_da_escala(modelo_usuarios):
    rec = modelo_usuarios.recomendar_usuario_por_notas({1: 5.0, 2: 3.0}, k=3)

    assert rec.movieId.tolist() == [4, 3]
    assert rec.nota_prevista.tolist() == pytest.approx([5.0, 4.0])


def test_recomendar_itemitem_por_notas_soma_a_similaridade_dos_favoritos(modelo_itens):
    rec = modelo_itens.recomendar_itemitem_por_notas({1: 5.0}, k=2)

    assert rec.movieId.tolist() == [2, 3]
    assert rec.score.tolist() == pytest.approx([41 / (66 * 41) ** 0.5, 4 / 66 ** 0.5])


def test_por_notas_ignora_filmes_que_nao_estao_na_matriz(modelo_usuarios, modelo_itens):
    assert modelo_usuarios.recomendar_usuario_por_notas({999: 5.0}).empty
    assert modelo_itens.recomendar_itemitem_por_notas({999: 5.0}).empty


def test_memoria_da_matriz_esparsa_conta_so_as_notas_que_existem(modelo_usuarios):
    densa, esparsa = modelo_usuarios.memoria_matrizes()

    # 7 notas de 8 bytes cada (float64).
    assert esparsa == pytest.approx(7 * 8 / 1024**2)
    assert densa > 0


def test_vizinhos_por_k_guarda_dist_idx_e_similaridade(modelo_usuarios):
    resultados = modelo_usuarios.vizinhos_por_k(1, ks=[1, 2])

    assert [r["k"] for r in resultados] == [1, 2]
    assert resultados[1]["similaridade"].shape == (1, 3)  # o próprio usuário + 2 vizinhos
    assert resultados[1]["similaridade"][0][0] == pytest.approx(1.0)
    assert resultados[1]["similaridade"][0][1] == pytest.approx(34 / (34 * 50) ** 0.5)


def test_comparar_abordagens_conta_filmes_em_comum(modelo_itens):
    user_user, item_item, em_comum = modelo_itens.comparar_abordagens(3, n=10, k=2)

    assert user_user.movieId.tolist() == [2, 3]
    assert item_item.movieId.tolist() == [2, 3]
    assert em_comum == 2


def test_titulo_aparece_nas_tabelas_quando_os_titulos_sao_informados():
    ratings = _ratings({1: {1: 5, 2: 5}, 2: {1: 4, 2: 4, 3: 1}, 3: {1: 5}})
    modelo = FiltragemColaborativa(ratings, titulos={1: "Filme A", 2: "Filme B", 3: "Filme C"})

    assert modelo.recomendar_itemitem(3, k=2).titulo.tolist() == ["Filme B", "Filme C"]
    assert "titulo" not in FiltragemColaborativa(ratings).recomendar_itemitem(3, k=2).columns
