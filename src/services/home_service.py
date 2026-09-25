from src.data.loader import GENEROS_PT
from src.recommenders.home_recommender import aleatorio, mais_avaliados, top10, top10_por_genero
from src.services.perfil_service import MIN_NOTAS

DESTAQUES_TITULOS = ["Braveheart", "Pulp Fiction", "Star Wars: Episode IV", "Casino", "Heat"]
GENEROS_HOME = ["Sci-Fi", "Comedy", "Action"]
USUARIO_DEMO = 1442
LIMIT = 10


def montar_destaques(filmes):
    escolhidos = [
        f for f in (
            next((f for f in filmes if f["title"].startswith(titulo)), None)
            for titulo in DESTAQUES_TITULOS
        ) if f and f["backdrop_url"]
    ]
    return escolhidos or [f for f in filmes if f["backdrop_url"]][:5]


def filmes_do_catalogo(recomendacao, filmes_por_id, limit=LIMIT):
    """Do ranking do kNN, que cobre todos os filmes do MovieLens, mantém só os que estão no catálogo do site."""
    ids = (str(movie_id) for movie_id in recomendacao["movieId"])
    return [filmes_por_id[mid] for mid in ids if mid in filmes_por_id][:limit]


def fileiras_padrao(modelo, filmes_por_id):
    """Recomendações do usuário de exemplo, mostradas enquanto o visitante ainda tem poucas notas."""
    folga = LIMIT + MIN_NOTAS  # sobra pra repor filmes que o visitante já marcou como assistidos
    return [
        {
            "titulo": "Recomendados pra você",
            "filmes": filmes_do_catalogo(modelo.recomendar_itemitem(USUARIO_DEMO, n=None), filmes_por_id, folga),
        },
        {
            "titulo": "Quem tem gosto parecido com o seu curtiu",
            "filmes": filmes_do_catalogo(modelo.recomendar_usuario(USUARIO_DEMO, n=None), filmes_por_id, folga),
        },
    ]


def fileiras_recomendadas(modelo, notas, filmes_por_id, padrao):
    """Fileiras de recomendação pro visitante. Os filmes que ele já avaliou não aparecem.

    Com poucas notas ainda não dá pra personalizar: mostra as fileiras padrão (sem os filmes já vistos).
    """
    if len(notas) < MIN_NOTAS:
        return [
            {"titulo": f["titulo"], "filmes": [m for m in f["filmes"] if int(m["movieId"]) not in notas][:LIMIT]}
            for f in padrao
        ]

    return [
        {
            "titulo": "Recomendados pra você",
            "filmes": filmes_do_catalogo(modelo.recomendar_itemitem_por_notas(notas, n=None), filmes_por_id),
        },
        {
            "titulo": "Quem tem gosto parecido com o seu curtiu",
            "filmes": filmes_do_catalogo(modelo.recomendar_usuario_por_notas(notas, n=None), filmes_por_id),
        },
    ]


def montar_home(filmes, recomendadas=None):
    fileiras_genero = [
        {"titulo": f"Top 10 {GENEROS_PT.get(genero, genero)}", "filmes": top10_por_genero(filmes, genero)}
        for genero in GENEROS_HOME
    ]

    return {
        "destaques": montar_destaques(filmes),
        "fileiras": [
            {"titulo": "Top 10 mais bem avaliados", "filmes": top10(filmes)},
            {"titulo": "Mais avaliados pelo público", "filmes": mais_avaliados(filmes)},
            *[f for f in (recomendadas or []) if f["filmes"]],
            *[f for f in fileiras_genero if f["filmes"]],
            {"titulo": "Descubra algo novo", "filmes": aleatorio(filmes)},
        ],
    }
