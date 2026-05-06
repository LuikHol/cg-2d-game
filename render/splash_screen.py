"""Tela de abertura estática (sem animação)."""

import pygame

from render.primitivas import desenhar_circulo, desenhar_elipse, flood_fill
from render.preenchimento import scanline_fill, scanline_fill_gradiente


class SplashScreen:
    """Tela de abertura estática com gradiente e formas geométricas."""

    def __init__(self, width=1280, height=800):
        self.width = width
        self.height = height

    def desenhar(self, surface):
        self._desenhar_fundo_gradiente(surface)
        self._desenhar_composicao_central(surface)

    def _desenhar_fundo_gradiente(self, surface):
        w = surface.get_width()
        h = surface.get_height()
        if w <= 1 or h <= 1:
            return

        pontos = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
        cores = [
            (10, 12, 22),
            (28, 18, 48),
            (18, 24, 38),
            (8, 12, 20),
        ]
        scanline_fill_gradiente(surface, pontos, cores)

    def _desenhar_composicao_central(self, surface):
        cx = self.width // 2
        cy = self.height // 2

        # Elipses decorativas fixas
        desenhar_elipse(surface, cx, cy, 230, 120, (55, 70, 120))
        desenhar_elipse(surface, cx, cy, 165, 82, (88, 110, 160))

        # Núcleo circular com flood fill
        cor_borda = (220, 220, 255)
        cor_fill = (185, 205, 255)
        desenhar_circulo(surface, cx, cy, 42, cor_borda)
        try:
            flood_fill(surface, cx, cy, cor_fill, cor_borda)
        except Exception:
            pass

        # Triângulo fixo para dar identidade visual
        tri = [(cx - 80, cy + 95), (cx + 80, cy + 95), (cx, cy - 40)]
        scanline_fill(surface, tri, (120, 240, 190))


def exibir_splash_screen(width, height, duracao=2.2):
    """Exibe splash estática por um tempo curto ou até input do usuário."""
    if not pygame.get_init():
        pygame.init()

    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    splash = SplashScreen(width, height)

    tempo = 0.0
    while tempo < max(0.2, float(duracao)):
        dt = clock.tick(60) / 1000.0
        tempo += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return True

        splash.desenhar(screen)
        pygame.display.flip()

    return True
