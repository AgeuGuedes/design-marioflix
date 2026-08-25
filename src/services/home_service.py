from src.recommenders.home_recommender import aleatorio, mais_avaliados, top10

DESTAQUES_TITULOS = ["Braveheart", "Pulp Fiction", "Star Wars: Episode IV", "Casino", "Heat"]


def montar_destaques(filmes):
    escolhidos = [
        f for f in (
            next((f for f in filmes if f["title"].startswith(titulo)), None)
            for titulo in DESTAQUES_TITULOS
        ) if f and f["backdrop_url"]
    ]
    return escolhidos or [f for f in filmes if f["backdrop_url"]][:5]


def montar_home(filmes):
    return {
        "destaques": montar_destaques(filmes),
        "fileiras": [
            {"titulo": "Top 10 mais bem avaliados", "filmes": top10(filmes)},
            {"titulo": "Mais avaliados pelo público", "filmes": mais_avaliados(filmes)},
            {"titulo": "Descubra algo novo", "filmes": aleatorio(filmes)},
        ],
    }
