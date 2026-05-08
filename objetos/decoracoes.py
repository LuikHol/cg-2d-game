import math
import pygame

from render.pixel import setPixel
from render.sprites_colecionaveis import obter_sprite_colecionavel
from render.viewport import mundo_para_viewport
from render.primitivas import desenhar_circulo

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

    # Copia sprite pixel a pixel usando setPixel, respeitando transparência
    sprite_w, sprite_h = sprite.get_size()
    for y in range(sprite_h):
        for x in range(sprite_w):
            pixel = sprite.get_at((x, y))
            # Só desenha se o pixel tiver alpha > 0
            if len(pixel) > 3 and pixel[3] > 0:  # Tem canal alpha e não é totalmente transparente
                screen_x = pos[0] + x
                screen_y = pos[1] + y
                # Verifica se está dentro do viewport
                if (viewport_rect.left <= screen_x < viewport_rect.right and
                    viewport_rect.top <= screen_y < viewport_rect.bottom):
                    setPixel(surface, screen_x, screen_y, pixel)

def desenhar_coroa_estatua(surface, camera, viewport, inventario=None):
    # Desenha a coroa vermelha sobre a gata no quarto e some ao ser coletado.
    from objetos import estado_puzzle
    if inventario is not None and inventario.tem("coroa_vermelha"):
        return
    if any(s == "coroa_vermelha" for s in estado_puzzle.obter_slots()):
        return
    estatua_wx, estatua_wy, estatua_ww = 259, 57, 102
    escala = (viewport[2] - viewport[0]) / (camera[2] - camera[0])
    pixel_size = max(2, int(escala * 7))
    coroa_surf = obter_sprite_colecionavel("coroa_vermelha", pixel_size=pixel_size)
    cx_mundo = estatua_wx + estatua_ww // 2
    cx_tela, cy_tela = mundo_para_viewport(cx_mundo, estatua_wy, camera, viewport)
    oscilacao = int(math.sin(pygame.time.get_ticks() * 0.003) * 3)
    pos = (cx_tela - coroa_surf.get_width() // 2, cy_tela - coroa_surf.get_height() + oscilacao)
    _blit_dentro_da_viewport(surface, coroa_surf, pos, viewport)


def desenhar_pote_urso(surface, camera, viewport, inventario=None):
    # Desenha o pote de mel sobre o urso do corredor e some ao ser coletado.
    from objetos import estado_puzzle
    if inventario is not None and inventario.tem("pote_mel"):
        return
    if any(s == "pote_mel" for s in estado_puzzle.obter_slots()):
        return

    pote_wx, pote_wy = 1368, 127
    escala = (viewport[2] - viewport[0]) / (camera[2] - camera[0])
    pixel_size = max(2, int(escala * 3))
    pote_surf = obter_sprite_colecionavel("pote_mel", pixel_size=pixel_size)
    px_tela, py_tela = mundo_para_viewport(pote_wx, pote_wy, camera, viewport)
    pos = (px_tela - pote_surf.get_width() // 2, py_tela - pote_surf.get_height() // 2)
    _blit_dentro_da_viewport(surface, pote_surf, pos, viewport)


def desenhar_livro_coala(surface, camera, viewport, inventario=None):
    # Desenha o livro laranja sobre a estatua do coala e some ao ser coletado.
    from objetos import estado_puzzle
    if inventario is not None and inventario.tem("livro_laranja"):
        return
    if any(s == "livro_laranja" for s in estado_puzzle.obter_slots()):
        return

    livro_wx, livro_wy = 335, 575
    escala = (viewport[2] - viewport[0]) / (camera[2] - camera[0])
    pixel_size = max(2, int(escala * 5))
    livro_surf = obter_sprite_colecionavel("livro_laranja", pixel_size=pixel_size)
    lx_tela, ly_tela = mundo_para_viewport(livro_wx, livro_wy, camera, viewport)
    pos = (lx_tela - livro_surf.get_width() // 2, ly_tela - livro_surf.get_height() // 2)
    _blit_dentro_da_viewport(surface, livro_surf, pos, viewport)

# Posições mundo de cada círculo do tapete (centro).
_CIRCULOS_TAPETE = [
    (289, 491),  # slot 0 – coroa (esquerda)
    (466, 331),  # slot 1 – livro (topo)
    (638, 491),  # slot 2 – pote  (direita)
]
_ITENS_TAPETE = ["coroa_vermelha", "livro_laranja", "pote_mel"]

def desenhar_itens_tapete(surface, camera, viewport):
    # Desenha os itens já depositados nos círculos do tapete do quarto da rainha.
    from objetos import estado_puzzle
    slots = estado_puzzle.obter_slots()
    escala = (viewport[2] - viewport[0]) / (camera[2] - camera[0])
    pixel_size = max(2, int(escala * 4))

    for i, item in enumerate(slots):
        if item is None:
            continue
        cx_mundo, cy_mundo = _CIRCULOS_TAPETE[i]
        sprite = obter_sprite_colecionavel(item, pixel_size=pixel_size)
        sx, sy = mundo_para_viewport(cx_mundo, cy_mundo, camera, viewport)
        pos = (sx - sprite.get_width() // 2, sy - sprite.get_height() // 2)
        _blit_dentro_da_viewport(surface, sprite, pos, viewport)

    # Brilha no centro do tapete quando resolvido.
    if estado_puzzle.tapete_resolvido():
        centro_wx, centro_wy = 467, 432
        sx, sy = mundo_para_viewport(centro_wx, centro_wy, camera, viewport)
        t = pygame.time.get_ticks() / 400.0
        raio = int(18 + math.sin(t) * 6)
        alpha = int(180 + math.sin(t * 1.5) * 60)
        glow = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        desenhar_circulo(glow, raio, raio, raio, (255, 240, 100, max(0, min(255, alpha))))
        pos = (sx - raio, sy - raio)
        _blit_dentro_da_viewport(surface, glow, pos, viewport)


