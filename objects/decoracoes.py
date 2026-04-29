import math
import pygame

from render.pixel import setPixel
from render.viewport import world_to_viewport

_cache_coroa_estatua = {}


def _get_coroa_vermelha(pixel_size):
    chave = max(1, int(pixel_size))
    if chave in _cache_coroa_estatua:
        return _cache_coroa_estatua[chave]

    pattern = [
        "1001001",
        "1011101",
        "1111111",
        "0111110",
        "0111110",
    ]
    largura = len(pattern[0]) * chave
    altura = len(pattern) * chave
    surf = pygame.Surface((largura, altura), pygame.SRCALPHA)
    vermelho        = (210,  40,  40, 255)
    vermelho_escuro = (140,  20,  20, 255)
    joia            = (255, 200,  60, 255)

    for py, row in enumerate(pattern):
        for px, val in enumerate(row):
            if val == "0":
                continue
            cor = vermelho if py < len(pattern) - 2 else vermelho_escuro
            if (px, py) == (3, 1):
                cor = joia
            for dy in range(chave):
                for dx in range(chave):
                    setPixel(surf, px * chave + dx, py * chave + dy, cor)

    _cache_coroa_estatua[chave] = surf
    return surf


def desenhar_coroa_estatua(surface, camera, viewport, inventario=None):
    """Desenha a coroa vermelha flutuante sobre a estátua gata (some ao ser coletada)."""
    if inventario is not None and inventario.tem("coroa_vermelha"):
        return
    estatua_wx, estatua_wy, estatua_ww = 259, 57, 102
    escala = (viewport[2] - viewport[0]) / (camera[2] - camera[0])
    pixel_size = max(2, int(escala * 7))
    coroa_surf = _get_coroa_vermelha(pixel_size)
    cx_mundo = estatua_wx + estatua_ww // 2
    cx_tela, cy_tela = world_to_viewport(cx_mundo, estatua_wy, camera, viewport)
    oscilacao = int(math.sin(pygame.time.get_ticks() * 0.003) * 3)
    pos = (cx_tela - coroa_surf.get_width() // 2, cy_tela - coroa_surf.get_height() + oscilacao)
    surface.blit(coroa_surf, pos)
