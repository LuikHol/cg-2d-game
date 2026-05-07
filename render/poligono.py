from render.primitivas import bresenham
from render.clipping import cohen_sutherland


def desenhar_poligono(surface, pontos, color):
    n = len(pontos)

    # Obtem os limites da surface para usar como janela de recorte.
    xmin, ymin = 0, 0
    xmax = surface.get_width() - 1
    ymax = surface.get_height() - 1

    for i in range(n):
        x0, y0 = pontos[i]
        x1, y1 = pontos[(i + 1) % n]

        # Recorta a aresta usando Cohen-Sutherland antes de desenhar.
        # Isso garante que apenas a parte visivel da aresta sera desenhada.
        resultado = cohen_sutherland(x0, y0, x1, y1, xmin, ymin, xmax, ymax)

        if resultado is not None:
            x0_clip, y0_clip, x1_clip, y1_clip = resultado
            # Desenha a aresta recortada com o algoritmo de Bresenham.
            bresenham(surface, x0_clip, y0_clip, x1_clip, y1_clip, color)