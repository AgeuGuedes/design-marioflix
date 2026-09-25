from fastapi.testclient import TestClient

from src.api.main import FILEIRAS_PADRAO, FILMES, app

client = TestClient(app)


def test_home_ok():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "MARIOFLIX" in resp.text


def test_listagem_ok():
    resp = client.get("/filmes")
    assert resp.status_code == 200


def _visitante():
    """Um navegador novo: cada TestClient guarda os próprios cookies."""
    return TestClient(app)


def _ids_do_catalogo(quantidade):
    return [f["movieId"] for f in FILMES[:quantidade]]


def test_home_sem_notas_mostra_as_recomendacoes_padrao():
    home = _visitante().get("/").text

    assert "Recomendados pra você" in home
    assert "Quem tem gosto parecido com o seu curtiu" in home


def test_filme_avaliado_sai_das_recomendacoes_padrao():
    filme_id = FILEIRAS_PADRAO[0]["filmes"][0]["movieId"]
    visitante = _visitante()
    assert f'href="/filme/{filme_id}"' in visitante.get("/").text.split("Recomendados pra você")[1].split("</section>")[0]

    visitante.post(f"/avaliar/{filme_id}", data={"nota": "5"})
    recomendados = visitante.get("/").text.split("Recomendados pra você")[1].split("</section>")[0]

    assert f'href="/filme/{filme_id}"' not in recomendados


def test_avaliar_guarda_a_nota_no_cookie_e_volta_pro_filme():
    filme_id = _ids_do_catalogo(1)[0]
    visitante = _visitante()

    resp = visitante.post(f"/avaliar/{filme_id}", data={"nota": "4"}, follow_redirects=False)

    assert resp.status_code == 303
    assert resp.headers["location"] == f"/filme/{filme_id}"
    assert f"notas={filme_id}:4" in resp.headers["set-cookie"]
    assert "✓ Assistido" in visitante.get(f"/filme/{filme_id}").text


def test_avaliar_com_nota_zero_remove_a_avaliacao():
    filme_id = _ids_do_catalogo(1)[0]
    visitante = _visitante()
    visitante.post(f"/avaliar/{filme_id}", data={"nota": "4"})

    visitante.post(f"/avaliar/{filme_id}", data={"nota": "0"})

    assert "✓ Assistido" not in visitante.get(f"/filme/{filme_id}").text


def test_avaliar_filme_inexistente_404():
    assert _visitante().post("/avaliar/id-que-nao-existe", data={"nota": "5"}).status_code == 404


def test_avaliar_nota_invalida_422():
    filme_id = _ids_do_catalogo(1)[0]

    assert _visitante().post(f"/avaliar/{filme_id}", data={"nota": "9"}).status_code == 422


def test_home_recomenda_depois_de_avaliar_filmes_e_nao_repete_os_ja_vistos():
    vistos = _ids_do_catalogo(3)
    visitante = _visitante()
    for filme_id in vistos:
        visitante.post(f"/avaliar/{filme_id}", data={"nota": "5"})

    home = visitante.get("/").text
    recomendados = home.split("Recomendados pra você")[1].split("</section>")[0]

    assert "Recomendados pra você" in home
    assert all(f'href="/filme/{filme_id}"' not in recomendados for filme_id in vistos)


def test_cartaz_do_filme_avaliado_ganha_o_selo_assistido():
    avaliado, outro = _ids_do_catalogo(2)
    visitante = _visitante()
    assert "poster-visto" not in visitante.get("/filmes").text

    visitante.post(f"/avaliar/{avaliado}", data={"nota": "3"})
    listagem = visitante.get("/filmes").text

    assert listagem.count("poster-visto") == 1
    assert listagem.split("poster-visto")[0].rsplit(f'href="/filme/', 1)[1].startswith(f"{avaliado}\"")


def test_detalhe_existente_ok():
    primeiro_id = FILMES[0]["movieId"]
    resp = client.get(f"/filme/{primeiro_id}")
    assert resp.status_code == 200


def test_detalhe_inexistente_404():
    resp = client.get("/filme/id-que-nao-existe")
    assert resp.status_code == 404
