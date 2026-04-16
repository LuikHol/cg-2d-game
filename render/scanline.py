from render.pixel import setPixel

# =========================
# SCANLINE NORMAL (cor sólida)
# =========================
def scanline_fill(surface, pontos, color):
    ys = [p[1] for p in pontos]
    y_min = int(min(ys))
    y_max = int(max(ys))

    n = len(pontos)

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

            x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            intersecoes.append(x)

        intersecoes.sort()

        for i in range(0, len(intersecoes), 2):
            if i + 1 < len(intersecoes):
                for x in range(int(intersecoes[i]), int(intersecoes[i+1]) + 1):
                    setPixel(surface, x, y, color)


# =========================
# SCANLINE COM TEXTURA
# =========================
def scanline_texture(surface, pontos, textura):
    ys = [p[1] for p in pontos]
    y_min = int(min(ys))
    y_max = int(max(ys))

    largura_tex = textura.get_width()
    altura_tex = textura.get_height()

    n = len(pontos)

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

            x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            intersecoes.append(x)

        intersecoes.sort()

        for i in range(0, len(intersecoes), 2):
            if i + 1 < len(intersecoes):
                x_ini = int(intersecoes[i])
                x_fim = int(intersecoes[i+1])

                for x in range(x_ini, x_fim + 1):
                    u = (x - x_ini) / max(1, (x_fim - x_ini))
                    v = (y - y_min) / max(1, (y_max - y_min))

                    tex_x = int(u * (largura_tex - 1))
                    tex_y = int(v * (altura_tex - 1))

                    cor = textura.get_at((tex_x, tex_y))
                    setPixel(surface, x, y, cor)