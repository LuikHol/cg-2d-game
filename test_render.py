import pygame
import sys
from objects.polygon_object import PolygonObject
from test_render_config import (
    GATO_MUNDO,
    ALTURA_TELA,
    CAMINHO_TEXTURA,
    ESCALA_TEMPO,
    AREA_VIEWPORT,
    JANELA_MUNDO,
    LARGURA_TELA,
    POLIGONO_MUNDO,
    POLIGONO_OBJ_PONTOS,
    POLIGONO_OBJ_X,
    POLIGONO_OBJ_Y,
    TITULO_JANELA,
    X_MAX_RECORTE,
    X_MIN_RECORTE,
    Y_MAX_RECORTE,
    Y_MIN_RECORTE,
)

# IMPORTS DO SEU RENDER
from render.pixel import setPixel
from render.linha import bresenham
from render.poligono import desenhar_poligono
from render.scanline import scanline_fill
from render.floodfill import flood_fill
from render.circulo import desenhar_circulo
from render.elipse import desenhar_elipse
from render.textura import scanline_texture
from render.clipping import cohen_sutherland, clip_polygon_sutherland_hodgman
from render.viewport import transformar_pontos
textura = pygame.image.load(CAMINHO_TEXTURA)
xmin, ymin = X_MIN_RECORTE, Y_MIN_RECORTE
xmax, ymax = X_MAX_RECORTE, Y_MAX_RECORTE

# janela no mundo
window = JANELA_MUNDO

# viewport na tela
viewport = AREA_VIEWPORT

poligono_mundo = POLIGONO_MUNDO

# "gato" no mundo: usa a textura.jpg e sera recortado pela janela antes de ir para viewport
gato_mundo = GATO_MUNDO

poligono_obj_teste = PolygonObject(POLIGONO_OBJ_PONTOS)
poligono_obj_teste.x = POLIGONO_OBJ_X
poligono_obj_teste.y = POLIGONO_OBJ_Y

pygame.init()

screen = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption(TITULO_JANELA)

clock = pygame.time.Clock()
time_scale = ESCALA_TEMPO

# Controle para flood fill rodar só uma vez
flood_executado = False

# =========================
# LOOP PRINCIPAL
# =========================
running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))

    # =========================
    # 1. LINHAS (Bresenham)
    # =========================
    bresenham(screen, 50, 50, 300, 100, (255, 0, 0))
    bresenham(screen, 300, 100, 100, 300, (0, 0, 255))
    bresenham(screen, 100, 300, 50, 50, (0, 255, 0))

    # =========================
    # 2. POLÍGONO + SCANLINE
    # =========================
    poligono = [(500, 100), (700, 150), (650, 300), (550, 280), (480, 200)]

    desenhar_poligono(screen, poligono, (255, 255, 255))
    scanline_fill(screen, poligono, (0, 200, 0))

    # =========================
    # 3. CÍRCULO
    # =========================
    desenhar_circulo(screen, 200, 400, 80, (255, 255, 0))

    # =========================
    # 4. ELIPSE
    # =========================
    desenhar_elipse(screen, 500, 450, 120, 60, (0, 255, 255))

    # =========================
    # 5. POLÍGONO + FLOOD FILL
    # =========================
    poligono2 = [(100, 350), (300, 370), (250, 550), (120, 500)]
    cor_borda = (255, 255, 255)
    cor_fill = (255, 0, 255)

    desenhar_poligono(screen, poligono2, cor_borda)

    # =========================
    # 6. POLÍGONO COM TEXTURA
    # =========================
    poligono_textura = [(500, 50), (500, 80), (550, 200), (350, 180)]

    # borda opcional
    desenhar_poligono(screen, poligono_textura, (255,255,255))

    # 🔥 textura
    scanline_texture(screen, poligono_textura, textura)

    # =========================
    # 7. CLIPPING (Cohen-Sutherland)
    # =========================

    # desenhar a "janela"
    cor_janela = (255, 255, 255)

    # borda da janela
    bresenham(screen, xmin, ymin, xmax, ymin, cor_janela)
    bresenham(screen, xmax, ymin, xmax, ymax, cor_janela)
    bresenham(screen, xmax, ymax, xmin, ymax, cor_janela)
    bresenham(screen, xmin, ymax, xmin, ymin, cor_janela)

    # linhas de teste (algumas fora da tela)
    linhas = [
        (50, 50, 750, 550),      # corta nos 4 lados
        (200, 50, 200, 550),     # vertical atravessando
        (50, 300, 750, 300),     # horizontal atravessando
        (300, 200, 600, 400),    # totalmente dentro
        (10, 10, 50, 50)         # totalmente fora
    ]

    for linha in linhas:
        resultado = cohen_sutherland(*linha, xmin, ymin, xmax, ymax)

        if resultado:
            x1, y1, x2, y2 = resultado
            bresenham(screen, x1, y1, x2, y2, (255, 0, 0))

    # =========================
    # 8. VIEWPORT
    # =========================

    # desenhar borda da viewport
    cor = (255, 255, 255)

    bresenham(screen, viewport[0], viewport[1], viewport[2], viewport[1], cor)
    bresenham(screen, viewport[2], viewport[1], viewport[2], viewport[3], cor)
    bresenham(screen, viewport[2], viewport[3], viewport[0], viewport[3], cor)
    bresenham(screen, viewport[0], viewport[3], viewport[0], viewport[1], cor)

    # transformar pontos
    poligono_tela = transformar_pontos(poligono_mundo, window, viewport)

    # clipping no mundo -> transformacao para viewport -> textura na tela
    gato_clip_mundo = clip_polygon_sutherland_hodgman(gato_mundo, *window)
    if len(gato_clip_mundo) >= 3:
        gato_tela = transformar_pontos(gato_clip_mundo, window, viewport)
        scanline_texture(screen, gato_tela, textura)
        desenhar_poligono(screen, gato_tela, (255, 255, 255))

    # desenhar
    desenhar_poligono(screen, poligono_tela, (255,255,0))
    scanline_fill(screen, poligono_tela, (100,100,255))

    # =========================
    # 9. POLYGON OBJECT (ANIMADO)
    # =========================
    poligono_obj_teste.update(dt * time_scale)
    poligono_obj_teste.draw(screen)

    # Executa flood fill só uma vez
    if not flood_executado:
        flood_fill(screen, 200, 450, cor_fill, cor_borda)
        flood_executado = True

    pygame.display.flip()

pygame.quit()
sys.exit()