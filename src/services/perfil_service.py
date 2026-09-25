"""Notas que o visitante deu aos filmes. Não há login: elas ficam num cookie no navegador dele."""

MIN_NOTAS = 3  # com menos notas que isso ainda não dá pra recomendar
MAX_NOTAS = 200


def ler_notas(cookie):
    """Cookie no formato "1:5_2:4" (movieId:nota) -> {movieId: nota}. O que estiver mal formado é ignorado."""
    notas = {}
    for par in (cookie or "").split("_"):
        movie_id, _, nota = par.partition(":")
        if movie_id.isdigit() and nota in ("1", "2", "3", "4", "5"):
            notas[int(movie_id)] = float(nota)
    return dict(list(notas.items())[:MAX_NOTAS])


def guardar_notas(notas):
    return "_".join(f"{movie_id}:{int(nota)}" for movie_id, nota in notas.items())
