from render.pixel import setPixel
from render.textura import scanline_texture

# =========================
# SCANLINE NORMAL (cor sólida)
# =========================
def scanline_fill(surface, pontos, color):
    # Coleta todos os valores de y para descobrir a altura total do poligono.
    ys = [p[1] for p in pontos]
    y_min = int(min(ys))
    y_max = int(max(ys))

    # Quantidade de vertices do poligono.
    n = len(pontos)

    # Percorre cada linha horizontal entre o topo e a base do poligono.
    for y in range(y_min, y_max):
        intersecoes = []

        for i in range(n):
            x0, y0 = pontos[i]
            x1, y1 = pontos[(i+1) % n]

            # Ignora arestas horizontais para evitar contagens duplicadas.
            if y0 == y1:
                continue

            if y0 > y1:
                # Reorganiza a aresta para sempre ir do menor y para o maior y.
                x0, y0, x1, y1 = x1, y1, x0, y0

            # Usa apenas arestas que realmente cruzam a linha atual.
            if y < y0 or y >= y1:
                continue

            # Calcula o x onde a aresta cruza a scanline atual.
            x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            intersecoes.append(x)

        # Ordena os pontos de entrada e saida na linha horizontal.
        intersecoes.sort()

        # Preenche entre pares de intersecoes: entra no poligono e depois sai dele.
        for i in range(0, len(intersecoes), 2):
            if i + 1 < len(intersecoes):
                for x in range(int(intersecoes[i]), int(intersecoes[i+1]) + 1):
                    setPixel(surface, x, y, color)

