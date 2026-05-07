from render.pixel import setPixel


def bresenham(surface, x0, y0, x1, y1, color):
    steep = abs(y1 - y0) > abs(x1 - x0)

    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = abs(y1 - y0)
    ystep = 1 if y0 < y1 else -1
    # Erro acumulado: quando passa de zero, avanca uma linha no eixo y.
    error = dx // 2
    y = y0

    for x in range(x0, x1 + 1):
        setPixel(surface, y, x, color) if steep else setPixel(surface, x, y, color)
        error -= dy
        if error < 0:
            y += ystep
            error += dx


def desenhar_circulo(surface, xc, yc, r, color):
    x = 0
    y = r
    # Variavel de decisao do algoritmo do ponto medio.
    d = 1 - r

    def plot(px, py):
        # Usa a simetria de 8 pontos do circulo de uma vez.
        setPixel(surface, xc + px, yc + py, color)
        setPixel(surface, xc - px, yc + py, color)
        setPixel(surface, xc + px, yc - py, color)
        setPixel(surface, xc - px, yc - py, color)
        setPixel(surface, xc + py, yc + px, color)
        setPixel(surface, xc - py, yc + px, color)
        setPixel(surface, xc + py, yc - px, color)
        setPixel(surface, xc - py, yc - px, color)

    # Percorre apenas um octante; os outros sao obtidos por espelhamento.
    while x <= y:
        plot(x, y)
        if d < 0:
            d += 2 * x + 3
        else:
            # Ajusta y para manter a curva proxima do circulo ideal.
            d += 2 * (x - y) + 5
            y -= 1
        x += 1


def desenhar_elipse(surface, xc, yc, rx, ry, color):
    x = 0
    y = ry
    # Pre-calcula os quadrados dos raios para evitar repeticao.
    rx2 = rx * rx
    ry2 = ry * ry

    # Variavel de decisao para a regiao 1 (curva mais horizontal).
    p1 = ry2 - rx2 * ry + 0.25 * rx2
    dx = 2 * ry2 * x
    dy = 2 * rx2 * y

    # Regiao 1: dx < dy (curva varia mais no eixo x).
    while dx < dy:
        _plot_ellipse(surface, xc, yc, x, y, color)
        if p1 < 0:
            # Dentro da curva: avanca so em x.
            x += 1
            dx = 2 * ry2 * x
            p1 += dx + ry2
        else:
            # Passou da curva: avanca em x e recua em y.
            x += 1
            y -= 1
            dx = 2 * ry2 * x
            dy = 2 * rx2 * y
            p1 += dx - dy + ry2

    # Regiao 2: curva varia mais no eixo y; metade inferior espelhada por _plot_ellipse.
    p2 = (ry2 * (x + 0.5) ** 2) + (rx2 * (y - 1) ** 2) - (rx2 * ry2)
    while y >= 0:
        _plot_ellipse(surface, xc, yc, x, y, color)
        if p2 > 0:
            # Fora da curva: recua so em y.
            y -= 1
            dy = 2 * rx2 * y
            p2 += rx2 - dy
        else:
            # Dentro da curva: recua em y e avanca em x.
            y -= 1
            x += 1
            dx = 2 * ry2 * x
            dy = 2 * rx2 * y
            p2 += dx - dy + rx2


def _plot_ellipse(surface, xc, yc, x, y, color):
    # Usa a simetria de 4 pontos da elipse de uma vez.
    setPixel(surface, xc + x, yc + y, color)
    setPixel(surface, xc - x, yc + y, color)
    setPixel(surface, xc + x, yc - y, color)
    setPixel(surface, xc - x, yc - y, color)


def flood_fill(surface, x, y, new_color, border_color):
    stack = [(x, y)]
    while stack:
        x, y = stack.pop()
        if not (0 <= x < surface.get_width() and 0 <= y < surface.get_height()):
            continue
        # [:3] pega apenas RGB, ignorando alpha.
        current = surface.get_at((x, y))[:3]
        # Para ao encontrar a borda ou area ja preenchida.
        if current == border_color or current == new_color:
            continue
        setPixel(surface, x, y, new_color)
        stack.append((x + 1, y))
        stack.append((x - 1, y))
        stack.append((x, y + 1))
        stack.append((x, y - 1))