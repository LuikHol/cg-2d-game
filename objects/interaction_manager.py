import math
import pygame
from render.poligono import desenhar_poligono
from render.scanline import scanline_fill
from render.viewport import world_to_viewport as mundo_para_viewport
from render.textura import scanline_texture


class InteractionManager:
    def __init__(self, paper_texture=None, inventario=None):
        self.fonte_prompt = pygame.font.SysFont("timesnewroman", 20)
        self.fonte_mundo = pygame.font.SysFont("timesnewroman", 20)
        self.fonte_titulo_papel = pygame.font.SysFont("timesnewroman", 38)
        self.fonte_corpo_papel = pygame.font.SysFont("timesnewroman", 20)
        self.textura_papel = paper_texture
        self.inventario = inventario
        self._texture_cache = {}

        self.alvo_prompt = None
        self.mensagem_mundo = ""
        self.pos_mensagem_mundo = (0, 0)
        self.tempo_mensagem_mundo = 0.0

        self.papel_aberto = None
        # Lista de interagiveis visiveis atualizada a cada frame para desenhar as estrelas.
        self._interagiveis_visiveis = []
        self._papel_estava_pressionado = False
        self._papel_pode_fechar = False

    def _retangulo_para_poligono(self, rect):
        return [
            (rect.left, rect.top),
            (rect.right, rect.top),
            (rect.right, rect.bottom),
            (rect.left, rect.bottom),
        ]

    def _desenhar_painel(self, screen, rect, cor_preenchimento, cor_borda=None):
        painel = self._retangulo_para_poligono(rect)
        scanline_fill(screen, painel, cor_preenchimento)
        if cor_borda is not None:
            desenhar_poligono(screen, painel, cor_borda)

    def update(self, keys, actor_rect, interactables, dt):
        papel_pressionado = bool(keys[pygame.K_e])

        # Quando o papel estiver aberto, pausa novas interacoes e gerencia apenas fechamento.
        if self.papel_aberto:
            if not papel_pressionado:
                self._papel_pode_fechar = True
            elif papel_pressionado and not self._papel_estava_pressionado and self._papel_pode_fechar:
                self.papel_aberto = None
                self._papel_pode_fechar = False

            self._papel_estava_pressionado = papel_pressionado
            self.alvo_prompt = None
            return

        self.alvo_prompt = None
        # Guarda os interagiveis disponiveis (nao coletados) para desenhar as estrelas.
        self._interagiveis_visiveis = []

        for objeto in interactables:
            componente = objeto.component
            # Nao mostra prompt para itens ja coletados
            if objeto.component.action.get("type") == "pickup" and self.inventario:
                nome_item = objeto.component.action.get("item")
                if nome_item and self.inventario.tem(nome_item):
                    continue
            self._interagiveis_visiveis.append(objeto)
            if componente.can_interact(actor_rect):
                self.alvo_prompt = objeto

            acionado, acao = componente.try_interact(keys, actor_rect)
            if acionado and acao:
                self._aplicar_acao(acao, objeto)

        if self.tempo_mensagem_mundo > 0.0:
            self.tempo_mensagem_mundo -= dt
        else:
            self.mensagem_mundo = ""

        self._papel_estava_pressionado = papel_pressionado

    def _aplicar_acao(self, action, obj):
        tipo_acao = action.get("type", "message")

        if tipo_acao == "pickup":
            nome_item = action.get("item")
            if nome_item and self.inventario:
                self.inventario.adicionar(nome_item)
            self.mensagem_mundo = action.get("mensagem", f"Pegou {nome_item}!")
            self.pos_mensagem_mundo = obj.get_center()
            self.tempo_mensagem_mundo = 2.5
            return

        if tipo_acao == "paper":
            self.papel_aberto = {
                "title": action.get("title", "Anotacao"),
                "lines": action.get("lines", []),
                "texture": texture,
                "is_image": is_image,
            }
            self._papel_pode_fechar = False
            return

        # Default: mensagem no mapa, acima do objeto.
        self.mensagem_mundo = action.get("text", "...")
        self.pos_mensagem_mundo = obj.get_center()
        self.tempo_mensagem_mundo = float(action.get("duration", 2.6))

    def _desenhar_estrela(self, surface, cx, cy, raio_externo, raio_interno, num_pontas, cor):
        """Desenha uma estrela preenchida usando o scanline_fill existente."""
        pontos = []
        for i in range(num_pontas * 2):
            ang = math.pi / num_pontas * i - math.pi / 2
            r = raio_externo if i % 2 == 0 else raio_interno
            pontos.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        if len(pontos) >= 3:
            scanline_fill(surface, pontos, cor)

    def draw(self, screen, camera, viewport):
        # Desenha estrela pulsante acima de cada objeto interativo disponivel.
        t = pygame.time.get_ticks() / 500.0
        for objeto in self._interagiveis_visiveis:
            wx, wy = objeto.get_center()
            sx, sy = mundo_para_viewport(wx, wy, camera, viewport)
            # Offset vertical acima do objeto + flutuacao suave.
            sy -= 10 + int(4 * math.sin(t + wx * 0.05))
            # Raio pulsa entre 4 e 7 pixels.
            raio = 4 + 3 * (0.5 + 0.5 * math.sin(t * 2 + wx * 0.05))
            alfa = int(180 + 75 * math.sin(t * 2))
            cor = (255, 255, 255, alfa)
            # Superficie temporaria para suportar alpha na estrela.
            tam = int(raio * 2) + 4
            surf_estrela = pygame.Surface((tam, tam), pygame.SRCALPHA)
            self._desenhar_estrela(surf_estrela, tam // 2, tam // 2, raio, raio * 0.4, 4, cor)
            screen.blit(surf_estrela, (sx - tam // 2, sy - tam // 2))

        if self.alvo_prompt and not self.mensagem_mundo:
            nome = self.alvo_prompt.name
            superficie_prompt = self.fonte_prompt.render(f"[ E ] {nome}", True, (255, 255, 255))
            largura_tela, altura_tela = screen.get_size()
            cx = largura_tela // 2
            cy = altura_tela - 48
            screen.blit(superficie_prompt, superficie_prompt.get_rect(center=(cx, cy)))

        if self.mensagem_mundo:
            largura_tela, altura_tela = screen.get_size()
            cx = largura_tela // 2
            cy = altura_tela - 48
            superficie_mensagem = self.fonte_mundo.render(self.mensagem_mundo, True, (255, 255, 255))
            screen.blit(superficie_mensagem, superficie_mensagem.get_rect(center=(cx, cy)))

        if self.papel_aberto:
            self._desenhar_sobreposicao_papel(screen)

    def _desenhar_sobreposicao_papel(self, screen):
        largura_tela, altura_tela = screen.get_size()

        # Folha em formato de poligono para reforçar o efeito de "papel".
        papel = [
            (largura_tela // 2 - 240, altura_tela // 2 - 170),
            (largura_tela // 2 + 240, altura_tela // 2 - 150),
            (largura_tela // 2 + 220, altura_tela // 2 + 170),
            (largura_tela // 2 - 220, altura_tela // 2 + 190),
        ]

        if self.textura_papel is not None:
            scanline_texture(screen, papel, self.textura_papel)
        else:
            scanline_fill(screen, papel, (233, 222, 188))

        # Borda discreta para evitar contorno forte/estranho.
        desenhar_poligono(screen, papel, (95, 82, 54))

        titulo = self.papel_aberto.get("title", "Documento")
        linhas = self.papel_aberto.get("lines", [])

        superficie_titulo = self.fonte_titulo_papel.render(titulo, True, (62, 44, 24))
        screen.blit(superficie_titulo, (largura_tela // 2 - superficie_titulo.get_width() // 2, altura_tela // 2 - 130))

        y = altura_tela // 2 - 72
        for linha in linhas:
            superficie_linha = self.fonte_corpo_papel.render(linha, True, (62, 44, 24))
            screen.blit(superficie_linha, (largura_tela // 2 - superficie_linha.get_width() // 2, y))
            y += 34

        hint = self.font_paper_hint.render("E: fechar", True, (255, 255, 255))
        screen.blit(hint, (w // 2 - hint.get_width() // 2, h // 2 + 140))
