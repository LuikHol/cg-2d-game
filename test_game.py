import pygame
import sys
import math
from pathlib import Path
from configs.game_config import (
    ALFA_ESCURIDAO_AMBIENTE,
    ALTURA_MUNDO,
    ALTURA_TELA,
    CAMINHO_TEXTURA,
    JOGADOR_INICIO_X,
    JOGADOR_INICIO_Y,
    LARGURA_MUNDO,
    LARGURA_TELA,
    MARGEM_VIEWPORT,
    MUSICA_POR_SALA,
    SALA_INICIAL,
    TAMANHO_FONTE_HUD,
    TITULO_JANELA,
    VOLUME_MUSICA,
)
from objects.player_object import PlayerObject
from objects.interaction_manager import InteractionManager
from objects.room_manager import RoomManager
from world.rooms import build_rooms
from world.decoracoes import desenhar_coroa_estatua
from render.sala_renderer import desenhar_sala, desenhar_foreground
from render.iluminacao import desenhar_iluminacao
from render.viewport import transformar_pontos, world_to_viewport
from render.poligono import desenhar_poligono
from objects.inventario import Inventario
from musica_loop import iniciar_musica_loop, trocar_musica_se_existir, parar_musica

# --- INICIALIZACAO ---------------------------------------------------------
pygame.init()
screen = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption(TITULO_JANELA)
clock = pygame.time.Clock()

try:
    textura = pygame.image.load(CAMINHO_TEXTURA)
except FileNotFoundError:
    textura = None

iniciar_musica_loop(volume=VOLUME_MUSICA)

rooms = build_rooms()
room_manager = RoomManager(rooms, SALA_INICIAL)
player = PlayerObject(JOGADOR_INICIO_X, JOGADOR_INICIO_Y)
inventario = Inventario()
interaction_manager = InteractionManager(paper_texture=textura, inventario=inventario)

camera   = (0, 0, LARGURA_MUNDO, ALTURA_MUNDO)
viewport = (MARGEM_VIEWPORT, MARGEM_VIEWPORT, LARGURA_TELA - MARGEM_VIEWPORT, ALTURA_TELA - MARGEM_VIEWPORT)
textures = {"paper": textura}


# --- UTILITARIOS -----------------------------------------------------------
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
    return int(wx0 + t_x * (wx1 - wx0)), int(wy0 + t_y * (wy1 - wy0))


def processar_input(keys, last_input_dir):
    dx = dy = 0
    left  = keys[pygame.K_a] or keys[pygame.K_LEFT]
    right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
    up    = keys[pygame.K_w] or keys[pygame.K_UP]
    down  = keys[pygame.K_s] or keys[pygame.K_DOWN]

    if left and not right:
        dx = -1
    elif right and not left:
        dx = 1
    elif left and right:
        dx = -1 if last_input_dir == "left" else (1 if last_input_dir == "right" else 0)

    if up and not down:
        dy = -1
    elif down and not up:
        dy = 1
    elif up and down:
        dy = -1 if last_input_dir == "up" else (1 if last_input_dir == "down" else 0)

    if dx != 0 and dy != 0:
        if last_input_dir in ("left", "right"):
            dy = 0
        else:
            dx = 0

    return dx, dy


def desenhar_hud(surface, fonte, room_manager, player, debug_clip, debug_light,
                 debug_pos, pick_inicio, ultimo_snippet, camera, viewport, inventario=None):
    texto = fonte.render(
        f"sala: {room_manager.current_room} | pos: ({int(player.x)}, {int(player.y)}) | WASD | V: clip {'on' if debug_clip else 'off'} | L: luz {'on' if debug_light else 'off'}",
        True, (200, 200, 200),
    )
    surface.blit(texto, (10, 10))

    # Inventario no canto superior direito
    if inventario:
        itens = inventario.listar()
        if itens:
            largura_tela = surface.get_width()
            texto_inv = fonte.render(f"Inventario: {', '.join(itens)}", True, (255, 220, 80))
            surface.blit(texto_inv, (largura_tela - texto_inv.get_width() - 10, 10))

    if not debug_pos:
        return

    mouse_world = tela_para_mundo(pygame.mouse.get_pos(), camera, viewport)
    pos_text = f"mouse mundo: ({mouse_world[0]}, {mouse_world[1]})" if mouse_world else "mouse mundo: fora da viewport"
    surface.blit(fonte.render(f"G: modo medidor on | clique 2 pontos para retangulo | C: limpar | {pos_text}", True, (255, 235, 120)), (10, 34))

    if ultimo_snippet:
        surface.blit(fonte.render(f"ultimo collider: {ultimo_snippet}", True, (160, 255, 180)), (10, 58))

    if pick_inicio is not None and mouse_world is not None:
        x0, y0 = pick_inicio
        x1, y1 = mouse_world
        preview = [(min(x0,x1),min(y0,y1)), (max(x0,x1),min(y0,y1)), (max(x0,x1),max(y0,y1)), (min(x0,x1),max(y0,y1))]
        desenhar_poligono(surface, transformar_pontos(preview, camera, viewport), (255, 255, 0))


# --- LOOP PRINCIPAL --------------------------------------------------------
fonte = pygame.font.SysFont(None, TAMANHO_FONTE_HUD)
dt = 0.0
running = True
last_input_dir = "right"
debug_clip  = False
debug_pos   = False
debug_light = True
pick_inicio    = None
ultimo_snippet = ""
last_room_for_music = room_manager.current_room

while running:
    # -- Eventos ------------------------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key in (pygame.K_a, pygame.K_LEFT):
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
                debug_pos  = not debug_pos
                pick_inicio = None
            elif event.key == pygame.K_c and debug_pos:
                pick_inicio    = None
                ultimo_snippet = ""
            elif event.key == pygame.K_l:
                debug_light = not debug_light

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and debug_pos:
            mouse_world = tela_para_mundo(event.pos, camera, viewport)
            if mouse_world is not None:
                if pick_inicio is None:
                    pick_inicio = mouse_world
                else:
                    x0, y0 = pick_inicio
                    x1, y1 = mouse_world
                    rx, ry = min(x0, x1), min(y0, y1)
                    rw, rh = abs(x1 - x0), abs(y1 - y0)
                    ultimo_snippet = f"sc({rx}, {ry}, {rw}, {rh}),"
                    print("[collider]", ultimo_snippet)
                    pick_inicio = None

    # -- Logica -------------------------------------------------------------
    keys = pygame.key.get_pressed()
    dx, dy = processar_input(keys, last_input_dir)

    dados_room = room_manager.get_room()
    player.mover(dx, dy, dt, dados_room["colliders"])
    room_manager.update(player, dt)

    current_room = room_manager.current_room
    if current_room != last_room_for_music:
        faixa = MUSICA_POR_SALA.get(current_room)
        if faixa:
            trocar_musica_se_existir(file_name=faixa, fallback_to_first=True, volume=VOLUME_MUSICA, fade_ms=500)
        last_room_for_music = current_room

    dados_room = room_manager.get_room()
    player_rect = player.collider.get_rect_from_center(player.x, player.y)
    interaction_manager.update(keys, player_rect, dados_room.get("interactables", []), dt)

    # -- Render -------------------------------------------------------------
    screen.fill((10, 10, 10))

    dados_room = room_manager.get_room()
    desenhar_sala(screen, dados_room, camera, viewport, textures, debug_clip)
    desenhar_iluminacao(screen, player, dados_room, camera, viewport)
    player.draw(screen, camera, viewport, textura)
    desenhar_foreground(screen, dados_room, camera, viewport, textures, debug_clip)

    if room_manager.current_room == "sala_1":
        desenhar_coroa_estatua(screen, camera, viewport, inventario)

    desenhar_hud(screen, fonte, room_manager, player, debug_clip, debug_light,
                 debug_pos, pick_inicio, ultimo_snippet, camera, viewport, inventario)
    interaction_manager.draw(screen, camera, viewport)

    pygame.display.flip()
    dt = clock.tick(60) / 1000.0

parar_musica()
pygame.quit()
sys.exit()
