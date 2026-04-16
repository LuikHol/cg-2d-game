from render.linha import bresenham

def desenhar_poligono(surface, pontos, color):
    n = len(pontos)
    for i in range(n):
        x0, y0 = pontos[i]
        x1, y1 = pontos[(i + 1) % n]
        bresenham(surface, int(x0), int(y0), int(x1), int(y1), color)