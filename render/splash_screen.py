"""Tela de abertura estática (sem animação)."""

import pygame

from render.primitivas import bresenham, desenhar_circulo, desenhar_elipse, flood_fill
from render.preenchimento import scanline_fill_gradiente


class SplashScreen:
    """Tela de abertura estática com gradiente e formas geométricas."""

    def __init__(self, width=1280, height=800):
        self.width = width
        self.height = height

    def desenhar(self, surface):
        self._desenhar_fundo_gradiente(surface)
        self._desenhar_composicao_central(surface)

    def _desenhar_linhas_decorativas(self, surface, cx, cy):
        # Linhas diagonais para dar mais estrutura ao layout da splash.
        cor_linha = (95, 125, 180)
        bresenham(surface, cx - 280, cy - 150, cx - 130, cy - 40, cor_linha)
        bresenham(surface, cx + 130, cy - 40, cx + 280, cy - 150, cor_linha)
        bresenham(surface, cx - 280, cy + 150, cx - 130, cy + 40, cor_linha)
        bresenham(surface, cx + 130, cy + 40, cx + 280, cy + 150, cor_linha)

    def _desenhar_coroa(self, surface, cx, cy):
        """Desenha uma coroa simples com 3 pontas e 1 joia vermelha central."""
        # Base da coroa (elipse)
        cor_ouro_borda = (200, 160, 40)
        cor_ouro_fill = (255, 215, 70)
        
        desenhar_elipse(surface, cx, cy, 50, 20, cor_ouro_borda)
        try:
            flood_fill(surface, cx, cy, cor_ouro_fill, cor_ouro_borda)
        except Exception:
            pass
        
        # 3 Triângulos (pontas) usando bresenham
        # Ponta esquerda
        bresenham(surface, cx - 30, cy - 5, cx - 50, cy - 50, (200, 160, 40))
        bresenham(surface, cx - 50, cy - 50, cx - 10, cy - 5, (200, 160, 40))
        
        # Ponta central (mais alta)
        bresenham(surface, cx - 10, cy - 5, cx, cy - 70, (200, 160, 40))
        bresenham(surface, cx, cy - 70, cx + 10, cy - 5, (200, 160, 40))
        
        # Ponta direita
        bresenham(surface, cx + 10, cy - 5, cx + 50, cy - 50, (200, 160, 40))
        bresenham(surface, cx + 50, cy - 50, cx + 30, cy - 5, (200, 160, 40))
        
        # Joia vermelha única no topo central
        cor_joia_borda = (200, 80, 80)
        cor_joia_fill = (220, 50, 50)
        
        desenhar_circulo(surface, cx, cy - 70, 12, cor_joia_borda)
        try:
            flood_fill(surface, cx, cy - 70, cor_joia_fill, cor_joia_borda)
        except Exception:
            pass

    def _desenhar_rosto(self, surface, cx, cy):
        # Estilo solicitado: círculo da cabeça, círculo do cabelo e linhas do rosto.
        cor_pele_borda = (210, 166, 136)
        cor_pele_fill = (234, 192, 162)
        cor_cabelo_borda = (150, 84, 56)
        cor_cabelo_fill = (184, 110, 78)
        cor_traco = (54, 46, 60)

        # Cabeça (círculo central).
        desenhar_circulo(surface, cx, cy, 22, cor_pele_borda)
        try:
            flood_fill(surface, cx, cy, cor_pele_fill, cor_pele_borda)
        except Exception:
            pass

        # Cabelo (círculo superior sobreposto).
        cabelo_cx = cx
        cabelo_cy = cy - 15
        desenhar_circulo(surface, cabelo_cx, cabelo_cy, 16, cor_cabelo_borda)
        try:
            flood_fill(surface, cabelo_cx, cabelo_cy, cor_cabelo_fill, cor_cabelo_borda)
        except Exception:
            pass

        # Linhas de rosto: sobrancelhas, olhos, nariz e boca.
        bresenham(surface, cx - 11, cy - 8, cx - 5, cy - 9, cor_traco)
        bresenham(surface, cx + 5, cy - 9, cx + 11, cy - 8, cor_traco)
        bresenham(surface, cx - 9, cy - 3, cx - 5, cy - 3, cor_traco)
        bresenham(surface, cx + 5, cy - 3, cx + 9, cy - 3, cor_traco)
        bresenham(surface, cx, cy - 1, cx, cy + 4, cor_traco)
        bresenham(surface, cx - 7, cy + 10, cx, cy + 12, cor_traco)
        bresenham(surface, cx, cy + 12, cx + 7, cy + 10, cor_traco)

    def _desenhar_fundo_gradiente(self, surface):
        w = surface.get_width()
        h = surface.get_height()
        if w <= 1 or h <= 1:
            return

        pontos = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
        cores = [
            (60, 80, 150),      # top-left: azul noturno claro
            (120, 40, 140),     # top-right: roxo vibrante
            (60, 30, 100),      # bottom-right: roxo escuro
            (25, 35, 80),       # bottom-left: azul noturno escuro
        ]
        scanline_fill_gradiente(surface, pontos, cores)

    def _desenhar_composicao_central(self, surface):
        cx = self.width // 2
        cy = self.height // 2

        self._desenhar_linhas_decorativas(surface, cx, cy)

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

        # Desenha coroa central
        self._desenhar_coroa(surface, cx, cy)


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
