import math
import pygame

from render.collectible_sprites import get_collectible_sprite
from render.pixel import setPixel
from render.viewport import world_to_viewport

_cache_coroa_estatua = {}


def _blit_dentro_da_viewport(surface, sprite, pos, viewport):
    viewport_rect = pygame.Rect(
        viewport[0],
        viewport[1],
        max(0, viewport[2] - viewport[0]),
        max(0, viewport[3] - viewport[1]),
    )
    sprite_rect = pygame.Rect(pos, sprite.get_size())
    if not sprite_rect.colliderect(viewport_rect):
        return

    old_clip = surface.get_clip()
    surface.set_clip(viewport_rect)
    try:
        surface.blit(sprite, pos)
    finally:
        surface.set_clip(old_clip)


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
    from objects import puzzle_state
    if inventario is not None and inventario.tem("coroa_vermelha"):
        return
    if any(s == "coroa_vermelha" for s in puzzle_state.get_slots()):
        return
    estatua_wx, estatua_wy, estatua_ww = 259, 57, 102
    escala = (viewport[2] - viewport[0]) / (camera[2] - camera[0])
    pixel_size = max(2, int(escala * 7))
    coroa_surf = _get_coroa_vermelha(pixel_size)
    cx_mundo = estatua_wx + estatua_ww // 2
    cx_tela, cy_tela = world_to_viewport(cx_mundo, estatua_wy, camera, viewport)
    oscilacao = int(math.sin(pygame.time.get_ticks() * 0.003) * 3)
    pos = (cx_tela - coroa_surf.get_width() // 2, cy_tela - coroa_surf.get_height() + oscilacao)
    _blit_dentro_da_viewport(surface, coroa_surf, pos, viewport)


def desenhar_pote_urso(surface, camera, viewport, inventario=None):
    """Desenha o pote de mel sobre o urso do corredor e some ao ser coletado."""
    from objects import puzzle_state
    if inventario is not None and inventario.tem("pote_mel"):
        return
    if any(s == "pote_mel" for s in puzzle_state.get_slots()):
        return

    pote_wx, pote_wy = 1368, 127
    escala = (viewport[2] - viewport[0]) / (camera[2] - camera[0])
    pixel_size = max(2, int(escala * 3))
    pote_surf = get_collectible_sprite("pote_mel", pixel_size=pixel_size)
    px_tela, py_tela = world_to_viewport(pote_wx, pote_wy, camera, viewport)
    pos = (px_tela - pote_surf.get_width() // 2, py_tela - pote_surf.get_height() // 2)
    _blit_dentro_da_viewport(surface, pote_surf, pos, viewport)


# Posições mundo de cada círculo do tapete (centro).
_CIRCULOS_TAPETE = [
    (466, 331),  # slot 0 – coroa (topo)
    (638, 491),  # slot 1 – livro (direita)
    (289, 491),  # slot 2 – pote  (esquerda)
]
_ITENS_TAPETE = ["coroa_vermelha", "livro_laranja", "pote_mel"]


def desenhar_itens_tapete(surface, camera, viewport):
    """Desenha os itens já depositados nos círculos do tapete do quarto da rainha."""
    from objects import puzzle_state
    slots = puzzle_state.get_slots()
    escala = (viewport[2] - viewport[0]) / (camera[2] - camera[0])
    pixel_size = max(2, int(escala * 4))

    for i, item in enumerate(slots):
        if item is None:
            continue
        cx_mundo, cy_mundo = _CIRCULOS_TAPETE[i]
        sprite = get_collectible_sprite(item, pixel_size=pixel_size)
        sx, sy = world_to_viewport(cx_mundo, cy_mundo, camera, viewport)
        pos = (sx - sprite.get_width() // 2, sy - sprite.get_height() // 2)
        _blit_dentro_da_viewport(surface, sprite, pos, viewport)

    # Brilha no centro do tapete quando resolvido.
    if puzzle_state.tapete_resolvido():
        centro_wx, centro_wy = 467, 432
        sx, sy = world_to_viewport(centro_wx, centro_wy, camera, viewport)
        t = pygame.time.get_ticks() / 400.0
        raio = int(18 + math.sin(t) * 6)
        alpha = int(180 + math.sin(t * 1.5) * 60)
        glow = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 240, 100, max(0, min(255, alpha))), (raio, raio), raio)
        pos = (sx - raio, sy - raio)
        _blit_dentro_da_viewport(surface, glow, pos, viewport)


def desenhar_livro_coala(surface, camera, viewport, inventario=None):
    """Desenha o livro laranja sobre a estatua do coala e some ao ser coletado."""
    from objects import puzzle_state
    if inventario is not None and inventario.tem("livro_laranja"):
        return
    if any(s == "livro_laranja" for s in puzzle_state.get_slots()):
        return

    livro_wx, livro_wy = 335, 575
    escala = (viewport[2] - viewport[0]) / (camera[2] - camera[0])
    pixel_size = max(2, int(escala * 5))
    livro_surf = get_collectible_sprite("livro_laranja", pixel_size=pixel_size)
    lx_tela, ly_tela = world_to_viewport(livro_wx, livro_wy, camera, viewport)
    pos = (lx_tela - livro_surf.get_width() // 2, ly_tela - livro_surf.get_height() // 2)
    _blit_dentro_da_viewport(surface, livro_surf, pos, viewport)
