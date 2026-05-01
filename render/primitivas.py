from render.pixel import setPixel


def bresenham(surface, x0, y0, x1, y1, color):
    # Verifica se a linha e mais inclinada no eixo y do que no eixo x.
    steep = abs(y1 - y0) > abs(x1 - x0)

    if steep:
        # Troca x por y para tratar linhas inclinadas como se fossem "normais".
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        # Garante que o desenho aconteca da esquerda para a direita.
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    # Diferencas entre os pontos inicial e final.
    dx = x1 - x0
    dy = abs(y1 - y0)

    # Define se y deve subir ou descer durante o percurso.
    ystep = 1 if y0 < y1 else -1

    # Erro acumulado para decidir quando mover no eixo y.
    error = dx // 2
    y = y0

    for x in range(x0, x1 + 1):
        if steep:
            # Se houve troca de eixos, desenha invertendo as coordenadas.
            setPixel(surface, y, x, color)
        else:
            setPixel(surface, x, y, color)

        # Atualiza o erro com base na variacao vertical da reta.
        error -= dy
        if error < 0:
            # Quando o erro passa do limite, avanca uma linha no eixo y.
            y += ystep
            error += dx


def desenhar_circulo(surface, xc, yc, r, color):
    # Comeca no topo do circulo relativo ao centro (xc, yc).
    x = 0
    y = r

    # Variavel de decisao do algoritmo do ponto medio.
    d = 1 - r

    def plot(px, py):
        # Usa a simetria do circulo para desenhar 8 pontos de uma vez.
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

        # Se o erro ainda estiver dentro do circulo, anda so no eixo x.
        if d < 0:
            d += 2 * x + 3
        else:
            # Caso contrario, ajusta y para manter a curva proxima do circulo ideal.
            d += 2 * (x - y) + 5
            y -= 1

        # O algoritmo sempre avanca uma coluna por iteracao.
        x += 1


def desenhar_elipse(surface, xc, yc, rx, ry, color):
    # Comeca no topo da elipse relativo ao centro (xc, yc).
    x = 0
    y = ry

    # Pre-calcula os quadrados dos raios para evitar repeticao.
    rx2 = rx * rx
    ry2 = ry * ry

    # Variavel de decisao para a regiao 1 (curva mais horizontal).
    p1 = ry2 - rx2 * ry + 0.25 * rx2

    # Regiao 1: percorre a parte onde a curva varia mais no eixo x.
    dx = 2 * ry2 * x
    dy = 2 * rx2 * y

    # Continua enquanto a variacao horizontal for menor que a vertical.
    while dx < dy:
        _plot_ellipse(surface, xc, yc, x, y, color)

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

    # Regiao 2: percorre a parte onde a curva varia mais no eixo y.
    p2 = (ry2 * (x + 0.5) ** 2) + (rx2 * (y - 1) ** 2) - (rx2 * ry2)

    # Continua descendo ate y chegar em 0 (metade inferior ja e espelhada por plot).
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
    # Usa a simetria da elipse para desenhar 4 pontos de uma vez.
    setPixel(surface, xc + x, yc + y, color)
    setPixel(surface, xc - x, yc + y, color)
    setPixel(surface, xc + x, yc - y, color)
    setPixel(surface, xc - x, yc - y, color)


def flood_fill(surface, x, y, new_color, border_color):
    # A pilha guarda os pixels que ainda precisam ser analisados.
    stack = [(x, y)]

    while stack:
        # Remove o ultimo pixel adicionado para processar agora.
        x, y = stack.pop()

        # Ignora pixels que estejam fora dos limites da tela.
        if not (0 <= x < surface.get_width() and 0 <= y < surface.get_height()):
            continue

        # Le a cor atual do pixel; [:3] pega apenas RGB e ignora alpha.
        current = surface.get_at((x, y))[:3]

        # Para ao encontrar a borda ou uma area que ja foi preenchida.
        if current == border_color or current == new_color:
            continue

        # Pinta o pixel atual com a nova cor.
        setPixel(surface, x, y, new_color)

        # Adiciona os 4 vizinhos para continuar o preenchimento.
        stack.append((x + 1, y))
        stack.append((x - 1, y))
        stack.append((x, y + 1))
        stack.append((x, y - 1))
