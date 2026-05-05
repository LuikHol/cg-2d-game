import pygame
import sys
from efeitos_sonoros import tocar_efeito_se_existir
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
from objects.perseguidora_object import ObjetoPerseguidora
from world.rooms import construir_salas
from objects.decoracoes import desenhar_coroa_estatua, desenhar_itens_tapete, desenhar_livro_coala, desenhar_pote_urso
from render.sala_renderer import desenhar_sala, desenhar_foreground, desenhar_background_com_tiling, desenhar_item
from render.iluminacao import desenhar_iluminacao
from render.viewport import transformar_pontos, atualizar_camera_player_follow
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
        self.perseguidora = None
        self.perseguidora_ativa = False
        self.alerta_perseguicao_tempo = 0.0
        self.tempo_para_spawn_perseguidora = 5.0
        self.tempo_andando_sala2 = 0.0
        self.perseguidora_agendada = False
        self.ultima_posicao_player_sala2 = (float(self.player.x), float(self.player.y))

        self.camera = (0, 0, LARGURA_MUNDO, ALTURA_MUNDO)
        self.default_viewport_margin = MARGEM_VIEWPORT
        self.viewport = (0, 0, LARGURA_TELA, ALTURA_TELA)
        self.textures = {"paper": self.textura}

        self.fonte = pygame.font.SysFont(None, TAMANHO_FONTE_HUD)
        self.inventario_hud = InventarioHUD(self.fonte)

        self.dt = 0.0
        self.running = True
        self.last_input_dir = "right"
        # Debug rapido de colisao (medidor de retangulo em coordenadas de mundo).
        self.debug_colisao = False
        self.pick_inicio = None
        self.ultimo_snippet = ""
        self.last_room_for_music = self.room_manager.current_room
        self.atualizar_viewport_por_sala(self.room_manager.get_room())

        # Sala 2 começa trancada até o puzzle do tapete ser resolvido.
        self.room_manager.lock_room("sala_2")
        self._sala2_desbloqueada = False

    def atualizar_viewport_por_sala(self, dados_room):
        if dados_room.get("viewport_fullscreen", False):
            self.viewport = (0, 0, LARGURA_TELA, ALTURA_TELA)
            return

        margem = int(dados_room.get("viewport_margin", self.default_viewport_margin))
        margem_max = max(0, (min(LARGURA_TELA, ALTURA_TELA) // 2) - 1)
        margem = max(0, min(margem, margem_max))
        self.viewport = (
            margem,
            margem,
            LARGURA_TELA - margem,
            ALTURA_TELA - margem,
        )

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

    def _spawn_perseguidora_atras_do_player(self, dados_room):
        """Cria a perseguidora atras do jogador."""
        direcoes = {
            "left": (-1.0, 0.0),
            "right": (1.0, 0.0),
            "up": (0.0, -1.0),
            "down": (0.0, 1.0),
        }
        frente = direcoes.get(self.player.direcao, (1.0, 0.0))
        atras = (-frente[0], -frente[1])

        origem_x = self.player.x
        origem_y = self.player.y
        distancias = [260.0, 320.0, 380.0, 220.0]

        # Tenta alguns offsets ate achar uma posicao valida sem colisao com paredes.
        spawn_x = origem_x + (atras[0] * distancias[0])
        spawn_y = origem_y + (atras[1] * distancias[0])
        tamanho_colisor = max(24.0, self.player.tamanho * 1.5)

        for dist in distancias:
            candidato_x = origem_x + (atras[0] * dist)
            candidato_y = origem_y + (atras[1] * dist)
            candidato = pygame.Rect(
                int(round(candidato_x - tamanho_colisor / 2.0)),
                int(round(candidato_y - tamanho_colisor / 2.0)),
                int(round(tamanho_colisor)),
                int(round(tamanho_colisor)),
            )
            if not any(candidato.colliderect(col.get_rect()) for col in dados_room.get("colliders", [])):
                spawn_x = candidato_x
                spawn_y = candidato_y
                break

        bounds = dados_room.get("camera_bounds", (0, 0, LARGURA_MUNDO, ALTURA_MUNDO))
        bx0, by0, bx1, by1 = bounds
        spawn_x = max(float(bx0 + 24), min(float(spawn_x), float(bx1 - 24)))
        spawn_y = max(float(by0 + 24), min(float(spawn_y), float(by1 - 24)))

        self.perseguidora = ObjetoPerseguidora(spawn_x, spawn_y, tamanho=max(20, self.player.tamanho + 2))
        self.perseguidora_ativa = True
        self.perseguidora_agendada = False
        self.alerta_perseguicao_tempo = 3.0

    def desenhar_hud(self):
        texto = self.fonte.render(
            f"sala: {self.room_manager.current_room} | pos: ({int(self.player.x)}, {int(self.player.y)}) | WASD",
            True,
            (200, 200, 200),
        )
        self.screen.blit(texto, (10, 10))

        itens = self.inventario.listar()
        if itens:
            largura_tela = self.screen.get_width()
            texto_inv = self.fonte.render(f"Inventario: {', '.join(itens)}", True, (255, 220, 80))
            self.screen.blit(texto_inv, (largura_tela - texto_inv.get_width() - 10, 10))

        if self.perseguidora_ativa and self.room_manager.current_room == "sala_2":
            texto_alerta = "FUJA! A perseguidora esta te seguindo."
            if self.alerta_perseguicao_tempo > 0.0:
                texto_alerta = "PERIGO! Ela apareceu atras de voce!"
            alerta = self.fonte.render(texto_alerta, True, (255, 92, 92))
            self.screen.blit(alerta, (10, 34))
        elif self.perseguidora_agendada and self.room_manager.current_room == "sala_2":
            restante = max(0.0, self.tempo_para_spawn_perseguidora - self.tempo_andando_sala2)
            texto_alerta = f"Sinto algo se aproximando... continue correndo ({restante:.1f}s)"
            alerta = self.fonte.render(texto_alerta, True, (255, 190, 110))
            self.screen.blit(alerta, (10, 34))

        if self.debug_colisao:
            mouse_world = self.tela_para_mundo(pygame.mouse.get_pos())
            pos_text = f"mouse mundo: ({mouse_world[0]}, {mouse_world[1]})" if mouse_world else "mouse mundo: fora da viewport"
            linha = self.fonte.render(
                f"G: medidor on | clique 2 pontos | C: limpar | {pos_text}",
                True,
                (255, 235, 120),
            )
            self.screen.blit(linha, (10, 58))

            if self.ultimo_snippet:
                self.screen.blit(
                    self.fonte.render(f"ultimo collider: {self.ultimo_snippet}", True, (160, 255, 180)),
                    (10, 82),
                )

            if self.pick_inicio is not None and mouse_world is not None:
                x0, y0 = self.pick_inicio
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
                elif event.key == pygame.K_g:
                    self.debug_colisao = not self.debug_colisao
                    if not self.debug_colisao:
                        self.pick_inicio = None
                elif event.key == pygame.K_c and self.debug_colisao:
                    self.pick_inicio = None
                    self.ultimo_snippet = ""
                elif event.key == pygame.K_r:
                    self.inventario_hud.alternar()
                elif event.key == pygame.K_w and self.inventario_hud.aberto:
                    self.inventario_hud.mover_selecao(-1, self.inventario)
                elif event.key == pygame.K_s and self.inventario_hud.aberto:
                    self.inventario_hud.mover_selecao(1, self.inventario)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.debug_colisao:
                mouse_world = self.tela_para_mundo(event.pos)
                if mouse_world is None:
                    continue

                if self.pick_inicio is None:
                    self.pick_inicio = mouse_world
                else:
                    x0, y0 = self.pick_inicio
                    x1, y1 = mouse_world
                    rx, ry = min(x0, x1), min(y0, y1)
                    rw, rh = abs(x1 - x0), abs(y1 - y0)
                    self.ultimo_snippet = f"sc({rx}, {ry}, {rw}, {rh}),"
                    print("[collider]", self.ultimo_snippet)
                    self.pick_inicio = None

    def atualizar_logica(self):
        keys = pygame.key.get_pressed()
        dx, dy = self.processar_input(keys)

        # Atualiza item em mao baseado na selecao do HUD.
        self.gerenciador_interacao.item_em_mao = self.inventario_hud.get_item_selecionado(self.inventario)

        dados_room = self.room_manager.get_room()
        
        if self.gerenciador_interacao.papel_aberto:
            dx, dy = 0, 0
        self.player.mover(dx, dy, self.dt, dados_room["colliders"])
        transicao = self.room_manager.update(self.player, self.dt)

        # Verifica se puzzle foi resolvido e desbloqueia sala 2.
        if not self._sala2_desbloqueada:
            from objects import puzzle_state
            if puzzle_state.tapete_resolvido():
                tocar_efeito_se_existir("puzzle_resolvido.mp3")
                self.gerenciador_interacao.mensagem_mundo = "Uma porta foi destrancada."
                self.gerenciador_interacao.pos_mensagem_mundo = (int(self.player.x), int(self.player.y) - 40)
                self.gerenciador_interacao.tempo_mensagem_mundo = 3.0
                self.room_manager.unlock_room("sala_2")
                self._sala2_desbloqueada = True
                # Remove o collider de porta do corredor.
                corredor = self.room_manager.rooms.get("corredor")
                if corredor:
                    corredor["colliders"] = [
                        c for c in corredor["colliders"]
                        if not (c.rect.x == 1588 and c.rect.y == 350 and c.rect.width == 12 and c.rect.height == 80)
                    ]

        # Porta bloqueada: avisa quando o jogador toca o collider da porta sala_2.
        if not self._sala2_desbloqueada and self.room_manager.current_room == "corredor":
            porta_rect = pygame.Rect(1588, 350, 12, 80)
            player_rect = self.player.collider.get_rect_from_center(self.player.x, self.player.y)
            expanded = porta_rect.inflate(16, 16)
            if player_rect.colliderect(expanded) and self.gerenciador_interacao.tempo_mensagem_mundo <= 0:
                self.gerenciador_interacao.mensagem_mundo = "A porta esta trancada."
                self.gerenciador_interacao.pos_mensagem_mundo = (int(self.player.x), int(self.player.y) - 40)
                self.gerenciador_interacao.tempo_mensagem_mundo = 2.0

        if transicao is not None and transicao.get("blocked"):
            transicao = None

        if transicao is not None:
            if transicao["target"] == "sala_2":
                self.perseguidora = None
                self.perseguidora_ativa = False
                self.perseguidora_agendada = True
                self.tempo_andando_sala2 = 0.0
                self.ultima_posicao_player_sala2 = (float(self.player.x), float(self.player.y))
            elif transicao["source"] == "sala_2":
                self.perseguidora = None
                self.perseguidora_ativa = False
                self.perseguidora_agendada = False
                self.tempo_andando_sala2 = 0.0

        # Camera segue somente salas que definem bounds (ex.: corredor horizontal).
        dados_room = self.room_manager.get_room()
        self.atualizar_viewport_por_sala(dados_room)
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
        if self.room_manager.current_room == "sala_2" and not self.perseguidora_ativa and not self.perseguidora_agendada:
            # Fallback para casos em que o jogador inicia/retorna na sala_2 sem evento de transicao.
            self.perseguidora_agendada = True
            self.tempo_andando_sala2 = 0.0
            self.ultima_posicao_player_sala2 = (float(self.player.x), float(self.player.y))

        if self.room_manager.current_room == "sala_2" and self.perseguidora_agendada and not self.perseguidora_ativa:
            atual_x = float(self.player.x)
            atual_y = float(self.player.y)
            ultimo_x, ultimo_y = self.ultima_posicao_player_sala2
            desloc = ((atual_x - ultimo_x) ** 2 + (atual_y - ultimo_y) ** 2) ** 0.5
            self.ultima_posicao_player_sala2 = (atual_x, atual_y)

            # Conta tempo somente quando houve deslocamento real.
            if desloc >= 1.0:
                self.tempo_andando_sala2 += self.dt
            if self.tempo_andando_sala2 >= self.tempo_para_spawn_perseguidora:
                self._spawn_perseguidora_atras_do_player(dados_room)

        if self.perseguidora_ativa and self.perseguidora is not None and self.room_manager.current_room == "sala_2":
            self.perseguidora.atualizar(self.player.x, self.player.y, self.dt, dados_room["colliders"])

            player_rect = self.player.collider.get_rect_from_center(self.player.x, self.player.y)
            perseguidora_rect = self.perseguidora.collider.get_rect_from_center(self.perseguidora.x, self.perseguidora.y)
            if player_rect.colliderect(perseguidora_rect):
                # Reposiciona a perseguidora para manter a pressao sem travar o player.
                self._spawn_perseguidora_atras_do_player(dados_room)

        if self.alerta_perseguicao_tempo > 0.0:
            self.alerta_perseguicao_tempo = max(0.0, self.alerta_perseguicao_tempo - self.dt)

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
        if dados_room.get("nome") in ("corredor", "sala_2"):
            desenhar_background_com_tiling(self.screen, dados_room, self.camera, self.viewport)
            for item in dados_room["poligonos"]:
                desenhar_item(self.screen, item, self.camera, self.viewport, self.textures, False)
            for item in dados_room["portas_visuais"]:
                desenhar_item(self.screen, item, self.camera, self.viewport, self.textures, False)
        else:
            desenhar_sala(self.screen, dados_room, self.camera, self.viewport, self.textures, False)

        desenhar_foreground(
            self.screen,
            dados_room,
            self.camera,
            self.viewport,
            self.textures,
            False,
            draw_above_player=False,
        )

        if self.perseguidora_ativa and self.perseguidora is not None and self.room_manager.current_room == "sala_2":
            self.perseguidora.draw(self.screen, self.camera, self.viewport)

        self.player.draw(self.screen, self.camera, self.viewport, self.textura)
        desenhar_foreground(
            self.screen,
            dados_room,
            self.camera,
            self.viewport,
            self.textures,
            False,
            draw_above_player=True,
        )
        desenhar_iluminacao(self.screen, self.player, dados_room, self.camera, self.viewport)

        if self.room_manager.current_room == "corredor":
            desenhar_pote_urso(self.screen, self.camera, self.viewport, self.inventario)

        if self.room_manager.current_room == "sala_1":
            desenhar_coroa_estatua(self.screen, self.camera, self.viewport, self.inventario)

        if self.room_manager.current_room == "biblioteca":
            desenhar_livro_coala(self.screen, self.camera, self.viewport, self.inventario)

        if self.room_manager.current_room == "quarto_rainha":
            desenhar_itens_tapete(self.screen, self.camera, self.viewport)

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
