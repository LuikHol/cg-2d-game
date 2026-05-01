from render.pixel import setPixel
from render.scanline_core import iter_scanline_spans


def scanline_fill(surface, pontos, color):
    for y, x_ini, x_fim, _y_min, _y_max in iter_scanline_spans(pontos):
        for x in range(x_ini, x_fim + 1):
            setPixel(surface, x, y, color)


def scanline_texture(surface, pontos, textura):
    ys = [p[1] for p in pontos]
    y_min = int(min(ys))
    y_max = int(max(ys))

    largura_tex = textura.get_width()
    altura_tex = textura.get_height()

    for y, x_ini, x_fim, _scan_y_min, _scan_y_max in iter_scanline_spans(pontos):
        for x in range(x_ini, x_fim + 1):
            u = (x - x_ini) / max(1, (x_fim - x_ini))
            v = (y - y_min) / max(1, (y_max - y_min))

            tex_x = int(u * (largura_tex - 1))
            tex_y = int(v * (altura_tex - 1))

            cor = textura.get_at((tex_x, tex_y))
            setPixel(surface, x, y, cor)
