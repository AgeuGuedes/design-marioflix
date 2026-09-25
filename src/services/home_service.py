from src.data.loader import GENEROS_PT
from src.recommenders.home_recommender import aleatorio, mais_avaliados, top10, top10_por_genero

DESTAQUES_TITULOS = ["Braveheart", "Pulp Fiction", "Star Wars: Episode IV", "Casino", "Heat"]
GENEROS_HOME = ["Sci-Fi", "Comedy", "Action"]
USUARIO_DEMO = "1442"


def montar_destaques(filmes):
    escolhidos = [
        f for f in (
            next((f for f in filmes if f["title"].startswith(titulo)), None)
            for titulo in DESTAQUES_TITULOS
        ) if f and f["backdrop_url"]
    ]
    return escolhidos or [f for f in filmes if f["backdrop_url"]][:5]


def montar_home(filmes, fileiras_recomendadas=None):
    fileiras_genero = [
        {"titulo": f"Top 10 {GENEROS_PT.get(genero, genero)}", "filmes": top10_por_genero(filmes, genero)}
        for genero in GENEROS_HOME
    ]

    return {
        "destaques": montar_destaques(filmes),
        "fileiras": [
            {"titulo": "Top 10 mais bem avaliados", "filmes": top10(filmes)},
            {"titulo": "Mais avaliados pelo público", "filmes": mais_avaliados(filmes)},
            *[f for f in (fileiras_recomendadas or []) if f["filmes"]],
            *[f for f in fileiras_genero if f["filmes"]],
            {"titulo": "Descubra algo novo", "filmes": aleatorio(filmes)},
        ],
    }
