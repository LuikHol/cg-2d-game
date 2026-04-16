def setPixel(surface, x, y, color):
    # Garante que o pixel esteja dentro dos limites da surface.
    if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
        # Pinta o pixel na coordenada (x, y) com a cor informada.
        surface.set_at((x, y), color)