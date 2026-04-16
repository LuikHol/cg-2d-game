from render.linha import bresenham

def desenhar_poligono(surface, pontos, color):
    # Conta quantos vertices existem na lista de pontos.
    n = len(pontos)

    # Percorre cada vertice para ligar o ponto atual ao proximo.
    for i in range(n):
        x0, y0 = pontos[i]

        # O operador % faz o ultimo ponto se ligar de volta ao primeiro.
        x1, y1 = pontos[(i + 1) % n]

        # Cada aresta do poligono e desenhada com o algoritmo de Bresenham.
        bresenham(surface, int(x0), int(y0), int(x1), int(y1), color)