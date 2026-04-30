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
_foreground_image_cache = {}


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
    out_w = viewport[2] - viewport[0]
    out_h = viewport[3] - viewport[1]
    tex_w = background.get_width()
    tex_h = background.get_height()

    # Define em que area do mundo esse PNG representa.
    # Para salas maiores (ex.: corredor horizontal), isso permite pan com a camera.
    bg_bounds = room_data.get("background_bounds", camera)
    bx0, by0, bx1, by1 = bg_bounds
    bw = max(1.0, float(bx1 - bx0))
    bh = max(1.0, float(by1 - by0))

    cx0, cy0, cx1, cy1 = camera
    cam_w = max(1.0, float(cx1 - cx0))
    cam_h = max(1.0, float(cy1 - cy0))

    # Mapeia o retangulo atual da camera para coordenadas da textura.
    src_x = int((cx0 - bx0) / bw * tex_w)
    src_y = int((cy0 - by0) / bh * tex_h)
    src_w = int(cam_w / bw * tex_w)
    src_h = int(cam_h / bh * tex_h)

    src_w = max(1, min(tex_w, src_w))
    src_h = max(1, min(tex_h, src_h))
    src_x = max(0, min(tex_w - src_w, src_x))
    src_y = max(0, min(tex_h - src_h, src_y))

    recorte = background.subsurface((src_x, src_y, src_w, src_h))
    amostra = pygame.transform.scale(recorte, (out_w, out_h))
    surface.blit(amostra, (viewport[0], viewport[1]))
    return True


def desenhar_foreground(surface, room_data, camera, viewport, textures, debug_clip=False):
    for item in room_data.get("foreground", []):
        if isinstance(item, dict) and "image_path" in item:
            img_path = item["image_path"]
            wx, wy, ww, wh = item["rect"]
            if img_path not in _foreground_image_cache:
                _foreground_image_cache[img_path] = pygame.image.load(img_path).convert_alpha()
            raw = _foreground_image_cache[img_path]
            sx1, sy1 = world_to_viewport(wx, wy, camera, viewport)
            sx2, sy2 = world_to_viewport(wx + ww, wy + wh, camera, viewport)
            sw, sh = max(1, sx2 - sx1), max(1, sy2 - sy1)

            if item.get("preserve_aspect", True):
                raw_w, raw_h = raw.get_size()
                escala = min(sw / max(1, raw_w), sh / max(1, raw_h))
                tw = max(1, int(raw_w * escala))
                th = max(1, int(raw_h * escala))
                screen_img = pygame.transform.scale(raw, (tw, th))
                # Mantem o objeto apoiado no "chao" do retangulo e centralizado no eixo X.
                draw_x = sx1 + (sw - tw) // 2
                draw_y = sy1 + (sh - th)
                surface.blit(screen_img, (draw_x, draw_y))
            else:
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
