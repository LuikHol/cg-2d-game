"""Objeto perseguidora que persegue o jogador na sala 2."""
import math
from pathlib import Path

import pygame

from objects.components import ColliderComponent, RigidbodyComponent, resolve_axis_aligned_motion
from render.preenchimento import scanline_fill
from render.geometry_utils import ellipse_points
from render.viewport import transformar_pontos


class ObjetoPerseguidora:
    """Inimiga que segue o jogador com colisao e sprite animado."""

    def __init__(self, x, y, tamanho=22):
        self.x = float(x)
        self.y = float(y)
        self.tamanho = int(tamanho)

        self.velocidade = 220
        self.rigidbody = RigidbodyComponent()
        self.collider = ColliderComponent(tamanho * 1.55, tamanho * 1.55)

        self.direcao = "left"
        self.movendo = False
        self.anim_fps = 8.0
        self.tempo_animacao = 0.0
        self.indice_animacao = 0
        self.escala_sprite = 1.2
        self.cache_sombra = {}
        self.tempo_sem_progresso = 0.0
        self.tempo_desvio_forcado = 0.0
        self.sinal_desvio = 1
        self.ultima_posicao_valida = (self.x, self.y)

        self.animacoes = self._carregar_animacoes()

    def _colide_estatico(self, rect, static_colliders):
        for collider in static_colliders:
            if rect.colliderect(collider.get_rect()):
                return True
        return False

    def _tentar_desgrudar(self, alvo_x, alvo_y, static_colliders):
        """Aplica pequeno desvio lateral para escapar de quinas quando travada."""
        vetor_x = alvo_x - self.x
        vetor_y = alvo_y - self.y
        dir_x, dir_y = self._normalizar_vetor(vetor_x, vetor_y)
        if dir_x == 0.0 and dir_y == 0.0:
            return False

        perp_x = -dir_y
        perp_y = dir_x
        candidatos = [
            (perp_x, perp_y),
            (-perp_x, -perp_y),
            (-dir_x, -dir_y),
        ]

        for cand_x, cand_y in candidatos:
            nx, ny = self._simular_passo(cand_x, cand_y, 0.22, static_colliders)
            rect_novo = self.collider.get_rect_from_center(nx, ny)
            desloc = math.hypot(nx - self.x, ny - self.y)
            if desloc > 8.0 and not self._colide_estatico(rect_novo, static_colliders):
                self.x = nx
                self.y = ny
                self.ultima_posicao_valida = (self.x, self.y)
                return True

        return False

    def _normalizar_vetor(self, x, y):
        norma = math.hypot(x, y)
        if norma <= 1e-6:
            return 0.0, 0.0
        return x / norma, y / norma

    def _simular_passo(self, dir_x, dir_y, dt, static_colliders):
        """Simula um passo para avaliar se a direcao ajuda a contornar obstaculos."""
        atual = self.collider.get_rect_from_center(self.x, self.y)
        move_x = dir_x * self.velocidade * dt
        move_y = dir_y * self.velocidade * dt
        resolvido = resolve_axis_aligned_motion(atual, move_x, move_y, static_colliders)
        return float(resolvido.centerx), float(resolvido.centery)

    def _escolher_direcao(self, alvo_x, alvo_y, dt, static_colliders):
        """Escolhe direcao com melhor progresso ao alvo, testando desvios locais."""
        vetor_x = alvo_x - self.x
        vetor_y = alvo_y - self.y
        distancia = math.hypot(vetor_x, vetor_y)
        if distancia <= 1e-5:
            return 0.0, 0.0, False

        base_x = vetor_x / distancia
        base_y = vetor_y / distancia

        if self.tempo_desvio_forcado > 0.0:
            perp_x = -base_y * self.sinal_desvio
            perp_y = base_x * self.sinal_desvio
            candidatos = [
                (0.25 * base_x + 0.75 * perp_x, 0.25 * base_y + 0.75 * perp_y),
                (perp_x, perp_y),
                (0.45 * base_x + 0.55 * perp_x, 0.45 * base_y + 0.55 * perp_y),
                (0.10 * base_x + 0.90 * perp_x, 0.10 * base_y + 0.90 * perp_y),
            ]

            melhor_desvio = None
            for cand_x, cand_y in candidatos:
                dir_x, dir_y = self._normalizar_vetor(cand_x, cand_y)
                if dir_x == 0.0 and dir_y == 0.0:
                    continue
                nx, ny = self._simular_passo(dir_x, dir_y, dt, static_colliders)
                dist_pos = math.hypot(alvo_x - nx, alvo_y - ny)
                delta_mov = math.hypot(nx - self.x, ny - self.y)
                score = (dist_pos, -delta_mov)
                if melhor_desvio is None or score < melhor_desvio[0]:
                    melhor_desvio = (score, dir_x, dir_y, delta_mov)

            if melhor_desvio is not None:
                return melhor_desvio[1], melhor_desvio[2], melhor_desvio[3] > 0.1

        angulos = (0, 25, -25, 50, -50, 75, -75, 115, -115)

        melhor = None
        for ang in angulos:
            rad = math.radians(ang)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            dir_x = (base_x * cos_a) - (base_y * sin_a)
            dir_y = (base_x * sin_a) + (base_y * cos_a)

            nx, ny = self._simular_passo(dir_x, dir_y, dt, static_colliders)
            dist_pos = math.hypot(alvo_x - nx, alvo_y - ny)
            delta_mov = math.hypot(nx - self.x, ny - self.y)

            # Prioriza aproximar do alvo sem travar em obstaculos.
            score = (dist_pos, -delta_mov, abs(ang))
            if melhor is None or score < melhor[0]:
                melhor = (score, dir_x, dir_y, delta_mov)

        if melhor is None:
            return 0.0, 0.0, False
        return melhor[1], melhor[2], melhor[3] > 0.1

    def _carregar_animacoes(self):
        caminho = Path("texturas/perseguidora/moca.png")
        if not caminho.exists():
            return {}

        faixa = pygame.image.load(str(caminho)).convert_alpha()
        quantidade_quadros = 4
        largura_quadro = max(1, faixa.get_width() // quantidade_quadros)
        altura_quadro = max(1, faixa.get_height())

        altura_alvo = max(24, int(self.tamanho * 2.8 * self.escala_sprite))
        quadros_direita = []
        for indice in range(quantidade_quadros):
            retangulo = pygame.Rect(indice * largura_quadro, 0, largura_quadro, altura_quadro)
            quadro = faixa.subsurface(retangulo).copy()
            bounds = quadro.get_bounding_rect(min_alpha=1)
            if bounds.width > 0 and bounds.height > 0:
                quadro = quadro.subsurface(bounds).copy()

            escala = altura_alvo / max(1, quadro.get_height())
            quadro = pygame.transform.scale(
                quadro,
                (
                    max(1, int(quadro.get_width() * escala)),
                    max(1, int(quadro.get_height() * escala)),
                ),
            )
            quadros_direita.append(quadro)

        largura_max = max(q.get_width() for q in quadros_direita)
        altura_max = max(q.get_height() for q in quadros_direita)
        padronizados = []
        for quadro in quadros_direita:
            canvas = pygame.Surface((largura_max, altura_max), pygame.SRCALPHA)
            canvas.blit(
                quadro,
                (
                    (largura_max - quadro.get_width()) // 2,
                    altura_max - quadro.get_height(),
                ),
            )
            padronizados.append(canvas)

        quadros_esquerda = [pygame.transform.flip(quadro, True, False) for quadro in padronizados]
        return {
            "right": padronizados,
            "left": quadros_esquerda,
            "down": padronizados,
            "up": padronizados,
        }

    def _get_shadow_surface(self, width, height):
        chave = (int(width), int(height))
        sombra = self.cache_sombra.get(chave)
        if sombra is not None:
            return sombra

        superficie = pygame.Surface(chave, pygame.SRCALPHA)
        pontos = ellipse_points(chave[0] // 2, chave[1] // 2, max(1, chave[0] // 2), max(1, chave[1] // 2), 24)
        scanline_fill(superficie, pontos, (0, 0, 0, 56))
        self.cache_sombra[chave] = superficie
        return superficie

    def atualizar(self, alvo_x, alvo_y, dt, static_colliders):
        """Atualiza perseguicao, colisao e animacao."""
        if not math.isfinite(self.x) or not math.isfinite(self.y):
            self.x, self.y = self.ultima_posicao_valida

        if self.tempo_desvio_forcado > 0.0:
            self.tempo_desvio_forcado = max(0.0, self.tempo_desvio_forcado - dt)

        distancia_antes = math.hypot(alvo_x - self.x, alvo_y - self.y)
        dir_x, dir_y, conseguiu_movimento = self._escolher_direcao(alvo_x, alvo_y, dt, static_colliders)

        if conseguiu_movimento:
            self.rigidbody.velocity.x = dir_x * self.velocidade
            self.rigidbody.velocity.y = dir_y * self.velocidade
            self.movendo = True
        else:
            self.rigidbody.velocity.x = 0.0
            self.rigidbody.velocity.y = 0.0
            self.movendo = False

        atual = self.collider.get_rect_from_center(self.x, self.y)
        move_x = self.rigidbody.velocity.x * dt
        move_y = self.rigidbody.velocity.y * dt
        resolvido = resolve_axis_aligned_motion(atual, move_x, move_y, static_colliders)
        novo_x = float(resolvido.centerx)
        novo_y = float(resolvido.centery)
        rect_novo = self.collider.get_rect_from_center(novo_x, novo_y)

        if self._colide_estatico(rect_novo, static_colliders):
            self.x, self.y = self.ultima_posicao_valida
            self.movendo = False
            self.tempo_desvio_forcado = max(self.tempo_desvio_forcado, 0.6)
        else:
            self.x = novo_x
            self.y = novo_y
            self.ultima_posicao_valida = (self.x, self.y)

        distancia_depois = math.hypot(alvo_x - self.x, alvo_y - self.y)
        ganho_distancia = distancia_antes - distancia_depois
        progresso_minimo = max(0.4, self.velocidade * dt * 0.07)

        if self.movendo and ganho_distancia < progresso_minimo:
            self.tempo_sem_progresso += dt
        else:
            self.tempo_sem_progresso = 0.0

        if self.tempo_sem_progresso >= 0.50 and self.tempo_desvio_forcado <= 0.0:
            self.tempo_desvio_forcado = 0.75
            self.tempo_sem_progresso = 0.0
            self.sinal_desvio *= -1

        if self.tempo_sem_progresso >= 1.10:
            if self._tentar_desgrudar(alvo_x, alvo_y, static_colliders):
                self.tempo_sem_progresso = 0.0
                self.tempo_desvio_forcado = max(self.tempo_desvio_forcado, 0.4)

        if self.movendo:
            if abs(self.rigidbody.velocity.x) >= abs(self.rigidbody.velocity.y):
                self.direcao = "right" if self.rigidbody.velocity.x > 0 else "left"
            else:
                self.direcao = "down" if self.rigidbody.velocity.y > 0 else "up"

            self.tempo_animacao += dt
            frame_time = 1.0 / self.anim_fps
            while self.tempo_animacao >= frame_time:
                self.tempo_animacao -= frame_time
                self.indice_animacao = (self.indice_animacao + 1) % 4
        else:
            self.indice_animacao = 0

    def draw(self, screen, camera, viewport):
        if not (camera[0] <= self.x <= camera[2] and camera[1] <= self.y <= camera[3]):
            return

        if not self.animacoes:
            sx, sy = transformar_pontos([(self.x, self.y)], camera, viewport)[0]
            pygame.draw.circle(screen, (55, 25, 35), (sx, sy), self.tamanho)
            return

        sx, sy = transformar_pontos([(self.x, self.y)], camera, viewport)[0]
        quadros = self.animacoes.get(self.direcao, self.animacoes["left"])
        quadro = quadros[self.indice_animacao % len(quadros)]

        largura_sombra = max(10, int(quadro.get_width() * 0.34))
        altura_sombra = max(4, int(quadro.get_height() * 0.10))
        sombra = self._get_shadow_surface(largura_sombra, altura_sombra)
        screen.blit(sombra, sombra.get_rect(center=(sx, sy + self.tamanho + 1)))

        rect = quadro.get_rect(midbottom=(sx, sy + self.tamanho))
        screen.blit(quadro, rect)
