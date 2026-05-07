import pygame
import sys
from efeitos_sonoros import tocar_efeito_se_existir
from configs.config_jogo import (
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

from objetos.objeto_jogador import ObjetoJogador
from objetos.gerenciador_interacao import GerenciadorInteracao
from objetos.gerenciador_sala import RoomManager
from objetos.objeto_perseguidora import ObjetoPerseguidora
from mundo.construtor_salas import construir_salas
from objetos.decoracoes import desenhar_coroa_estatua, desenhar_itens_tapete, desenhar_livro_coala, desenhar_pote_urso
from render.renderizador_sala import desenhar_sala, desenhar_foreground, desenhar_background_com_tiling, desenhar_item
from render.iluminacao import desenhar_iluminacao
from render.viewport import transformar_pontos, atualizar_camera_player_follow
from render.poligono import desenhar_poligono
from objetos.inventario import Inventario
from musica_loop import iniciar_musica_loop, trocar_musica_se_existir, parar_musica
from menu.hud_inventario import InventarioHUD
from menu.tela_creditos import tela_creditos

class TestGameApp:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption(TITULO_JANELA)
        self.relogio = pygame.time.Clock()

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
        self.margem_viewport_padrao = MARGEM_VIEWPORT
        self.viewport = (0, 0, LARGURA_TELA, ALTURA_TELA)
        self.texturas = {"paper": self.textura}

        self.fonte = pygame.font.SysFont(None, TAMANHO_FONTE_HUD)
        self.inventario_hud = InventarioHUD(self.fonte)

        self.dt = 0.0
        self.rodando = True
        self.last_input_dir = "direita"
        # Debug rapido de colisao (medidor de retangulo em coordenadas de mundo).
        self.debug_colisao = False
        self.pick_inicio = None
        self.ultimo_snippet = ""
        self.last_room_for_music = self.room_manager.current_room
        self.atualizar_viewport_por_sala(self.room_manager.obter_sala())

        # Sala 2 começa trancada até o puzzle do tapete ser resolvido.
        self.room_manager.trancar_sala("sala_2")
        self._sala2_desbloqueada = False
        self.em_creditos = False
        self.em_game_over = False

    def atualizar_viewport_por_sala(self, dados_room):
        if dados_room.get("tela_cheia", False):
            self.viewport = (0, 0, LARGURA_TELA, ALTURA_TELA)
            return

        margem = int(dados_room.get("margem_viewport", self.margem_viewport_padrao))
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
            dx = -1 if self.last_input_dir == "esquerda" else (1 if self.last_input_dir == "direita" else 0)

        if up and not down:
            dy = -1
        elif down and not up:
            dy = 1
        elif up and down:
            dy = -1 if self.last_input_dir == "cima" else (1 if self.last_input_dir == "baixo" else 0)

        if dx != 0 and dy != 0:
            if self.last_input_dir in ("esquerda", "direita"):
                dy = 0
            else:
                dx = 0

        return dx, dy

    def _spawn_perseguidora_atras_do_player(self, dados_room):
        direcoes = {
            "esquerda": (-1.0, 0.0),
            "direita": (1.0, 0.0),
            "cima": (0.0, -1.0),
            "baixo": (0.0, 1.0),
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
            if not any(candidato.colliderect(col.get_rect()) for col in dados_room.get("colisores", [])):
                spawn_x = candidato_x
                spawn_y = candidato_y
                break

        bounds = dados_room.get("limites_camera", (0, 0, LARGURA_MUNDO, ALTURA_MUNDO))
        bx0, by0, bx1, by1 = bounds
        spawn_x = max(float(bx0 + 24), min(float(spawn_x), float(bx1 - 24)))
        spawn_y = max(float(by0 + 24), min(float(spawn_y), float(by1 - 24)))

        self.perseguidora = ObjetoPerseguidora(spawn_x, spawn_y, tamanho=max(20, self.player.tamanho + 2))
        self.perseguidora_ativa = True
        self.perseguidora_agendada = False
        self.alerta_perseguicao_tempo = 3.0

    def _ativar_game_over(self):
        self.em_game_over = True
        self.perseguidora = None
        self.perseguidora_ativa = False
        self.perseguidora_agendada = False
        self.tempo_andando_sala2 = 0.0
        self.alerta_perseguicao_tempo = 0.0

    def _reiniciar_antes_da_perseguicao(self):
        self.room_manager.current_room = "corredor"
        self.player.x = 1500.0
        self.player.y = 390.0
        self.perseguidora = None
        self.perseguidora_ativa = False
        self.perseguidora_agendada = False
        self.tempo_andando_sala2 = 0.0
        self.alerta_perseguicao_tempo = 0.0
        self.ultima_posicao_player_sala2 = (float(self.player.x), float(self.player.y))
        self.gerenciador_interacao.papel_aberto = None
        self.inventario_hud.aberto = False
        self.em_game_over = False

        dados_room = self.room_manager.obter_sala()
        self.atualizar_viewport_por_sala(dados_room)
        self.camera = (0, 0, LARGURA_MUNDO, ALTURA_MUNDO)

        faixa = MUSICA_POR_SALA.get("corredor")
        if faixa:
            trocar_musica_se_existir(
                file_name=faixa,
                fallback_to_first=True,
                volume=VOLUME_MUSICA,
                fade_ms=350,
            )
        self.last_room_for_music = "corredor"

    def _mostrar_tela_game_over(self):
        fonte_titulo = pygame.font.SysFont(None, 86)
        fonte_sub = pygame.font.SysFont(None, 34)

        while self.rodando and self.em_game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.rodando = False
                    return
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    self._reiniciar_antes_da_perseguicao()
                    return

            self.tela.fill((8, 0, 0))
            titulo = fonte_titulo.render("GAME OVER", True, (240, 70, 70))
            subtitulo = fonte_sub.render("Pressione qualquer botao para continuar", True, (235, 235, 235))
            self.tela.blit(titulo, (LARGURA_TELA // 2 - titulo.get_width() // 2, ALTURA_TELA // 2 - 80))
            self.tela.blit(subtitulo, (LARGURA_TELA // 2 - subtitulo.get_width() // 2, ALTURA_TELA // 2 + 12))
            pygame.display.flip()
            self.relogio.tick(60)

    def desenhar_hud(self):
        texto = self.fonte.render(
            f"sala: {self.room_manager.current_room} | pos: ({int(self.player.x)}, {int(self.player.y)}) | WASD",
            True,
            (200, 200, 200),
        )
        self.tela.blit(texto, (10, 10))

        itens = self.inventario.listar()
        if itens:
            largura_tela = self.tela.get_width()
            texto_inv = self.fonte.render(f"Inventario: {', '.join(itens)}", True, (255, 220, 80))
            self.tela.blit(texto_inv, (largura_tela - texto_inv.get_width() - 10, 10))

        if self.perseguidora_ativa and self.room_manager.current_room == "sala_2":
            texto_alerta = "FUJA! A perseguidora está te seguindo."
            if self.alerta_perseguicao_tempo > 0.0:
                texto_alerta = "PERIGO! Ela apareceu atrás de você!"
            alerta = self.fonte.render(texto_alerta, True, (255, 92, 92))
            self.tela.blit(alerta, (10, 34))
        elif self.perseguidora_agendada and self.room_manager.current_room == "sala_2":
            restante = max(0.0, self.tempo_para_spawn_perseguidora - self.tempo_andando_sala2)
            texto_alerta = f"Sinto algo se aproximando... continue correndo ({restante:.1f}s)"
            alerta = self.fonte.render(texto_alerta, True, (255, 190, 110))
            self.tela.blit(alerta, (10, 34))

        if self.debug_colisao:
            mouse_mundo = self.tela_para_mundo(pygame.mouse.get_pos())
            pos_text = f"mouse mundo: ({mouse_mundo[0]}, {mouse_mundo[1]})" if mouse_mundo else "mouse mundo: fora da viewport"
            linha = self.fonte.render(
                f"G: medidor on | clique 2 pontos | C: limpar | {pos_text}",
                True,
                (255, 235, 120),
            )
            self.tela.blit(linha, (10, 58))

            if self.ultimo_snippet:
                self.tela.blit(
                    self.fonte.render(f"ultimo collider: {self.ultimo_snippet}", True, (160, 255, 180)),
                    (10, 82),
                )

            if self.pick_inicio is not None and mouse_mundo is not None:
                x0, y0 = self.pick_inicio
                x1, y1 = mouse_mundo
                preview = [
                    (min(x0, x1), min(y0, y1)),
                    (max(x0, x1), min(y0, y1)),
                    (max(x0, x1), max(y0, y1)),
                    (min(x0, x1), max(y0, y1)),
                ]
                desenhar_poligono(self.tela, transformar_pontos(preview, self.camera, self.viewport), (255, 255, 0))

    def processar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.rodando = False
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    self.last_input_dir = "esquerda"
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    self.last_input_dir = "direita"
                elif event.key in (pygame.K_w, pygame.K_UP):
                    if self.inventario_hud.aberto:
                        self.inventario_hud.mover_selecao(-1, self.inventario)
                    else:
                        self.last_input_dir = "cima"
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    if self.inventario_hud.aberto:
                        self.inventario_hud.mover_selecao(1, self.inventario)
                    else:
                        self.last_input_dir = "baixo"
                elif event.key == pygame.K_g:
                    self.debug_colisao = not self.debug_colisao
                    if not self.debug_colisao:
                        self.pick_inicio = None
                elif event.key == pygame.K_c and self.debug_colisao:
                    self.pick_inicio = None
                    self.ultimo_snippet = ""
                elif event.key == pygame.K_r:
                    self.inventario_hud.alternar()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.debug_colisao:
                mouse_mundo = self.tela_para_mundo(event.pos)
                if mouse_mundo is None:
                    continue

                if self.pick_inicio is None:
                    self.pick_inicio = mouse_mundo
                else:
                    x0, y0 = self.pick_inicio
                    x1, y1 = mouse_mundo
                    rx, ry = min(x0, x1), min(y0, y1)
                    rw, rh = abs(x1 - x0), abs(y1 - y0)
                    self.ultimo_snippet = f"sc({rx}, {ry}, {rw}, {rh}),"
                    print("[collider]", self.ultimo_snippet)
                    self.pick_inicio = None

    def atualizar_logica(self):
        keys = pygame.key.get_pressed()
        dx, dy = self.processar_input(keys)

        # Atualiza item em mao baseado na selecao do HUD.
        self.gerenciador_interacao.item_em_mao = self.inventario_hud.obter_item_selecionado(self.inventario)

        dados_room = self.room_manager.obter_sala()
        
        if self.gerenciador_interacao.papel_aberto or self.inventario_hud.aberto:
            dx, dy = 0, 0
        self.player.mover(dx, dy, self.dt, dados_room["colisores"])
        transicao = self.room_manager.atualizar(self.player, self.dt)

        # Verifica se puzzle foi resolvido e desbloqueia sala 2.
        if not self._sala2_desbloqueada:
            from objetos import estado_puzzle
            if estado_puzzle.tapete_resolvido():
                tocar_efeito_se_existir("puzzle_resolvido.mp3")
                self.gerenciador_interacao.mensagem_mundo = "Uma porta foi destrancada."
                self.gerenciador_interacao.pos_mensagem_mundo = (int(self.player.x), int(self.player.y) - 40)
                self.gerenciador_interacao.tempo_mensagem_mundo = 3.0
                self.room_manager.destrancar_sala("sala_2")
                self._sala2_desbloqueada = True
                # Remove o collider de porta do corredor.
                corredor = self.room_manager.rooms.get("corredor")
                if corredor:
                    corredor["colisores"] = [
                        c for c in corredor["colisores"]
                        if not (c.rect.x == 1588 and c.rect.y == 350 and c.rect.width == 12 and c.rect.height == 80)
                    ]

        # Porta bloqueada: avisa quando o jogador toca o collider da porta sala_2.
        if not self._sala2_desbloqueada and self.room_manager.current_room == "corredor":
            porta_rect = pygame.Rect(1588, 350, 12, 80)
            player_rect = self.player.collider.obter_rect_do_centro(self.player.x, self.player.y)
            expanded = porta_rect.inflate(16, 16)
            if player_rect.colliderect(expanded) and self.gerenciador_interacao.tempo_mensagem_mundo <= 0:
                self.gerenciador_interacao.mensagem_mundo = "A porta esta trancada."
                self.gerenciador_interacao.pos_mensagem_mundo = (int(self.player.x), int(self.player.y) - 40)
                self.gerenciador_interacao.tempo_mensagem_mundo = 2.0

        if transicao is not None and transicao.get("bloqueado"):
            transicao = None

        if transicao is not None:
            if transicao["destino"] == "creditos":
                self.em_creditos = True
            elif transicao["destino"] == "sala_2":
                self.perseguidora = None
                self.perseguidora_ativa = False
                self.perseguidora_agendada = True
                self.tempo_andando_sala2 = 0.0
                self.ultima_posicao_player_sala2 = (float(self.player.x), float(self.player.y))
            elif transicao["origem"] == "sala_2":
                self.perseguidora = None
                self.perseguidora_ativa = False
                self.perseguidora_agendada = False
                self.tempo_andando_sala2 = 0.0

        # Camera segue somente salas que definem bounds (ex.: corredor horizontal).
        dados_room = self.room_manager.obter_sala()
        self.atualizar_viewport_por_sala(dados_room)
        camera_bounds = dados_room.get("limites_camera")
        if camera_bounds:
            self.camera = atualizar_camera_player_follow(
                self.player.x,
                self.player.y,
                camera_bounds,
                (
                    dados_room.get("largura_camera", LARGURA_MUNDO),
                    dados_room.get("altura_camera", ALTURA_MUNDO),
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

        dados_room = self.room_manager.obter_sala()
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
            self.perseguidora.atualizar(self.player.x, self.player.y, self.dt, dados_room["colisores"])

            player_rect = self.player.collider.obter_rect_do_centro(self.player.x, self.player.y)
            perseguidora_rect = self.perseguidora.collider.obter_rect_do_centro(self.perseguidora.x, self.perseguidora.y)
            if player_rect.colliderect(perseguidora_rect):
                self._ativar_game_over()
                return

        if self.alerta_perseguicao_tempo > 0.0:
            self.alerta_perseguicao_tempo = max(0.0, self.alerta_perseguicao_tempo - self.dt)

        player_rect = self.player.collider.obter_rect_do_centro(self.player.x, self.player.y)
        self.gerenciador_interacao.atualizar(
            keys,
            player_rect,
            dados_room.get("interagiveis", []),
            self.dt,
        )

    def renderizar(self):
        self.tela.fill((10, 10, 10))
        dados_room = self.room_manager.obter_sala()

        # Corredor usa tiling + poligonos de parede.
        if dados_room.get("nome") in ("corredor", "sala_2"):
            desenhar_background_com_tiling(self.tela, dados_room, self.camera, self.viewport)
            for item in dados_room["poligonos"]:
                desenhar_item(self.tela, item, self.camera, self.viewport, self.texturas, False)
            for item in dados_room["portas_visuais"]:
                desenhar_item(self.tela, item, self.camera, self.viewport, self.texturas, False)
        else:
            desenhar_sala(self.tela, dados_room, self.camera, self.viewport, self.texturas, False)

        desenhar_foreground(
            self.tela,
            dados_room,
            self.camera,
            self.viewport,
            self.texturas,
            False,
            draw_above_player=False,
        )

        if self.perseguidora_ativa and self.perseguidora is not None and self.room_manager.current_room == "sala_2":
            self.perseguidora.desenhar(self.tela, self.camera, self.viewport)

        self.player.desenhar(self.tela, self.camera, self.viewport, self.textura)
        desenhar_foreground(
            self.tela,
            dados_room,
            self.camera,
            self.viewport,
            self.texturas,
            False,
            draw_above_player=True,
        )
        desenhar_iluminacao(self.tela, self.player, dados_room, self.camera, self.viewport)

        if self.room_manager.current_room == "corredor":
            desenhar_pote_urso(self.tela, self.camera, self.viewport, self.inventario)

        if self.room_manager.current_room == "sala_1":
            desenhar_coroa_estatua(self.tela, self.camera, self.viewport, self.inventario)

        if self.room_manager.current_room == "biblioteca":
            desenhar_livro_coala(self.tela, self.camera, self.viewport, self.inventario)

        if self.room_manager.current_room == "quarto_rainha":
            desenhar_itens_tapete(self.tela, self.camera, self.viewport)

        self.gerenciador_interacao.desenhar(self.tela, self.camera, self.viewport)
        self.desenhar_hud()
        self.inventario_hud.desenhar_hint(self.tela, self.viewport)
        self.inventario_hud.desenhar(self.tela, self.inventario, self.viewport)

        pygame.display.flip()

    def run(self):
        while self.rodando:
            if self.em_game_over:
                self._mostrar_tela_game_over()
                continue

            if self.em_creditos:
                resultado = tela_creditos(self.tela, self.relogio, tempo_total=12.0)
                if resultado == "menu":
                    self.rodando = False
                elif resultado == "sair":
                    parar_musica()
                    pygame.quit()
                    sys.exit()
                break
            
            self.processar_eventos()
            self.atualizar_logica()
            self.renderizar()
            self.dt = self.relogio.tick(60) / 1000.0

        parar_musica()
        pygame.quit()
        sys.exit()


def main():
    app = TestGameApp()
    app.run()


if __name__ == "__main__":
    main()
