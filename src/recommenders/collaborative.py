"""Filtragem colaborativa (Aula 03): recomendação user-user e item-item com kNN.

Segue o notebook KNN_user_items. As linhas da matriz são usuários e as colunas são filmes;
o kNN usa cosseno com algorithm="brute" (a matriz é esparsa e tem muitas dimensões).
"""
import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.neighbors import NearestNeighbors

K_VIZINHOS = 20
K_LISTA = [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31]
NOTA_MIN = 0.5
NOTA_MAX = 5.0
NOTA_MIN_FAVORITO = 4.0


class FiltragemColaborativa:
    def __init__(self, ratings, titulos=None):
        self.ratings = ratings
        self.titulos = titulos or {}  # movieId -> título (opcional, só pra mostrar nas tabelas)

        # Matriz usuário-item: densa (com zeros) só pra montar a esparsa e consultar notas.
        self.matriz_densa = ratings.pivot(index="userId", columns="movieId", values="rating").fillna(0)
        self.matriz_esparsa = sp.csr_matrix(self.matriz_densa.values)
        # Transposta: linhas viram filmes e colunas viram usuários (usada no item-item).
        self.matriz_itens = self.matriz_esparsa.T.tocsr()

        self.knn_usuarios = NearestNeighbors(metric="cosine", algorithm="brute").fit(self.matriz_esparsa)
        self.knn_itens = NearestNeighbors(metric="cosine", algorithm="brute").fit(self.matriz_itens)

        # Posição na matriz <-> id.
        self.user_ids = self.matriz_densa.index.to_numpy()
        self.movie_ids = self.matriz_densa.columns.to_numpy()
        self.pos_filme = {int(mid): i for i, mid in enumerate(self.movie_ids)}

        # Média de cada usuário só sobre os filmes que ele avaliou (os zeros não entram).
        self.medias_usuario = ratings.groupby("userId")["rating"].mean()

    def memoria_matrizes(self):
        """Memória usada pela matriz densa e pela esparsa, em MB."""
        densa = self.matriz_densa.memory_usage().sum() / 1024**2
        esparsa = self.matriz_esparsa.data.nbytes / 1024**2
        return densa, esparsa

    def _com_titulo(self, rec):
        if self.titulos:
            rec["titulo"] = rec["movieId"].map(self.titulos)
        return rec

    # ---------- user-user ----------

    def vizinhos_por_k(self, user_id, ks=K_LISTA):
        """Os vizinhos do usuário para cada valor de k: lista de dicionários com k, dist, idx e similaridade."""
        pos = self.matriz_densa.index.get_loc(user_id)

        results = []
        for k in ks:
            dist, idx = self.knn_usuarios.kneighbors(self.matriz_esparsa[pos], n_neighbors=k + 1)
            results.append({"k": k, "dist": dist, "idx": idx, "similaridade": 1 - dist})
        return results

    def vizinhos_usuario(self, user_id, k=K_VIZINHOS):
        """Os k usuários mais parecidos, como (userId, similaridade)."""
        pos = self.matriz_densa.index.get_loc(user_id)
        dist, idx = self.knn_usuarios.kneighbors(self.matriz_esparsa[pos], n_neighbors=k + 1)

        viz = []
        for d, i in zip(dist[0], idx[0]):
            vid = int(self.user_ids[i])
            if vid == user_id:  # o próprio usuário sempre aparece, com similaridade 1
                continue
            viz.append((vid, 1 - d))  # similaridade = 1 - distância
        return viz[:k]

    def prever_nota_usuario(self, user_id, movie_id, k=K_VIZINHOS):
        """Nota que o usuário daria ao filme: a média dele mais o desvio dos vizinhos, ponderado pela similaridade."""
        if movie_id not in self.matriz_densa.columns:
            return np.nan

        num = den = 0.0
        for vid, sim in self.vizinhos_usuario(user_id, k=k):
            nota = self.matriz_densa.at[vid, movie_id]
            if nota == 0:  # o vizinho não avaliou este filme
                continue
            num += sim * (nota - self.medias_usuario[vid])
            den += abs(sim)

        if den == 0:  # nenhum vizinho viu o filme
            return self.medias_usuario[user_id]

        pred = self.medias_usuario[user_id] + num / den
        return float(np.clip(pred, NOTA_MIN, NOTA_MAX))

    def vizinhos_por_notas(self, notas, k=K_VIZINHOS):
        """Os k usuários mais parecidos com quem deu essas notas ({movieId: nota}), mesmo fora da matriz."""
        vetor = np.zeros((1, self.matriz_esparsa.shape[1]))
        for movie_id, nota in notas.items():
            if movie_id in self.pos_filme:
                vetor[0, self.pos_filme[movie_id]] = nota

        if not vetor.any():  # nenhum dos filmes está na matriz
            return []

        dist, idx = self.knn_usuarios.kneighbors(vetor, n_neighbors=k)
        return [(int(self.user_ids[i]), 1 - d) for d, i in zip(dist[0], idx[0])]

    def recomendar_usuario(self, user_id, n=10, k=K_VIZINHOS):
        """Top-n de filmes não vistos, ordenados pela nota prevista (n=None devolve todos)."""
        vistos = set(self.matriz_densa.columns[self.matriz_densa.loc[user_id] > 0])
        vizinhos = self.vizinhos_usuario(user_id, k=k)
        return self._prever_top_n(vizinhos, self.medias_usuario[user_id], vistos, n)

    def recomendar_usuario_por_notas(self, notas, n=10, k=K_VIZINHOS):
        """Como recomendar_usuario, mas pra quem só tem as notas ({movieId: nota}), como um visitante do site."""
        media = sum(notas.values()) / len(notas) if notas else 0.0
        return self._prever_top_n(self.vizinhos_por_notas(notas, k), media, set(notas), n)

    def _prever_top_n(self, vizinhos, media_usuario, vistos, n):
        num, den = {}, {}
        for vid, sim in vizinhos:
            linha = self.matriz_densa.loc[vid]
            for movie_id, nota in linha[linha > 0].items():
                if movie_id in vistos:
                    continue
                num[movie_id] = num.get(movie_id, 0.0) + sim * (nota - self.medias_usuario[vid])
                den[movie_id] = den.get(movie_id, 0.0) + abs(sim)

        linhas = []
        for movie_id in num:
            if den[movie_id] == 0:
                continue
            pred = media_usuario + num[movie_id] / den[movie_id]
            linhas.append((movie_id, float(np.clip(pred, NOTA_MIN, NOTA_MAX))))

        rec = pd.DataFrame(linhas, columns=["movieId", "nota_prevista"])
        rec = rec.sort_values("nota_prevista", ascending=False)
        return self._com_titulo((rec if n is None else rec.head(n)).reset_index(drop=True))

    # ---------- item-item ----------

    def vizinhos_filme(self, movie_id, k=K_VIZINHOS):
        """Os k filmes mais parecidos (recebem notas parecidas dos mesmos usuários), como (movieId, similaridade)."""
        if movie_id not in self.pos_filme:
            return []

        dist, idx = self.knn_itens.kneighbors(self.matriz_itens[self.pos_filme[movie_id]], n_neighbors=k + 1)

        viz = []
        for d, i in zip(dist[0], idx[0]):
            mid = int(self.movie_ids[i])
            if mid == movie_id:
                continue
            viz.append((mid, 1 - d))
        return viz[:k]

    def recomendar_itemitem(self, user_id, n=10, k=K_VIZINHOS, nota_min=NOTA_MIN_FAVORITO):
        """Top-n de filmes não vistos, pelo score: soma das similaridades com os filmes que o usuário curtiu."""
        hist = self.ratings[self.ratings.userId == user_id]
        return self.recomendar_itemitem_por_notas(dict(zip(hist.movieId, hist.rating)), n, k, nota_min)

    def recomendar_itemitem_por_notas(self, notas, n=10, k=K_VIZINHOS, nota_min=NOTA_MIN_FAVORITO):
        """Como recomendar_itemitem, mas pra quem só tem as notas ({movieId: nota}), como um visitante do site."""
        gostou = [mid for mid, nota in notas.items() if nota >= nota_min]
        vistos = set(notas)

        score, sementes = {}, {}
        for mid in gostou:
            for cand, sim in self.vizinhos_filme(mid, k=k):
                if cand in vistos or sim <= 0:
                    continue
                score[cand] = score.get(cand, 0.0) + sim
                sementes[cand] = sementes.get(cand, 0) + 1  # de quantos favoritos ele é vizinho

        linhas = [(m, score[m], sementes[m]) for m in score]
        rec = pd.DataFrame(linhas, columns=["movieId", "score", "n_favoritos"])
        rec = rec.sort_values(["score", "n_favoritos"], ascending=False)
        return self._com_titulo((rec if n is None else rec.head(n)).reset_index(drop=True))

    # ---------- comparação ----------

    def comparar_abordagens(self, user_id, n=10, k=K_VIZINHOS):
        """Top-n do user-user e do item-item para o mesmo usuário, e quantos filmes as duas listas têm em comum."""
        user_user = self.recomendar_usuario(user_id, n=n, k=k)
        item_item = self.recomendar_itemitem(user_id, n=n, k=k)
        em_comum = len(set(user_user.movieId) & set(item_item.movieId))
        return user_user, item_item, em_comum
