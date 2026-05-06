"""Objeto do jogador com animacao, fisicas e renderizacao."""
import pygame
import math
from pathlib import Path
from render.poligono import desenhar_poligono
from render.superficie import escalar_superficie, espelhar_x
from render.pixel import setPixel
from render.preenchimento import scanline_fill, scanline_texture
from render.viewport import transformar_pontos
from render.clipping import clip_polygon_com_cohen_sutherland
from render.utils_geometrias import pontos_elipse
from objetos.componentes import ComponenteRigidbody, ComponenteColisao, resolver_movimento_alinhado


class ObjetoJogador:
    """Representa o jogador no mundo com sprite animado, colisoes e fisicas."""

    def __init__(self, x, y, tamanho=20):
        # Posicao no mundo (ponto central do corpo).
        self.x = float(x)
        self.y = float(y)
        self.tamanho = tamanho

        # Fisicas basicas.
        self.velocidade = 250  # unidades de mundo por segundo
        self.rigidbody = ComponenteRigidbody()
        self.collider = ComponenteColisao(tamanho * 1.4, tamanho * 1.4)

        # Estado de movimento e animacao.
        self.direcao = "direita"   # direita | esquerda | cima | baixo
        self.movendo = False
        self.anim_fps = 9.0
        self.tempo_animacao = 0.0
        self.indice_animacao = 0
        self.escala_sprite = 1.18

        # Cache de superficies renderizadas para nao recriar a cada frame.
        self.cache_sombra = {}
        self.cache_coroa = {}

        # Calcula altura alvo do sprite baseado no tamanho do jogador.
        altura_alvo = max(16, int(self.tamanho * 2.5 * self.escala_sprite))

        # Novo formato: 3 arquivos separados por direcao (4 frames cada).
        faixa_baixo = Path("texturas/personagem/menino1.png")
        faixa_lado = Path("texturas/personagem/menino2.png")
        faixa_cima = Path("texturas/personagem/menino3.png")
        if faixa_baixo.exists() and faixa_lado.exists() and faixa_cima.exists():
            quadros_baixo = self._carregar_quadros_da_faixa(faixa_baixo, altura_alvo)
            quadros_direita = self._carregar_quadros_da_faixa(faixa_lado, altura_alvo)
            quadros_cima = self._carregar_quadros_da_faixa(faixa_cima, altura_alvo)
            quadros_esquerda = [self._espelhar_superficie_x(quadro) for quadro in quadros_direita]

            quadros_baixo, quadros_cima, quadros_direita, quadros_esquerda = self._normalizar_animacoes(
                quadros_baixo,
                quadros_cima,
                quadros_direita,
                quadros_esquerda,
            )

            self.animacoes = {
                "baixo": quadros_baixo,
                "cima": quadros_cima,
                "direita": quadros_direita,
                "esquerda": quadros_esquerda,
            }
            self.quantidade_frames = 4
            return

        # Fallback: carrega spritesheet unificada se os arquivos individuais nao existirem.
        self.folha_sprite = pygame.image.load("texturas/menino.png").convert_alpha()
        largura_folha = self.folha_sprite.get_width()
        altura_folha = self.folha_sprite.get_height()

        # Spritesheet do menino: grade 4x3 (frente/lado/costas).
        # A linha do meio contem lados esquerdo e direito separados por colunas.
        usa_grade_4x3 = True

        if usa_grade_4x3:
            largura_quadro = largura_folha // 4
            altura_quadro = altura_folha // 3
            extra_cabeca_cima = max(2, altura_quadro // 12)

            linhas = []
            for linha in range(3):
                quadros_linha = []
                for coluna in range(4):
                    extra_topo = extra_cabeca_cima if linha == 2 else 0
                    y = max(0, linha * altura_quadro - extra_topo)
                    h = min(altura_folha - y, altura_quadro + extra_topo)
                    retangulo = pygame.Rect(coluna * largura_quadro, y, largura_quadro, h)
                    quadros_linha.append(self.folha_sprite.subsurface(retangulo).copy())
                linhas.append(quadros_linha)

            # Escala baseada no conteudo real do sprite (ignorando transparencias extras).
            altura_alvo = max(16, int(self.tamanho * 3.5 * self.escala_sprite))

            escala = altura_alvo / max(1, altura_quadro)

            def preparar_quadros(quadros):
                """Prepara quadros aplicando escala uniforme."""
                preparados = []
                for quadro in quadros:
                    preparados.append(
                        escalar_superficie(
                            quadro,
                            (
                                max(1, int(largura_quadro * escala)),
                                max(1, int(altura_quadro * escala)),
                            ),
                        )
                    )
                return preparados

            quadros_baixo = preparar_quadros(linhas[0])
            # Todos os 4 frames laterais estao virados para a direita;
            # left é gerado espelhando.
            quadros_direita = preparar_quadros(linhas[1])
            quadros_esquerda = [self._espelhar_superficie_x(quadro) for quadro in quadros_direita]
            quadros_cima = preparar_quadros(linhas[2])

            # Normaliza todos os frames para o mesmo tamanho e ancora no "pe"
            # para evitar tremores ao trocar entre frente/costas/lados.
            quadros_baixo, quadros_cima, quadros_direita, quadros_esquerda = self._normalizar_animacoes(
                quadros_baixo,
                quadros_cima,
                quadros_direita,
                quadros_esquerda,
            )

            self.animacoes = {
                "baixo": quadros_baixo,
                "cima": quadros_cima,
                "direita": quadros_direita,
                "esquerda": quadros_esquerda,
            }
            self.quantidade_frames = 4
        else:
            # Fallback para o spritesheet antigo em uma linha.
            self.quantidade_frames = 5
            largura_quadro = largura_folha // self.quantidade_frames
            altura_quadro = altura_folha
            quadros_base = []
            for indice in range(self.quantidade_frames):
                retangulo = pygame.Rect(indice * largura_quadro, 0, largura_quadro, altura_quadro)
                quadros_base.append(self.folha_sprite.subsurface(retangulo).copy())

            altura_alvo = max(16, int(self.tamanho * 3.5 * self.escala_sprite))
            quadros_base_preparados = []
            for quadro in quadros_base:
                corte = self._recortar_alpha(quadro)
                escala = altura_alvo / max(1, corte.get_height())
                quadros_base_preparados.append(
                    escalar_superficie(
                        corte,
                        (
                            max(1, int(corte.get_width() * escala)),
                            max(1, int(corte.get_height() * escala)),
                        ),
                    )
                )
            quadros_base = quadros_base_preparados
            quadros_base_esquerda = [self._espelhar_superficie_x(quadro) for quadro in quadros_base]
            self.animacoes = {
                "baixo": quadros_base,
                "cima": quadros_base,
                "direita": quadros_base,
                "esquerda": quadros_base_esquerda,
            }

    def _recortar_alpha(self, surface):
        """Recorta a superficie removendo bordas transparentes."""
        bounds = surface.get_bounding_rect(min_alpha=1)
        if bounds.width <= 0 or bounds.height <= 0:
            return surface
        return surface.subsurface(bounds).copy()

    def _carregar_quadros_da_faixa(self, caminho_imagem, altura_alvo):
        """Carrega e processa frames de animacao a partir de uma faixa de sprite.
        
        Extrai 4 frames, aplica escala proporcional e centra/ancora no pe.
        """
        faixa = pygame.image.load(str(caminho_imagem)).convert_alpha()
        quantidade_quadros = 4
        largura_quadro = faixa.get_width() // quantidade_quadros
        altura_quadro = faixa.get_height()
        quadros_originais = []
        for indice in range(quantidade_quadros):
            retangulo = pygame.Rect(indice * largura_quadro, 0, largura_quadro, altura_quadro)
            quadros_originais.append(faixa.subsurface(retangulo).copy())

        # Recorta cada frame removendo alfa transparente.
        recortes = []
        largura_max_recorte = 1
        altura_max_recorte = 1
        for quadro in quadros_originais:
            b = quadro.get_bounding_rect(min_alpha=1)
            if b.width <= 0 or b.height <= 0:
                b = pygame.Rect(0, 0, largura_quadro, altura_quadro)
            else:
                # Pequena folga para evitar corte seco na borda do sprite.
                folga = 1
                x = max(0, b.x - folga)
                y = max(0, b.y - folga)
                w = min(largura_quadro - x, b.width + (2 * folga))
                h = min(altura_quadro - y, b.height + (2 * folga))
                b = pygame.Rect(x, y, w, h)
            recorte = quadro.subsurface(b).copy()
            recortes.append(recorte)
            if recorte.get_width() > largura_max_recorte:
                largura_max_recorte = recorte.get_width()
            if recorte.get_height() > altura_max_recorte:
                altura_max_recorte = recorte.get_height()

        # Escala proporcional baseada na altura maxima dos recortes.
        escala = altura_alvo / max(1, altura_max_recorte)
        quadros = []
        largura_canvas_alvo = max(1, int(largura_max_recorte * escala))
        altura_canvas_alvo = max(1, int(altura_max_recorte * escala))

        for recorte in recortes:
            quadro_escalado = escalar_superficie(
                recorte,
                max(1, int(recorte.get_width() * escala)),
                max(1, int(recorte.get_height() * escala)),
            )
            # Canvas centralizado horizontalmente e ancorado no pe verticalmente.
            canvas = pygame.Surface((largura_canvas_alvo, altura_canvas_alvo), pygame.SRCALPHA)
            x = (largura_canvas_alvo - quadro_escalado.get_width()) // 2
            y = altura_canvas_alvo - quadro_escalado.get_height()
            canvas.blit(quadro_escalado, (x, y))
            quadros.append(canvas)
        return quadros

    def _limites_sem_fundo(self, surface, bg_color, tolerance=18):
        """Calcula bounding box ignorando pixels proximos da cor de fundo."""
        w, h = surface.get_size()
        min_x, min_y = w, h
        max_x, max_y = -1, -1

        for y in range(h):
            for x in range(w):
                r, g, b, _ = surface.get_at((x, y))
                if (
                    abs(r - bg_color[0]) > tolerance
                    or abs(g - bg_color[1]) > tolerance
                    or abs(b - bg_color[2]) > tolerance
                ):
                    if x < min_x:
                        min_x = x
                    if y < min_y:
                        min_y = y
                    if x > max_x:
                        max_x = x
                    if y > max_y:
                        max_y = y

        if max_x < min_x or max_y < min_y:
            return None
        return pygame.Rect(min_x, min_y, (max_x - min_x) + 1, (max_y - min_y) + 1)

    def _normalizar_animacoes(self, quadros_baixo, quadros_cima, quadros_direita, quadros_esquerda):
        """Normaliza todos os frames para mesmo tamanho, centralizando e ancorand no pe."""
        grupos = [quadros_baixo, quadros_cima, quadros_direita, quadros_esquerda]
        todos = [quadro for grupo in grupos for quadro in grupo]
        largura_maxima = max(quadro.get_width() for quadro in todos)
        altura_maxima = max(quadro.get_height() for quadro in todos)

        def padronizar(grupo):
            """Coloca cada frame em um canvas padrao, centralizado e ancorado."""
            saida = []
            for quadro in grupo:
                w, h = quadro.get_size()
                canvas = pygame.Surface((largura_maxima, altura_maxima), pygame.SRCALPHA)
                # Centraliza em x e ancora no pe (base do sprite).
                canvas.blit(quadro, ((largura_maxima - w) // 2, altura_maxima - h))
                saida.append(canvas)
            return saida

        return padronizar(quadros_baixo), padronizar(quadros_cima), padronizar(quadros_direita), padronizar(quadros_esquerda)

    def _espelhar_superficie_x(self, surface):
        """Espelha uma superficie horizontalmente."""
        return espelhar_x(surface)

    def _gerar_pontos_elipse(self, width, height, segmentos=28):
        """Gera poligono aproximando uma elipse para usar com scanline_fill."""
        cx = width // 2
        cy = height // 2
        rx = max(1, width // 2)
        ry = max(1, height // 2)
        return pontos_elipse(cx, cy, rx, ry, segmentos)

    def _obter_sombra_contato(self, width, height):
        """Retorna sombra de contato em cache (otimizacao)."""
        chave = (width, height)
        sombra_em_cache = self.cache_sombra.get(chave)
        if sombra_em_cache is not None:
            return sombra_em_cache

        # Desenha sombra como elipse preenchida com alpha baixo.
        superficie = pygame.Surface((width, height), pygame.SRCALPHA)
        pontos = self._gerar_pontos_elipse(width, height)
        scanline_fill(superficie, pontos, (0, 0, 0, 42))
        self.cache_sombra[chave] = superficie
        return superficie

    def _obter_superficie_coroa(self, pixel_size):
        """Retorna coroa renderizada em cache (otimizacao)."""
        chave = max(1, int(pixel_size))
        coroa_em_cache = self.cache_coroa.get(chave)
        if coroa_em_cache is not None:
            return coroa_em_cache

        # Desenha coroa usando padroes de pixels (retro style).
        pattern = [
            "00100100",
            "00111100",
            "01111110",
            "11111111",
            "01111110",
            "00111100",
        ]
        largura = len(pattern[0]) * chave
        altura = len(pattern) * chave
        superficie = pygame.Surface((largura, altura), pygame.SRCALPHA)
        dourado = (246, 210, 74, 255)
        dourado_escuro = (179, 128, 26, 255)
        joia = (220, 70, 80, 255)

        for py, row in enumerate(pattern):
            for px, value in enumerate(row):
                if value == "0":
                    continue
                color = dourado
                if py >= len(pattern) - 2:
                    color = dourado_escuro
                if (px, py) in {(3, 2), (4, 2)}:
                    color = joia
                inicio_x = px * chave
                inicio_y = py * chave
                for desloc_y in range(chave):
                    for desloc_x in range(chave):
                        setPixel(superficie, inicio_x + desloc_x, inicio_y + desloc_y, color)

        self.cache_coroa[chave] = superficie
        return superficie

    def mover(self, dx, dy, dt, static_colliders):
        """Atualiza movimento, colisoes, direcao e animacao."""
        # Define velocidade baseada no input.
        self.rigidbody.velocidade.x = dx * self.velocidade
        self.rigidbody.velocidade.y = dy * self.velocidade
        self.movendo = (dx != 0 or dy != 0)

        # Resolve colisoes com retangulo de colisao axis-aligned.
        atual = self.collider.obter_rect_do_centro(self.x, self.y)
        move_x = self.rigidbody.velocidade.x * dt
        move_y = self.rigidbody.velocidade.y * dt
        resolvido = resolver_movimento_alinhado(atual, move_x, move_y, static_colliders)

        # Atualiza posicao do centro.
        self.x = float(resolvido.centerx)
        self.y = float(resolvido.centery)

        # Determina direcao baseado na velocidade (prioriza horizontal).
        if self.movendo:
            if abs(dx) >= abs(dy):
                self.direcao = "direita" if dx > 0 else "esquerda"
            else:
                self.direcao = "baixo" if dy > 0 else "cima"

        # Atualiza animacao: incrementa frame quando movendo, reseta quando parado.
        if self.movendo:
            self.tempo_animacao += dt
            frame_time = 1.0 / self.anim_fps
            while self.tempo_animacao >= frame_time:
                self.tempo_animacao -= frame_time
                self.indice_animacao = (self.indice_animacao + 1) % self.quantidade_frames
        else:
            self.indice_animacao = 0

    def get_pontos(self):
        """Retorna os pontos do corpo do jogador como losango (fallback para renderizacao poligonal)."""
        t = self.tamanho
        return [
            (self.x,     self.y - t),   # topo
            (self.x + t, self.y),        # direita
            (self.x,     self.y + t),    # base
            (self.x - t, self.y),        # esquerda
        ]

    def desenhar(self, screen, camera, viewport, textura=None):
        """Renderiza o jogador com sprite animado, sombra e coroa.
        
        Culling: nao renderiza se fora do viewport.
        Se animacoes existem: usa sprite com sombra e coroa pulsante.
        Senao: fallback para poligono losango.
        """
        # Culling simples no mundo antes de converter para a tela.
        if not (camera[0] <= self.x <= camera[2] and camera[1] <= self.y <= camera[3]):
            return

        # Se os frames existem, desenha sprite animado.
        if hasattr(self, "animacoes") and self.animacoes:
            sx, sy = transformar_pontos([(self.x, self.y)], camera, viewport)[0]
            quadros_direcao = self.animacoes.get(self.direcao, self.animacoes.get("baixo", []))
            if not quadros_direcao:
                quadros_direcao = next(iter(self.animacoes.values()))
            quadro = quadros_direcao[self.indice_animacao % len(quadros_direcao)]

            # Ancora visual no pe do personagem.
            rect = quadro.get_rect(midbottom=(sx, sy + self.tamanho))

            # Renderiza sombra de contato no solo.
            largura_sombra = max(10, int(quadro.get_width() * 0.36))
            altura_sombra = max(4, int(quadro.get_height() * 0.10))
            sombra_contato = self._obter_sombra_contato(largura_sombra, altura_sombra)
            retangulo_sombra = sombra_contato.get_rect(center=(sx, sy + self.tamanho + 1))
            screen.blit(sombra_contato, retangulo_sombra)

            # Renderiza sprite principal.
            screen.blit(quadro, rect)

            # Renderiza coroa pulsante acima da cabeca.
            tamanho_pixel_coroa = max(2, int(quadro.get_height() * 0.05))
            coroa = self._obter_superficie_coroa(tamanho_pixel_coroa)
            oscilacao = int(pygame.time.get_ticks() / 220) % 2
            retangulo_coroa = coroa.get_rect(
                midbottom=(sx, rect.top + max(3, coroa.get_height() // 2) + oscilacao)
            )
            screen.blit(coroa, retangulo_coroa)
            return

        # Fallback para o desenho poligonal anterior.
        pontos = self.get_pontos()
        clip = clip_polygon_com_cohen_sutherland(pontos, *camera)
        if len(clip) >= 3:
            tela = transformar_pontos(clip, camera, viewport)
            if textura:
                scanline_texture(screen, tela, textura)
            else:
                scanline_fill(screen, tela, (220, 200, 0))
            desenhar_poligono(screen, tela, (255, 255, 80))
        
