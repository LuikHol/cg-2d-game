def setPixel(surface, x, y, color):
    """Desenha um pixel na superficie, apenas se dentro dos limites."""
    if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
        surface.set_at((x, y), color)