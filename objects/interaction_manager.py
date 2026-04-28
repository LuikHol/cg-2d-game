import pygame
from render.poligono import desenhar_poligono
from render.scanline import scanline_fill
from render.viewport import world_to_viewport as mundo_para_viewport
from render.textura import scanline_texture


class InteractionManager:
    def __init__(self, paper_texture=None, inventario=None):
        self.fonte_prompt = pygame.font.SysFont(None, 28)
        self.fonte_mundo = pygame.font.SysFont(None, 34)
        self.fonte_titulo_papel = pygame.font.SysFont(None, 38)
        self.fonte_corpo_papel = pygame.font.SysFont(None, 30)
        self.textura_papel = paper_texture
        self.inventario = inventario

        self.alvo_prompt = None
        self.mensagem_mundo = ""
        self.pos_mensagem_mundo = (0, 0)
        self.tempo_mensagem_mundo = 0.0

        self.papel_aberto = None
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

        for objeto in interactables:
            componente = objeto.component
            # Nao mostra prompt para itens ja coletados
            if objeto.component.action.get("type") == "pickup" and self.inventario:
                nome_item = objeto.component.action.get("item")
                if nome_item and self.inventario.tem(nome_item):
                    continue
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
            }
            self._papel_pode_fechar = False
            return

        # Default: mensagem no mapa, acima do objeto.
        self.mensagem_mundo = action.get("text", "...")
        self.pos_mensagem_mundo = obj.get_center()
        self.tempo_mensagem_mundo = float(action.get("duration", 2.6))

    def draw(self, screen, camera, viewport):
        if self.alvo_prompt:
            px, py = self.alvo_prompt.get_center()
            sx, sy = mundo_para_viewport(px, py - 34, camera, viewport)
            superficie_prompt = self.fonte_prompt.render("E: interagir", True, (245, 230, 150))
            fundo = superficie_prompt.get_rect(center=(sx, sy))
            fundo.inflate_ip(14, 8)
            self._desenhar_painel(screen, fundo, (20, 20, 20), (70, 70, 70))
            screen.blit(superficie_prompt, superficie_prompt.get_rect(center=(sx, sy)))

        if self.mensagem_mundo:
            wx, wy = self.pos_mensagem_mundo
            sx, sy = mundo_para_viewport(wx, wy - 56, camera, viewport)
            superficie_mensagem = self.fonte_mundo.render(self.mensagem_mundo, True, (250, 250, 250))
            fundo = superficie_mensagem.get_rect(center=(sx, sy))
            fundo.inflate_ip(18, 10)
            self._desenhar_painel(screen, fundo, (10, 10, 10), (60, 60, 60))
            screen.blit(superficie_mensagem, superficie_mensagem.get_rect(center=(sx, sy)))

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

        dica = self.fonte_prompt.render("E: fechar", True, (90, 75, 48))
        screen.blit(dica, (largura_tela // 2 - dica.get_width() // 2, altura_tela // 2 + 140))