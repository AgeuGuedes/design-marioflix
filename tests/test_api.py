from fastapi.testclient import TestClient

from src.api.main import FILMES, app

client = TestClient(app)


def test_home_ok():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "MARIOFLIX" in resp.text


def test_listagem_ok():
    resp = client.get("/filmes")
    assert resp.status_code == 200


def test_detalhe_existente_ok():
    primeiro_id = FILMES[0]["movieId"]
    resp = client.get(f"/filme/{primeiro_id}")
    assert resp.status_code == 200


def test_detalhe_inexistente_404():
    resp = client.get("/filme/id-que-nao-existe")
    assert resp.status_code == 404
