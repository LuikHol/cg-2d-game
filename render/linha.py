from render.pixel import setPixel

def bresenham(surface, x0, y0, x1, y1, color):
    # Verifica se a linha é mais inclinada no eixo y do que no eixo x.
    steep = abs(y1 - y0) > abs(x1 - x0)

    if steep:
        # Troca x por y para tratar linhas inclinadas como se fossem "normais".
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        # Garante que o desenho aconteça da esquerda para a direita.
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