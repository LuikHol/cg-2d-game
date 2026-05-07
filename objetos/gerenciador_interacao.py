import math
import pygame
from efeitos_sonoros import tocar_efeito_se_existir
from render.poligono import desenhar_poligono
from render.preenchimento import scanline_fill, scanline_texture
from render.viewport import mundo_para_viewport
from render.superficie import escalar_superficie

FONTE_UI_NOME = "timesnewroman"
FONTE_UI_TAMANHO_PROMPT = 15
FONTE_UI_TAMANHO_MUNDO = 20
FONTE_UI_TAMANHO_TITULO_PAPEL = 38
FONTE_UI_TAMANHO_CORPO_PAPEL = 20

class GerenciadorInteracao:
    # Gerencia prompts, estrelas de interacao e leitura de papeis.

    def __init__(self, textura_papel=None, inventario=None):
        # Fontes de UI
        self.fonte_prompt = pygame.font.SysFont(FONTE_UI_NOME, FONTE_UI_TAMANHO_PROMPT)
        self.fonte_mundo = pygame.font.SysFont(FONTE_UI_NOME, FONTE_UI_TAMANHO_MUNDO)
        self.fonte_titulo_papel = pygame.font.SysFont(FONTE_UI_NOME, FONTE_UI_TAMANHO_TITULO_PAPEL)
        self.fonte_corpo_papel = pygame.font.SysFont(FONTE_UI_NOME, FONTE_UI_TAMANHO_CORPO_PAPEL)

        # Dependencias externas
        self.textura_papel = textura_papel
        self.inventario = inventario
        self._texture_cache = {}
        self._pickups_coletados = set()

        # Estado de mensagens e prompt
        self.alvo_prompt = None
        self.mensagem_mundo = ""
        self.pos_mensagem_mundo = (0, 0)
        self.tempo_mensagem_mundo = 0.0

        # Estado de leitura de papel
        self.papel_aberto = None
        self._interagiveis_visiveis = []
        self._papel_estava_pressionado = False
        self._papel_pode_fechar = False

    def atualizar(self, teclas, retangulo_ator, interagiveis, dt):
        # Atualiza estado de interacoes no frame atual.
        papel_pressionado = bool(teclas[pygame.K_e])

        # Se um papel estiver aberto, so processa o fechamento para evitar
        # interacoes concorrentes com outros objetos.
        if self._atualizar_papel_aberto(papel_pressionado):
            return

        self.alvo_prompt = None
        self._interagiveis_visiveis = []

        for objeto in interagiveis:
            componente = objeto.component

            # Nao exibe itens de pickup que ja foram coletados.
            if componente.acao.get("tipo") == "coletar":
                nome_item = componente.acao.get("item")
                if nome_item in self._pickups_coletados:
                    continue

            # Circulos do tapete preenchidos continuam visiveis para permitir retirar o item.

            self._interagiveis_visiveis.append(objeto)

            if componente.pode_interagir(retangulo_ator):
                self.alvo_prompt = objeto

            acionado, acao = componente.tentar_interagir(teclas, retangulo_ator)
            if acionado and acao:
                self._aplicar_acao(acao, objeto)

        if self.tempo_mensagem_mundo > 0.0:
            self.tempo_mensagem_mundo -= dt
        else:
            self.mensagem_mundo = ""

        self._papel_estava_pressionado = papel_pressionado

    def _atualizar_papel_aberto(self, papel_pressionado):
        # Atualiza estado de fechamento do papel.

        # Retorna True quando o fluxo principal de interacao deve ser interrompido.
        if not self.papel_aberto:
            return False

        if not papel_pressionado:
            self._papel_pode_fechar = True
        elif papel_pressionado and not self._papel_estava_pressionado and self._papel_pode_fechar:
            self.papel_aberto = None
            self._papel_pode_fechar = False

        self._papel_estava_pressionado = papel_pressionado
        self.alvo_prompt = None
        return True

    def _aplicar_acao(self, acao, obj):
        # Executa a acao configurada para o interagivel.
        tipo_acao = acao.get("tipo", "mensagem")

        if tipo_acao == "coletar":
            nome_item = acao.get("item")
            if nome_item in self._pickups_coletados:
                return
            if nome_item and self.inventario:
                self.inventario.adicionar(nome_item)
                self._pickups_coletados.add(nome_item)
                tocar_efeito_se_existir("pegar_item.mp3")
            self.mensagem_mundo = acao.get("mensagem", f"Pegou {nome_item}!")
            self.pos_mensagem_mundo = obj.obter_centro()
            self.tempo_mensagem_mundo = 2.5
            return

        if tipo_acao == "depositar":
            from objetos import estado_puzzle
            slot = acao.get("slot", -1)
            # Slot preenchido: devolve o item ao inventario.
            if estado_puzzle.slot_preenchido(slot):
                item_devolvido = estado_puzzle.retirar_item(slot)
                if item_devolvido and self.inventario:
                    self.inventario.adicionar(item_devolvido)
                return
            # Slot vazio: usa o item selecionado no HUD (ou primeiro disponivel).
            item_na_mao = getattr(self, "item_em_mao", None)
            if not item_na_mao or not (self.inventario and self.inventario.tem(item_na_mao)):
                item_na_mao = next(
                    (i for i in estado_puzzle.obter_ordem() if self.inventario and self.inventario.tem(i)),
                    None,
                )
            if item_na_mao and estado_puzzle.colocar_item(slot, item_na_mao):
                self.inventario.remover(item_na_mao)
                tocar_efeito_se_existir("colocar_item.mp3")
                self.mensagem_mundo = acao.get("mensagem_ok", "Item colocado!")
                self.pos_mensagem_mundo = obj.obter_centro()
                self.tempo_mensagem_mundo = 2.5
            return

        if tipo_acao == "documento":
            textura = self.textura_papel
            caminho_textura = acao.get("caminho_textura")
            e_imagem = False
            if caminho_textura:
                if caminho_textura not in self._texture_cache:
                    self._texture_cache[caminho_textura] = pygame.image.load(caminho_textura).convert_alpha()
                textura = self._texture_cache[caminho_textura]
                e_imagem = True
            self.papel_aberto = {
                "titulo": acao.get("titulo", "Anotacao"),
                "linhas": acao.get("linhas", []),
                "texture": textura,
                "e_imagem": e_imagem,
            }
            self._papel_pode_fechar = False
            return

        # Fallback para mensagem comum acima do objeto.
        self.mensagem_mundo = acao.get("texto", "...")
        self.pos_mensagem_mundo = obj.obter_centro()
        self.tempo_mensagem_mundo = float(acao.get("duracao", 2.6))

    def _desenhar_estrela(self, surface, cx, cy, raio_externo, raio_interno, num_pontas, cor):
        # Desenha uma estrela preenchida com scanline_fill.
        pontos = []
        for i in range(num_pontas * 2):
            ang = math.pi / num_pontas * i - math.pi / 2
            r = raio_externo if i % 2 == 0 else raio_interno
            pontos.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        if len(pontos) >= 3:
            scanline_fill(surface, pontos, cor)

    def desenhar(self, screen, camera, viewport):
        # Renderiza estrelas, prompts, mensagens e sobreposicao de papel.

        viewport_rect = pygame.Rect(
            viewport[0],
            viewport[1],
            max(0, viewport[2] - viewport[0]),
            max(0, viewport[3] - viewport[1]),
        )
        old_clip = screen.get_clip()
        screen.set_clip(viewport_rect)

        t = pygame.time.get_ticks() / 500.0
        for objeto in self._interagiveis_visiveis:
            wx, wy = objeto.obter_centro()
            sx, sy = mundo_para_viewport(wx, wy, camera, viewport)

            # Flutuacao vertical suave.
            sy -= 10 + int(4 * math.sin(t + wx * 0.05))

            # Raio entre 4 e 7 px.
            raio = 4 + 3 * (0.5 + 0.5 * math.sin(t * 2 + wx * 0.05))
            alfa = int(180 + 75 * math.sin(t * 2))
            cor = (255, 255, 255, alfa)

            tam = int(raio * 2) + 4
            estrela_rect = pygame.Rect(sx - tam // 2, sy - tam // 2, tam, tam)
            if not estrela_rect.colliderect(viewport_rect):
                continue
            surf_estrela = pygame.Surface((tam, tam), pygame.SRCALPHA)
            self._desenhar_estrela(surf_estrela, tam // 2, tam // 2, raio, raio * 0.4, 4, cor)
            screen.blit(surf_estrela, (sx - tam // 2, sy - tam // 2))

        screen.set_clip(old_clip)

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

        # Folha em formato de poligono para reforcar visual de papel.
        papel = [
            (largura_tela // 2 - 240, altura_tela // 2 - 170),
            (largura_tela // 2 + 240, altura_tela // 2 - 150),
            (largura_tela // 2 + 220, altura_tela // 2 + 170),
            (largura_tela // 2 - 220, altura_tela // 2 + 190),
        ]

        textura = self.papel_aberto.get("texture")
        e_imagem = self.papel_aberto.get("e_imagem", False)

        if textura is not None and e_imagem:
            xs = [p[0] for p in papel]
            ys = [p[1] for p in papel]
            rect_w = max(xs) - min(xs)
            rect_h = max(ys) - min(ys)
            scaled = escalar_superficie(textura, rect_w, rect_h)
            screen.blit(scaled, (min(xs), min(ys)))
        elif textura is not None:
            scanline_texture(screen, papel, textura)
            desenhar_poligono(screen, papel, (95, 82, 54))
        else:
            scanline_fill(screen, papel, (233, 222, 188))
            desenhar_poligono(screen, papel, (95, 82, 54))

        titulo = self.papel_aberto.get("titulo", "Documento")
        linhas = self.papel_aberto.get("linhas", [])

        superficie_titulo = self.fonte_titulo_papel.render(titulo, True, (62, 44, 24))
        screen.blit(superficie_titulo, (largura_tela // 2 - superficie_titulo.get_width() // 2, altura_tela // 2 - 130))

        y = altura_tela // 2 - 72
        for linha in linhas:
            superficie_linha = self.fonte_corpo_papel.render(linha, True, (62, 44, 24))
            screen.blit(superficie_linha, (largura_tela // 2 - superficie_linha.get_width() // 2, y))
            y += 34

        dica = self.fonte_prompt.render("E: fechar", True, (255, 255, 255))
        screen.blit(dica, (largura_tela // 2 - dica.get_width() // 2, altura_tela // 2 + 140))