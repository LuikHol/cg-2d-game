import pygame
from render.pixel import setPixel

def escalar_superficie(src, dst_w, dst_h):
    # Redimensiona uma Surface pixel a pixel (nearest-neighbor) via setPixel.
    dst_w = max(1, int(dst_w))
    dst_h = max(1, int(dst_h))
    src_w, src_h = src.get_size()
    dst = pygame.Surface((dst_w, dst_h), pygame.SRCALPHA)
    for y in range(dst_h):
        src_y = int(y * src_h / dst_h)
        for x in range(dst_w):
            src_x = int(x * src_w / dst_w)
            setPixel(dst, x, y, src.get_at((src_x, src_y)))
    return dst

def espelhar_x(src):
    # Espelha uma Surface horizontalmente pixel a pixel via setPixel.
    w, h = src.get_size()
    dst = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        for x in range(w):
            setPixel(dst, x, y, src.get_at((w - 1 - x, y)))
    return dst