import math
from render.poligono import desenhar_poligono
from render.scanline import scanline_fill
from render.tranfomacoes import *

class PolygonObject:
    def __init__(self, pontos):
        self.original = pontos

        # transformação
        self.x = 0
        self.y = 0
        self.angulo = 0
        self.escala = 1

        # animação
        self.tempo = 0
        self.vel_angular = 1.8
        self.vel_tempo = 3.0

        # calcula centro (pivô)
        self.cx = sum(p[0] for p in pontos) / len(pontos)
        self.cy = sum(p[1] for p in pontos) / len(pontos)

    def update(self, dt=1 / 60):
        # animação independente de FPS (dt em segundos)
        self.angulo += self.vel_angular * dt
        self.tempo += self.vel_tempo * dt

        # escala pulsando
        self.escala = 1 + 0.3 * math.sin(self.tempo)

    def get_transformado(self):
        # T(-p) · R · S · T(p) · T(pos)
        m = identidade()

        m = multiplica_matrizes(translacao(-self.cx, -self.cy), m)
        m = multiplica_matrizes(rotacao(self.angulo), m)
        m = multiplica_matrizes(escala(self.escala, self.escala), m)
        m = multiplica_matrizes(translacao(self.cx, self.cy), m)

        # posição no mundo
        m = multiplica_matrizes(translacao(self.x, self.y), m)

        return aplica_transformacao(m, self.original)

    def draw(self, screen):
        pontos = self.get_transformado()

        desenhar_poligono(screen, pontos, (255,255,255))
        scanline_fill(screen, pontos, (0,200,0))