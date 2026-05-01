import pygame

from objects.components import ComponenteColisaoEstatica
from objects.objeto_interagivel import ObjetoInterativo
from world.salas.utils import poligono_de_chao


def criar_corredor():
    colisao_estatica = ComponenteColisaoEstatica

    placa_corredor = [(470, 355), (530, 355), (530, 395), (470, 395)]

    inter_placa = ObjetoInterativo(
        "placa",
        placa_corredor,
        (90, 110, 120),
        (110, 145, 160),
        {
            "type": "message",
            "text": "aaaaaa sorroco",
            "duration": 2.8,
        },
    )

    # Layout do corredor:
    # Teto y=0..250, chão y=500..750, corredor passável y=250..500
    # Porta sala_1: x=460..540, abertura vertical menor (y=170..250)
    # Porta sala_2: y=350..430 (abertura vertical menor)
    # Biblioteca: x=120..220, abertura vertical menor (y=500..580)

    # Teto em duas partes com vão para porta sala_1
    parede_teto_esq = [(0, 0), (460, 0), (460, 250), (0, 250)]
    parede_teto_dir = [(540, 0), (1600, 0), (1600, 250), (540, 250)]
    # Tampa superior do vão da sala_1 para reduzir altura vertical da abertura
    parede_teto_centro = [(460, 0), (540, 0), (540, 170), (460, 170)]

    # Chão com vao no canto inferior esquerdo para a biblioteca
    parede_chao_esq = [(0, 500), (120, 500), (120, 750), (0, 750)]
    parede_chao_dir = [(220, 500), (1600, 500), (1600, 750), (220, 750)]
    # Tampa inferior do vão da biblioteca para reduzir altura vertical da abertura
    parede_chao_centro = [(120, 580), (220, 580), (220, 750), (120, 750)]

    # Parede lateral esq fechada
    parede_esq = [(0, 250), (12, 250), (12, 500), (0, 500)]

    # Parede lateral dir com vão para porta sala_2
    parede_dir_cima  = [(1588, 250), (1600, 250), (1600, 350), (1588, 350)]
    parede_dir_baixo = [(1588, 430), (1600, 430), (1600, 500), (1588, 500)]

    COR_PAREDE = (30, 25, 35)
    COR_BORDA  = (55, 45, 60)

    def parede(pts):
        return {"polygon": pts, "fill_color": COR_PAREDE, "border_color": COR_BORDA, "show_border": True}

    return {
        "nome": "corredor",
        "background_texture": "texturas/cenario/chaointeiro.png",
        "background_bounds": (0, 0, 1600, 750),
        "camera_bounds": (0, 0, 1600, 750),
        "background_scale": 1.5,
        "tile_world_width": 1600,
        "poligonos": [
            parede(parede_teto_esq),
            parede(parede_teto_dir),
            parede(parede_teto_centro),
            parede(parede_chao_esq),
            parede(parede_chao_dir),
            parede(parede_chao_centro),
            parede(parede_esq),
            parede(parede_dir_cima),
            parede(parede_dir_baixo),
            inter_placa.como_item_desenhavel(),
        ],
        "portas_visuais": [],
        "interactables": [inter_placa],
        "colliders": [
            colisao_estatica(0, 0, 460, 250),
            colisao_estatica(540, 0, 1060, 250),
            colisao_estatica(460, 0, 80, 170),
            colisao_estatica(0, 500, 120, 250),
            colisao_estatica(220, 500, 1380, 250),
            colisao_estatica(120, 580, 100, 170),
            colisao_estatica(0, 250, 12, 250),
            colisao_estatica(1588, 250, 12, 100),
            colisao_estatica(1588, 430, 12, 70),
        ],
        "transicoes": [
            {
                "trigger": pygame.Rect(460, 170, 80, 20),
                "target": "sala_1",
                "spawn": (500, 650),
            },
            {
                "trigger": pygame.Rect(1588, 350, 12, 80),
                "target": "sala_2",
                "spawn": (40, 375),
            },
            {
                "trigger": pygame.Rect(120, 500, 100, 20),
                "target": "biblioteca",
                "spawn": (500, 260),
            },
        ],
    }
