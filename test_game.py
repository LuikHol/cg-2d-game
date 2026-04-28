import pygame
import sys
from pathlib import Path
from objects.player_object import PlayerObject
from objects.interaction_manager import InteractionManager
from objects.room_manager import RoomManager
from world.rooms import build_rooms
from render.poligono import desenhar_poligono
from render.scanline import scanline_fill
from render.textura import scanline_texture
from render.clipping import clip_polygon_sutherland_hodgman
from render.viewport import transformar_pontos
from musica_loop import iniciar_musica_loop, trocar_musica_se_existir, parar_musica

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RPG - teste")
clock = pygame.time.Clock()
textura = pygame.image.load("textura.jpg")

# Iniciar música de fundo
iniciar_musica_loop(volume=0.5)

# Troca de trilha por sala (ajuste os nomes para os arquivos da pasta musica/).
MUSICA_POR_SALA = {
    "sala_1": "dorminho2.mp3",
    "corredor": "dorminhogrande.mp3",
    "sala_2": "sala_2.mp3",
}

WORLD_W = 1000
WORLD_H = 750
BACKGROUND_TEXTURE_ZOOM = 1.35

rooms = build_rooms()
room_manager = RoomManager(rooms, "sala_1")

# ─── PLAYER ────────────────────────────────────────────────────────────────
player = PlayerObject(500, 440)

# ─── CÂMERA FIXA / VIEWPORT ────────────────────────────────────────────────
VP_MARGIN = 90
camera = (0, 0, WORLD_W, WORLD_H)
viewport = (VP_MARGIN, VP_MARGIN, WIDTH - VP_MARGIN, HEIGHT - VP_MARGIN)
interaction_manager = InteractionManager(paper_texture=textura)
textures = {
    "paper": textura,
}
background_cache = {}


# ─── HELPER ────────────────────────────────────────────────────────────────
def desenhar_item(surface, item, camera, debug_clip=False):
    if isinstance(item, dict):
        pontos = item["polygon"]
        cor_fill = item.get("fill_color")
        cor_borda = item.get("border_color")
        texture_key = item.get("texture_key")
        show_border = item.get("show_border", True)
    else:
        # Compatibilidade com itens antigos em tupla.
        pontos, cor_fill, cor_borda = item
        texture_key = None
        show_border = True

    clip = clip_polygon_sutherland_hodgman(pontos, *camera)
    if len(clip) >= 3:
        if debug_clip:
            # Mostra o poligono original na viewport para comparar com o recorte.
            original_tela = transformar_pontos(pontos, camera, viewport)
            desenhar_poligono(surface, original_tela, (90, 90, 90))

        tela = transformar_pontos(clip, camera, viewport)
        if texture_key and texture_key in textures:
            scanline_texture(surface, tela, textures[texture_key])
        elif cor_fill is not None:
            scanline_fill(surface, tela, cor_fill)

        if show_border and cor_borda is not None:
            desenhar_poligono(surface, tela, cor_borda)

        if debug_clip:
            # Destaca a borda final apos o clipping.
            desenhar_poligono(surface, tela, (0, 255, 255))


def carregar_background(path_str):
    if path_str not in background_cache:
        texture_path = Path(path_str)
        background_cache[path_str] = pygame.image.load(texture_path).convert()
    return background_cache[path_str]


def desenhar_background_da_sala(surface, room_data, camera, viewport):
    background_path = room_data.get("background_texture")
    if not background_path:
        return False

    background = carregar_background(background_path)
    viewport_size = (viewport[2] - viewport[0], viewport[3] - viewport[1])
    zoom = float(room_data.get("background_zoom", BACKGROUND_TEXTURE_ZOOM))
    zoom = max(1.0, zoom)
    cache_key = (background_path, viewport_size, zoom)

    if cache_key not in background_cache:
        zoomed_size = (
            int(viewport_size[0] * zoom),
            int(viewport_size[1] * zoom),
        )
        background_zoomed = pygame.transform.scale(background, zoomed_size)
        crop_rect = pygame.Rect(
            (zoomed_size[0] - viewport_size[0]) // 2,
            (zoomed_size[1] - viewport_size[1]) // 2,
            viewport_size[0],
            viewport_size[1],
        )
        background_cache[cache_key] = background_zoomed.subsurface(crop_rect).copy()

    surface.blit(background_cache[cache_key], (viewport[0], viewport[1]))
    return True


def item_eh_chao_base(item):
    return isinstance(item, dict) and item.get("skip_on_background", False)


def tela_para_mundo(pos_tela, camera, viewport):
    vx0, vy0, vx1, vy1 = viewport
    if not (vx0 <= pos_tela[0] <= vx1 and vy0 <= pos_tela[1] <= vy1):
        return None

    vw = vx1 - vx0
    vh = vy1 - vy0
    if vw <= 0 or vh <= 0:
        return None

    wx0, wy0, wx1, wy1 = camera
    t_x = (pos_tela[0] - vx0) / vw
    t_y = (pos_tela[1] - vy0) / vh
    world_x = int(wx0 + t_x * (wx1 - wx0))
    world_y = int(wy0 + t_y * (wy1 - wy0))
    return world_x, world_y


# ─── LOOP PRINCIPAL ────────────────────────────────────────────────────────
fonte = pygame.font.SysFont(None, 22)
dt = 0.0
running = True
last_input_dir = "right"
debug_clip = False
debug_pos = False
pick_inicio = None
ultimo_snippet = ""
last_room_for_music = room_manager.current_room
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_a, pygame.K_LEFT):
                last_input_dir = "left"
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                last_input_dir = "right"
            elif event.key in (pygame.K_w, pygame.K_UP):
                last_input_dir = "up"
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                last_input_dir = "down"
            elif event.key == pygame.K_v:
                debug_clip = not debug_clip
            elif event.key == pygame.K_g:
                debug_pos = not debug_pos
                pick_inicio = None
            elif event.key == pygame.K_c and debug_pos:
                pick_inicio = None
                ultimo_snippet = ""

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and debug_pos:
            mouse_world = tela_para_mundo(event.pos, camera, viewport)
            if mouse_world is not None:
                if pick_inicio is None:
                    pick_inicio = mouse_world
                else:
                    x0, y0 = pick_inicio
                    x1, y1 = mouse_world
                    rx = min(x0, x1)
                    ry = min(y0, y1)
                    rw = abs(x1 - x0)
                    rh = abs(y1 - y0)
                    ultimo_snippet = f"sc({rx}, {ry}, {rw}, {rh}),"
                    print("[collider]", ultimo_snippet)
                    pick_inicio = None

    # ── Input ──────────────────────────────────────────────────────────────
    keys = pygame.key.get_pressed()
    dx = dy = 0
    left_pressed = keys[pygame.K_a] or keys[pygame.K_LEFT]
    right_pressed = keys[pygame.K_d] or keys[pygame.K_RIGHT]
    up_pressed = keys[pygame.K_w] or keys[pygame.K_UP]
    down_pressed = keys[pygame.K_s] or keys[pygame.K_DOWN]

    # Resolve horizontal com prioridade para o ultimo input quando ha conflito.
    if left_pressed and not right_pressed:
        dx = -1
    elif right_pressed and not left_pressed:
        dx = 1
    elif left_pressed and right_pressed:
        if last_input_dir == "left":
            dx = -1
        elif last_input_dir == "right":
            dx = 1

    # Resolve vertical com prioridade para o ultimo input quando ha conflito.
    if up_pressed and not down_pressed:
        dy = -1
    elif down_pressed and not up_pressed:
        dy = 1
    elif up_pressed and down_pressed:
        if last_input_dir == "up":
            dy = -1
        elif last_input_dir == "down":
            dy = 1

    # Bloqueia diagonal: se dois eixos estiverem ativos, vence o eixo do ultimo input.
    if dx != 0 and dy != 0:
        if last_input_dir in ("left", "right"):
            dy = 0
        else:
            dx = 0

    dados_room = room_manager.get_room()
    player.mover(dx, dy, dt, dados_room["colliders"])

    room_manager.update(player, dt)

    # Evento especifico: ao trocar de sala, troca a musica.
    current_room = room_manager.current_room
    if current_room != last_room_for_music:
        faixa = MUSICA_POR_SALA.get(current_room)
        if faixa:
            trocar_musica_se_existir(
                file_name=faixa,
                fallback_to_first=True,
                volume=0.5,
                fade_ms=500,
            )
        last_room_for_music = current_room

    # Interações modulares (mensagem no mapa ou folha de papel)
    dados_room = room_manager.get_room()
    player_rect = player.collider.get_rect_from_center(player.x, player.y)
    interaction_manager.update(keys, player_rect, dados_room.get("interactables", []), dt)

    # ── Render ─────────────────────────────────────────────────────────────
    screen.fill((10, 10, 10))

    dados_room = room_manager.get_room()
    room_has_background = desenhar_background_da_sala(screen, dados_room, camera, viewport)
    for item in dados_room["poligonos"]:
        if room_has_background and item_eh_chao_base(item):
            continue
        desenhar_item(screen, item, camera, debug_clip)

    for item in dados_room["portas_visuais"]:
        desenhar_item(screen, item, camera, debug_clip)

    # Player (losango com textura)
    player.draw(screen, camera, viewport, textura)

    # HUD: sala atual + posição
    texto = fonte.render(
        f"sala: {room_manager.current_room} | pos: ({int(player.x)}, {int(player.y)}) | WASD | V: clip debug {'on' if debug_clip else 'off'}",
        True,
        (200, 200, 200),
    )
    screen.blit(texto, (10, 10))

    if debug_pos:
        mouse_world = tela_para_mundo(pygame.mouse.get_pos(), camera, viewport)
        if mouse_world is None:
            pos_text = "mouse mundo: fora da viewport"
        else:
            pos_text = f"mouse mundo: ({mouse_world[0]}, {mouse_world[1]})"

        texto_debug = fonte.render(
            f"G: modo medidor on | clique 2 pontos para retangulo | C: limpar | {pos_text}",
            True,
            (255, 235, 120),
        )
        screen.blit(texto_debug, (10, 34))

        if ultimo_snippet:
            texto_snippet = fonte.render(
                f"ultimo collider: {ultimo_snippet}",
                True,
                (160, 255, 180),
            )
            screen.blit(texto_snippet, (10, 58))

        if pick_inicio is not None:
            mouse_world = tela_para_mundo(pygame.mouse.get_pos(), camera, viewport)
            if mouse_world is not None:
                x0, y0 = pick_inicio
                x1, y1 = mouse_world
                preview = [
                    (min(x0, x1), min(y0, y1)),
                    (max(x0, x1), min(y0, y1)),
                    (max(x0, x1), max(y0, y1)),
                    (min(x0, x1), max(y0, y1)),
                ]
                preview_tela = transformar_pontos(preview, camera, viewport)
                desenhar_poligono(screen, preview_tela, (255, 255, 0))

    interaction_manager.draw(screen, camera, viewport)

    pygame.display.flip()
    dt = clock.tick(60) / 1000.0

parar_musica()
pygame.quit()
sys.exit()
