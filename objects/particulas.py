"""Partículas de pickup usando PolygonObject com transformações geométricas.

Cada partícula é um losango pequeno que:
- Rotaciona via matriz R
- Sobe e encolhe via translação T + escala S
- Desaparece quando escala chega a zero
"""

import math
from render.poligono import desenhar_poligono
from render.preenchimento import scanline_fill
from render.transformacoes import (
    identidade, translacao, escala, rotacao,
    multiplica_matrizes, aplica_transformacao,
)
from render.viewport import world_to_viewport


# Losango base centrado na origem (será posicionado via transformação)
_LOSANGO = [
    ( 0, -5),
    ( 3,  0),
    ( 0,  5),
    (-3,  0),
]

# Triângulo base
_TRIANGULO = [
    ( 0, -5),
    ( 4,  4),
    (-4,  4),
]


class Particula:
    """Partícula animada usando apenas transformações geométricas."""

    def __init__(self, x, y, vel_x, vel_y, cor, forma="losango"):
        # Posição no mundo
        self.x = float(x)
        self.y = float(y)
        self.vel_x = float(vel_x)
        self.vel_y = float(vel_y)
        self.cor = cor

        # Estado de animação
        self.angulo = 0.0
        self.vel_angular = 4.0 + abs(vel_x) * 0.3   # Mais rápido quanto mais velocidade
        self.escala_val = 1.0
        self.tempo = 0.0
        self.duracao = 0.6                            # Tempo até desaparecer (segundos)
        self.viva = True

        self.pontos_base = _LOSANGO if forma == "losango" else _TRIANGULO

    def update(self, dt):
        if not self.viva:
            return

        self.tempo += dt
        t = self.tempo / self.duracao           # 0 → 1 ao longo da vida

        # Encerra quando completar o ciclo
        if t >= 1.0:
            self.viva = False
            return

        # Move no mundo
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        # Rotação crescente
        self.angulo += self.vel_angular * dt

        # Escala vai de 1 → 0 (encolhe até sumir)
        self.escala_val = max(0.0, 1.0 - t)

    def draw(self, screen, camera, viewport):
        if not self.viva or self.escala_val <= 0.01:
            return

        # Culling
        if not (camera[0] <= self.x <= camera[2] and camera[1] <= self.y <= camera[3]):
            return

        # Converte centro para tela
        sx, sy = world_to_viewport(self.x, self.y, camera, viewport)

        # Monta matriz: T(-centro) · R · S · T(tela)
        # Os pontos base já estão centrados na origem, então só R · S · T(sx, sy)
        m = identidade()
        m = multiplica_matrizes(rotacao(self.angulo), m)
        m = multiplica_matrizes(escala(self.escala_val, self.escala_val), m)
        m = multiplica_matrizes(translacao(sx, sy), m)

        pontos = aplica_transformacao(m, self.pontos_base)

        # Determina cor com fade (vai escurecendo)
        fator = self.escala_val
        cor_fill = tuple(max(0, min(255, int(c * fator))) for c in self.cor)
        cor_borda = tuple(min(255, int(c * 1.2)) for c in cor_fill)

        scanline_fill(screen, pontos, cor_fill)
        desenhar_poligono(screen, pontos, cor_borda)


class SistemaParticulas:
    """Gerencia partículas ativas na tela."""

    def __init__(self):
        self.particulas: list[Particula] = []

    def emitir_pickup(self, x, y, cor=(255, 240, 80)):
        """Emite um burst de partículas na posição do item coletado."""
        import random

        formas = ["losango", "triangulo"]
        for i in range(8):
            ang = (2 * math.pi / 8) * i
            velocidade = 60 + random.uniform(-20, 40)
            vx = math.cos(ang) * velocidade
            vy = math.sin(ang) * velocidade - 40  # Pequeno impulso para cima

            # Varia levemente a cor
            cor_variada = (
                max(0, min(255, cor[0] + random.randint(-30, 30))),
                max(0, min(255, cor[1] + random.randint(-20, 20))),
                max(0, min(255, cor[2] + random.randint(-20, 20))),
            )

            p = Particula(x, y, vx, vy, cor_variada, forma=random.choice(formas))
            p.vel_angular = random.uniform(-6.0, 6.0)
            p.duracao = 0.5 + random.uniform(0, 0.3)
            self.particulas.append(p)

    def update(self, dt):
        for p in self.particulas:
            p.update(dt)
        # Remove partículas mortas
        self.particulas = [p for p in self.particulas if p.viva]

    def draw(self, screen, camera, viewport):
        for p in self.particulas:
            p.draw(screen, camera, viewport)
