"""
Script de scrap: completa os filmes do MovieLens (movies.csv + links.csv)
com diretor e elenco, buscando na API do TMDB pelo tmdbId de cada filme.

Uso:
    setx TMDB_API_KEY "sua_chave_aqui"      (Windows, uma vez só)
    python scrape_tmdb.py [limite]

    Ex: python scrape_tmdb.py 20   -> processa só 20 filmes (teste)
        python scrape_tmdb.py      -> processa todos os que faltam

Pode ser interrompido (Ctrl+C) e rodado de novo: ele pula os filmes
que já estão no arquivo de saída.
"""
import csv
import os
import sys
import time
import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API_KEY = os.environ.get("TMDB_API_KEY")
if not API_KEY:
    sys.exit("Defina a variável de ambiente TMDB_API_KEY antes de rodar.")

BASE_URL = "https://api.themoviedb.org/3"
INPUT_MOVIES = "ml-latest-small/movies.csv"
INPUT_LINKS = "ml-latest-small/links.csv"
OUTPUT_FILE = "filmes_completo.csv"
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else None


def load_links():
    links = {}
    with open(INPUT_LINKS, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["tmdbId"]:
                links[row["movieId"]] = row["tmdbId"]
    return links


def load_movies():
    with open(INPUT_MOVIES, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def already_done():
    if not os.path.exists(OUTPUT_FILE):
        return set()
    with open(OUTPUT_FILE, newline="", encoding="utf-8") as f:
        return {row["movieId"] for row in csv.DictReader(f)}


def fetch_details(tmdb_id):
    resp = requests.get(
        f"{BASE_URL}/movie/{tmdb_id}",
        params={"api_key": API_KEY, "append_to_response": "credits"},
        timeout=10,
    )
    if resp.status_code != 200:
        return None, None, None
    data = resp.json()
    credits = data.get("credits", {})
    diretores = [c["name"] for c in credits.get("crew", []) if c.get("job") == "Director"]
    atores = [c["name"] for c in credits.get("cast", [])[:5]]
    poster = data.get("poster_path") or ""
    backdrop = data.get("backdrop_path") or ""
    return "; ".join(diretores), ", ".join(atores), poster, backdrop


def main():
    links = load_links()
    movies = load_movies()
    done = already_done()
    file_exists = os.path.exists(OUTPUT_FILE)

    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        if not file_exists:
            writer.writerow(["movieId", "title", "genres", "diretor", "atores", "poster", "backdrop"])

        count = 0
        for movie in movies:
            movie_id = movie["movieId"]
            if movie_id in done:
                continue

            tmdb_id = links.get(movie_id)
            if not tmdb_id:
                writer.writerow([movie_id, movie["title"], movie["genres"], "", "", "", ""])
                continue

            diretor, atores, poster, backdrop = fetch_details(tmdb_id)
            writer.writerow([movie_id, movie["title"], movie["genres"], diretor or "", atores or "", poster or "", backdrop or ""])
            out.flush()

            count += 1
            print(f"[{count}] {movie['title']} -> diretor={diretor}")
            time.sleep(0.25)

            if LIMIT and count >= LIMIT:
                print(f"\nLimite de {LIMIT} filmes atingido. Rode de novo para continuar de onde parou.")
                break


if __name__ == "__main__":
    main()
