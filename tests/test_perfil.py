from src.services.perfil_service import MAX_NOTAS, guardar_notas, ler_notas


def test_ler_notas_le_o_formato_do_cookie():
    assert ler_notas("1:5_2:4") == {1: 5.0, 2: 4.0}


def test_ler_notas_sem_cookie_devolve_vazio():
    assert ler_notas(None) == {}
    assert ler_notas("") == {}


def test_ler_notas_ignora_o_que_esta_mal_formado():
    assert ler_notas("1:5_abc_2:9_x:3_3:0_4:4") == {1: 5.0, 4: 4.0}


def test_ler_notas_limita_a_quantidade_de_filmes():
    cookie = "_".join(f"{i}:3" for i in range(1, MAX_NOTAS + 50))

    assert len(ler_notas(cookie)) == MAX_NOTAS


def test_guardar_notas_e_o_inverso_de_ler_notas():
    assert guardar_notas({1: 5.0, 2: 4.0}) == "1:5_2:4"
    assert ler_notas(guardar_notas({7: 3.0, 9: 1.0})) == {7: 3.0, 9: 1.0}
