import math


def polygon_centroid(pontos):
    """Retorna o centroide de um poligono como tupla float (cx, cy)."""
    if not pontos:
        return 0.0, 0.0
    n = len(pontos)
    cx = sum(p[0] for p in pontos) / n
    cy = sum(p[1] for p in pontos) / n
    return cx, cy


def polygon_bounds(pontos, margem=0):
    """Retorna bounds (xmin, ymin, xmax, ymax) com margem opcional."""
    if not pontos:
        return 0, 0, 0, 0
    xs = [p[0] for p in pontos]
    ys = [p[1] for p in pontos]
    xmin = min(xs) - margem
    ymin = min(ys) - margem
    xmax = max(xs) + margem
    ymax = max(ys) + margem
    return xmin, ymin, xmax, ymax


def ellipse_points(cx, cy, rx, ry, segmentos=56):
    """Gera vertices inteiros aproximando uma elipse."""
    pontos = []
    for i in range(segmentos):
        ang = (2.0 * math.pi * i) / segmentos
        x = int(cx + rx * math.cos(ang))
        y = int(cy + ry * math.sin(ang))
        pontos.append((x, y))
    return pontos
