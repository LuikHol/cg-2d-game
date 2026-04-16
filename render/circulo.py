from render.pixel import setPixel

def desenhar_circulo(surface, xc, yc, r, color):
    # Começa no topo do círculo relativo ao centro (xc, yc).
    x = 0
    y = r

    # Variável de decisão do algoritmo do ponto médio.
    d = 1 - r

    def plot(x, y):
        # Usa a simetria do círculo para desenhar 8 pontos de uma vez.
        setPixel(surface, xc + x, yc + y, color)
        setPixel(surface, xc - x, yc + y, color)
        setPixel(surface, xc + x, yc - y, color)
        setPixel(surface, xc - x, yc - y, color)
        setPixel(surface, xc + y, yc + x, color)
        setPixel(surface, xc - y, yc + x, color)
        setPixel(surface, xc + y, yc - x, color)
        setPixel(surface, xc - y, yc - x, color)

    # Percorre apenas um octante; os outros são obtidos por espelhamento.
    while x <= y:
        plot(x, y)

        # Se o erro ainda estiver dentro do círculo, anda só no eixo x.
        if d < 0:
            d += 2 * x + 3
        else:
            # Caso contrário, ajusta y para manter a curva próxima do círculo ideal.
            d += 2 * (x - y) + 5
            y -= 1

        # O algoritmo sempre avança uma coluna por iteração.
        x += 1