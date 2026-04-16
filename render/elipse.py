from render.pixel import setPixel

def desenhar_elipse(surface, xc, yc, rx, ry, color):
    # Começa no topo da elipse relativo ao centro (xc, yc).
    x = 0
    y = ry

    # Pre-calcula os quadrados dos raios para evitar repeticao.
    rx2 = rx * rx
    ry2 = ry * ry

    # Variavel de decisao para a regiao 1 (curva mais horizontal).
    p1 = ry2 - rx2 * ry + 0.25 * rx2

    # Região 1: percorre a parte onde a curva varia mais no eixo x.
    dx = 2 * ry2 * x
    dy = 2 * rx2 * y

    # Continua enquanto a variacao horizontal for menor que a vertical.
    while dx < dy:
        plot_ellipse(surface, xc, yc, x, y, color)

        if p1 < 0:
            # Ainda dentro da curva: avanca so em x.
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

    # Região 2: percorre a parte onde a curva varia mais no eixo y.
    p2 = (ry2 * (x + 0.5)**2) + (rx2 * (y - 1)**2) - (rx2 * ry2)

    # Continua descendo ate y chegar em 0 (metade inferior ja e espelhada por plot_ellipse).
    while y >= 0:
        plot_ellipse(surface, xc, yc, x, y, color)

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


def plot_ellipse(surface, xc, yc, x, y, color):
    # Usa a simetria da elipse para desenhar 4 pontos de uma vez.
    setPixel(surface, xc + x, yc + y, color)  # quadrante inferior direito
    setPixel(surface, xc - x, yc + y, color)  # quadrante inferior esquerdo
    setPixel(surface, xc + x, yc - y, color)  # quadrante superior direito
    setPixel(surface, xc - x, yc - y, color)  # quadrante superior esquerdo