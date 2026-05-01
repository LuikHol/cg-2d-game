from render.primitivas import bresenham
from render.clipping import cohen_sutherland


def desenhar_poligono(surface, pontos, color):
    # Conta quantos vertices existem na lista de pontos.
    n = len(pontos)

    # Obtem os limites da surface para usar como janela de recorte.
    xmin, ymin = 0, 0
    xmax = surface.get_width() - 1
    ymax = surface.get_height() - 1

    # Percorre cada vertice para ligar o ponto atual ao proximo.
    for i in range(n):
        x0, y0 = pontos[i]

        # O operador % faz o ultimo ponto se ligar de volta ao primeiro.
        x1, y1 = pontos[(i + 1) % n]

        # Recorta a aresta usando Cohen-Sutherland antes de desenhar.
        # Isso garante que apenas a parte visivel da aresta sera desenhada.
        resultado = cohen_sutherland(x0, y0, x1, y1, xmin, ymin, xmax, ymax)

        # Se o resultado nao e None, a aresta (ou parte dela) esta dentro da janela.
        if resultado is not None:
            x0_clip, y0_clip, x1_clip, y1_clip = resultado
            # Desenha a aresta recortada com o algoritmo de Bresenham.
            bresenham(surface, x0_clip, y0_clip, x1_clip, y1_clip, color)