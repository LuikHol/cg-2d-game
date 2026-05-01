import pygame
import sys
from configs.game_config import (
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

from objects.player_object import ObjetoJogador
from objects.interaction_manager import GerenciadorInteracao
from objects.room_manager import RoomManager
from world.rooms import construir_salas
from objects.decoracoes import desenhar_coroa_estatua
from render.sala_renderer import desenhar_sala, desenhar_foreground, desenhar_background_com_tiling, desenhar_item
from render.iluminacao import desenhar_iluminacao
from render.viewport import transformar_pontos, world_to_viewport, atualizar_camera_player_follow
from render.poligono import desenhar_poligono
from objects.inventario import Inventario
from musica_loop import iniciar_musica_loop, trocar_musica_se_existir, parar_musica
from menu.inventory_hud import InventarioHUD

class TestGameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption(TITULO_JANELA)
        self.clock = pygame.time.Clock()

        try:
            self.textura = pygame.image.load(CAMINHO_TEXTURA)
        except FileNotFoundError:
            self.textura = None

        iniciar_musica_loop(volume=VOLUME_MUSICA)

        rooms = construir_salas()
        self.room_manager = RoomManager(rooms, SALA_INICIAL)
        self.player = ObjetoJogador(JOGADOR_INICIO_X, JOGADOR_INICIO_Y)
        self.inventario = Inventario()
        self.gerenciador_interacao = GerenciadorInteracao(
            textura_papel=self.textura,
            inventario=self.inventario,
        )

        self.camera = (0, 0, LARGURA_MUNDO, ALTURA_MUNDO)
        self.viewport = (
            MARGEM_VIEWPORT,
            MARGEM_VIEWPORT,
            LARGURA_TELA - MARGEM_VIEWPORT,
            ALTURA_TELA - MARGEM_VIEWPORT,
        )
        self.textures = {"paper": self.textura}

        self.fonte = pygame.font.SysFont(None, TAMANHO_FONTE_HUD)
        self.inventario_hud = InventarioHUD(self.fonte)

        self.dt = 0.0
        self.running = True
        self.last_input_dir = "right"
        self.debug = {
            "clip": False,
            "pos": False,
            "light": True,
            "pick_inicio": None,
            "ultimo_snippet": "",
        }
        self.last_room_for_music = self.room_manager.current_room

    def tela_para_mundo(self, pos_tela):
        vx0, vy0, vx1, vy1 = self.viewport
        if not (vx0 <= pos_tela[0] <= vx1 and vy0 <= pos_tela[1] <= vy1):
            return None

        vw = vx1 - vx0
        vh = vy1 - vy0
        if vw <= 0 or vh <= 0:
            return None

        wx0, wy0, wx1, wy1 = self.camera
        t_x = (pos_tela[0] - vx0) / vw
        t_y = (pos_tela[1] - vy0) / vh
        return int(wx0 + t_x * (wx1 - wx0)), int(wy0 + t_y * (wy1 - wy0))

    def processar_input(self, keys):
        dx = dy = 0
        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        up = keys[pygame.K_w] or keys[pygame.K_UP]
        down = keys[pygame.K_s] or keys[pygame.K_DOWN]

        if left and not right:
            dx = -1
        elif right and not left:
            dx = 1
        elif left and right:
            dx = -1 if self.last_input_dir == "left" else (1 if self.last_input_dir == "right" else 0)

        if up and not down:
            dy = -1
        elif down and not up:
            dy = 1
        elif up and down:
            dy = -1 if self.last_input_dir == "up" else (1 if self.last_input_dir == "down" else 0)

        if dx != 0 and dy != 0:
            if self.last_input_dir in ("left", "right"):
                dy = 0
            else:
                dx = 0

        return dx, dy

    def desenhar_hud(self):
        texto = self.fonte.render(
            f"sala: {self.room_manager.current_room} | pos: ({int(self.player.x)}, {int(self.player.y)}) | WASD | V: clip {'on' if self.debug['clip'] else 'off'} | L: luz {'on' if self.debug['light'] else 'off'}",
            True,
            (200, 200, 200),
        )
        self.screen.blit(texto, (10, 10))

        itens = self.inventario.listar()
        if itens:
            largura_tela = self.screen.get_width()
            texto_inv = self.fonte.render(f"Inventario: {', '.join(itens)}", True, (255, 220, 80))
            self.screen.blit(texto_inv, (largura_tela - texto_inv.get_width() - 10, 10))

        if not self.debug["pos"]:
            return

        mouse_world = self.tela_para_mundo(pygame.mouse.get_pos())
        pos_text = f"mouse mundo: ({mouse_world[0]}, {mouse_world[1]})" if mouse_world else "mouse mundo: fora da viewport"
        self.screen.blit(
            self.fonte.render(
                f"G: modo medidor on | clique 2 pontos para retangulo | C: limpar | {pos_text}",
                True,
                (255, 235, 120),
            ),
            (10, 34),
        )

        if self.debug["ultimo_snippet"]:
            self.screen.blit(
                self.fonte.render(f"ultimo collider: {self.debug['ultimo_snippet']}", True, (160, 255, 180)),
                (10, 58),
            )

        if self.debug["pick_inicio"] is not None and mouse_world is not None:
            x0, y0 = self.debug["pick_inicio"]
            x1, y1 = mouse_world
            preview = [
                (min(x0, x1), min(y0, y1)),
                (max(x0, x1), min(y0, y1)),
                (max(x0, x1), max(y0, y1)),
                (min(x0, x1), max(y0, y1)),
            ]
            desenhar_poligono(self.screen, transformar_pontos(preview, self.camera, self.viewport), (255, 255, 0))

    def processar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    self.last_input_dir = "left"
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    self.last_input_dir = "right"
                elif event.key in (pygame.K_w, pygame.K_UP):
                    self.last_input_dir = "up"
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    self.last_input_dir = "down"
                elif event.key == pygame.K_v:
                    self.debug["clip"] = not self.debug["clip"]
                elif event.key == pygame.K_g:
                    self.debug["pos"] = not self.debug["pos"]
                    self.debug["pick_inicio"] = None
                elif event.key == pygame.K_c and self.debug["pos"]:
                    self.debug["pick_inicio"] = None
                    self.debug["ultimo_snippet"] = ""
                elif event.key == pygame.K_l:
                    self.debug["light"] = not self.debug["light"]
                elif event.key == pygame.K_r:
                    self.inventario_hud.alternar()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.debug["pos"]:
                mouse_world = self.tela_para_mundo(event.pos)
                if mouse_world is None:
                    continue

                if self.debug["pick_inicio"] is None:
                    self.debug["pick_inicio"] = mouse_world
                else:
                    x0, y0 = self.debug["pick_inicio"]
                    x1, y1 = mouse_world
                    rx, ry = min(x0, x1), min(y0, y1)
                    rw, rh = abs(x1 - x0), abs(y1 - y0)
                    self.debug["ultimo_snippet"] = f"sc({rx}, {ry}, {rw}, {rh}),"
                    print("[collider]", self.debug["ultimo_snippet"])
                    self.debug["pick_inicio"] = None

    def atualizar_logica(self):
        keys = pygame.key.get_pressed()
        dx, dy = self.processar_input(keys)

        dados_room = self.room_manager.get_room()
        self.player.mover(dx, dy, self.dt, dados_room["colliders"])
        self.room_manager.update(self.player, self.dt)

        # Camera segue somente salas que definem bounds (ex.: corredor horizontal).
        dados_room = self.room_manager.get_room()
        camera_bounds = dados_room.get("camera_bounds")
        if camera_bounds:
            self.camera = atualizar_camera_player_follow(
                self.player.x,
                self.player.y,
                camera_bounds,
                (
                    dados_room.get("camera_viewport_width", LARGURA_MUNDO),
                    dados_room.get("camera_viewport_height", ALTURA_MUNDO),
                ),
            )
        else:
            self.camera = (0, 0, LARGURA_MUNDO, ALTURA_MUNDO)

        current_room = self.room_manager.current_room
        if current_room != self.last_room_for_music:
            faixa = MUSICA_POR_SALA.get(current_room)
            if faixa:
                trocar_musica_se_existir(
                    file_name=faixa,
                    fallback_to_first=True,
                    volume=VOLUME_MUSICA,
                    fade_ms=500,
                )
            self.last_room_for_music = current_room

        dados_room = self.room_manager.get_room()
        player_rect = self.player.collider.get_rect_from_center(self.player.x, self.player.y)
        self.gerenciador_interacao.atualizar(
            keys,
            player_rect,
            dados_room.get("interactables", []),
            self.dt,
        )

    def renderizar(self):
        self.screen.fill((10, 10, 10))
        dados_room = self.room_manager.get_room()

        # Corredor usa tiling + poligonos de parede.
        if dados_room.get("nome") == "corredor":
            desenhar_background_com_tiling(self.screen, dados_room, self.camera, self.viewport)
            for item in dados_room["poligonos"]:
                desenhar_item(self.screen, item, self.camera, self.viewport, self.textures, self.debug["clip"])
            for item in dados_room["portas_visuais"]:
                desenhar_item(self.screen, item, self.camera, self.viewport, self.textures, self.debug["clip"])
        else:
            desenhar_sala(self.screen, dados_room, self.camera, self.viewport, self.textures, self.debug["clip"])

        self.player.draw(self.screen, self.camera, self.viewport, self.textura)
        desenhar_foreground(self.screen, dados_room, self.camera, self.viewport, self.textures, self.debug["clip"])
        if self.debug["light"]:
            desenhar_iluminacao(self.screen, self.player, dados_room, self.camera, self.viewport)

        if self.room_manager.current_room == "sala_1":
            desenhar_coroa_estatua(self.screen, self.camera, self.viewport, self.inventario)

        self.gerenciador_interacao.desenhar(self.screen, self.camera, self.viewport)
        self.desenhar_hud()
        self.inventario_hud.desenhar_hint(self.screen, self.viewport)
        self.inventario_hud.desenhar(self.screen, self.inventario, self.viewport)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.processar_eventos()
            self.atualizar_logica()
            self.renderizar()
            self.dt = self.clock.tick(60) / 1000.0

        parar_musica()
        pygame.quit()
        sys.exit()


def main():
    app = TestGameApp()
    app.run()


if __name__ == "__main__":
    main()
