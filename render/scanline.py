from render.pixel import setPixel

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


# =========================
# SCANLINE COM TEXTURA
# =========================
def scanline_texture(surface, pontos, textura):
    # Usa os limites verticais do poligono para normalizar a textura no eixo y.
    ys = [p[1] for p in pontos]
    y_min = int(min(ys))
    y_max = int(max(ys))

    # Tamanho da imagem usada como textura.
    largura_tex = textura.get_width()
    altura_tex = textura.get_height()

    n = len(pontos)

    # Varre cada linha horizontal do poligono.
    for y in range(y_min, y_max):
        intersecoes = []

        for i in range(n):
            x0, y0 = pontos[i]
            x1, y1 = pontos[(i+1) % n]

            if y0 == y1:
                continue

            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0

            if y < y0 or y >= y1:
                continue

            # Descobre onde a aresta cruza a scanline atual.
            x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            intersecoes.append(x)

        intersecoes.sort()

        for i in range(0, len(intersecoes), 2):
            if i + 1 < len(intersecoes):
                x_ini = int(intersecoes[i])
                x_fim = int(intersecoes[i+1])

                for x in range(x_ini, x_fim + 1):
                    # u e v sao coordenadas normalizadas entre 0 e 1 dentro da textura.
                    u = (x - x_ini) / max(1, (x_fim - x_ini))
                    v = (y - y_min) / max(1, (y_max - y_min))

                    # Converte u e v para coordenadas reais da imagem.
                    tex_x = int(u * (largura_tex - 1))
                    tex_y = int(v * (altura_tex - 1))

                    # Le a cor na textura e pinta o pixel correspondente no poligono.
                    cor = textura.get_at((tex_x, tex_y))
                    setPixel(surface, x, y, cor)