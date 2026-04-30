import pygame
from pathlib import Path

from render.poligono import desenhar_poligono
from render.scanline import scanline_fill
from render.textura import scanline_texture
from render.clipping import clip_polygon_sutherland_hodgman
from render.viewport import transformar_pontos, world_to_viewport
from render.pixel import setPixel
from configs.game_config import ZOOM_TEXTURA_FUNDO

_background_cache = {}


def item_eh_chao_base(item):
    return isinstance(item, dict) and item.get("skip_on_background", False)


def desenhar_item(surface, item, camera, viewport, textures, debug_clip=False):
    if isinstance(item, dict):
        pontos = item["polygon"]
        cor_fill = item.get("fill_color")
        cor_borda = item.get("border_color")
        texture_key = item.get("texture_key")
        show_border = item.get("show_border", True)
    else:
        pontos, cor_fill, cor_borda = item
        texture_key = None
        show_border = True

    clip = clip_polygon_sutherland_hodgman(pontos, *camera)
    if len(clip) >= 3:
        if debug_clip:
            original_tela = transformar_pontos(pontos, camera, viewport)
            desenhar_poligono(surface, original_tela, (90, 90, 90))

        tela = transformar_pontos(clip, camera, viewport)
        # A chave pode existir com valor None (ex.: arquivo de textura ausente).
        # Nesse caso, cai no preenchimento por cor para evitar crash.
        textura_item = textures.get(texture_key) if texture_key else None
        if textura_item is not None:
            scanline_texture(surface, tela, textura_item)
        elif cor_fill is not None:
            scanline_fill(surface, tela, cor_fill)

        if show_border and cor_borda is not None:
            desenhar_poligono(surface, tela, cor_borda)

        if debug_clip:
            desenhar_poligono(surface, tela, (0, 255, 255))


def _carregar_background(path_str):
    if path_str not in _background_cache:
        _background_cache[path_str] = pygame.image.load(Path(path_str)).convert()
    return _background_cache[path_str]


def desenhar_background_da_sala(surface, room_data, camera, viewport):
    background_path = room_data.get("background_texture")
    if not background_path:
        return False

    background = _carregar_background(background_path)
    viewport_size = (viewport[2] - viewport[0], viewport[3] - viewport[1])
    zoom = float(room_data.get("background_zoom", ZOOM_TEXTURA_FUNDO))
    zoom = max(1.0, zoom)
    cache_key = (background_path, viewport_size, zoom)

    if cache_key not in _background_cache:
        out_w, out_h = viewport_size
        tex_w = background.get_width()
        tex_h = background.get_height()
        sampled = pygame.Surface((out_w, out_h)).convert()

        sample_w = 1.0 / zoom
        sample_h = 1.0 / zoom
        sample_u0 = (1.0 - sample_w) * 0.5
        sample_v0 = (1.0 - sample_h) * 0.5

        for y in range(out_h):
            v = y / max(1, out_h - 1)
            sv = sample_v0 + v * sample_h
            tex_y = int(sv * (tex_h - 1))
            for x in range(out_w):
                u = x / max(1, out_w - 1)
                su = sample_u0 + u * sample_w
                tex_x = int(su * (tex_w - 1))
                setPixel(sampled, x, y, background.get_at((tex_x, tex_y)))

        _background_cache[cache_key] = sampled

    surface.blit(_background_cache[cache_key], (viewport[0], viewport[1]))
    return True


def desenhar_foreground(surface, room_data, camera, viewport, textures, debug_clip=False):
    foreground_image_cache = {}
    for item in room_data.get("foreground", []):
        if isinstance(item, dict) and "image_path" in item:
            img_path = item["image_path"]
            wx, wy, ww, wh = item["rect"]
            if img_path not in foreground_image_cache:
                foreground_image_cache[img_path] = pygame.image.load(img_path).convert_alpha()
            raw = foreground_image_cache[img_path]
            sx1, sy1 = world_to_viewport(wx, wy, camera, viewport)
            sx2, sy2 = world_to_viewport(wx + ww, wy + wh, camera, viewport)
            sw, sh = max(1, sx2 - sx1), max(1, sy2 - sy1)
            screen_img = pygame.transform.scale(raw, (sw, sh))
            surface.blit(screen_img, (sx1, sy1))
        else:
            desenhar_item(surface, item, camera, viewport, textures, debug_clip)


def desenhar_sala(surface, room_data, camera, viewport, textures, debug_clip=False):
    """Desenha background + polígonos + portas visuais da sala."""
    tem_background = desenhar_background_da_sala(surface, room_data, camera, viewport)
    for item in room_data["poligonos"]:
        if tem_background and item_eh_chao_base(item):
            continue
        desenhar_item(surface, item, camera, viewport, textures, debug_clip)
    for item in room_data["portas_visuais"]:
        desenhar_item(surface, item, camera, viewport, textures, debug_clip)
    return tem_background
