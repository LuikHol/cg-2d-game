import pygame

from objects.components import ComponenteColisaoEstatica
from objects.objeto_interagivel import ObjetoInterativo
from render.collectible_sprites import get_collectible_sprite
from world.salas.utils import foreground_img, foreground_surface, poligono_de_chao


def criar_corredor():
    colisao_estatica = ComponenteColisaoEstatica
    sprite_pote_mel = get_collectible_sprite("pote_mel", pixel_size=1)

    placa_corredor = [(470, 355), (530, 355), (530, 395), (470, 395)]
    # Area de interacao na base do urso para manter a estrela na posicao anterior.
    pote_corredor = [(1358, 246), (1382, 246), (1382, 268), (1358, 268)]

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

    inter_pote = ObjetoInterativo(
        "pote",
        pote_corredor,
        None,
        None,
        {
            "type": "pickup",
            "item": "pote_mel",
            "mensagem": "Voce pegou um Pote de Mel!",
        },
        show_border=False,
    )

    # Layout do corredor:
    # Teto y=0..180, chão y=600..750, corredor passável y=180..600
    # Porta sala_1: x=460..540, abertura vertical menor (y=130..180)
    # Porta sala_2: y=350..430 (abertura vertical menor)
    # Biblioteca: x=130..210, abertura vertical menor (y=600..680)

    # Teto em duas partes com vão para porta sala_1
    parede_teto_esq = [(0, 0), (460, 0), (460, 180), (0, 180)]
    parede_teto_dir = [(540, 0), (1600, 0), (1600, 180), (540, 180)]
    # Tampa superior do vão da sala_1 para reduzir altura vertical da abertura
    parede_teto_centro = [(460, 0), (540, 0), (540, 130), (460, 130)]

    # Chão com vao no canto inferior esquerdo para a biblioteca
    parede_chao_esq = [(0, 600), (130, 600), (130, 750), (0, 750)]
    parede_chao_dir = [(210, 600), (1600, 600), (1600, 750), (210, 750)]
    # Tampa inferior do vão da biblioteca para reduzir altura vertical da abertura
    parede_chao_centro = [(130, 680), (210, 680), (210, 750), (130, 750)]

    # Parede lateral esq fechada
    parede_esq = [(0, 180), (12, 180), (12, 600), (0, 600)]

    # Parede lateral dir com vão para porta sala_2
    parede_dir_cima  = [(1588, 180), (1600, 180), (1600, 350), (1588, 350)]
    parede_dir_baixo = [(1588, 430), (1600, 430), (1600, 600), (1588, 600)]

    COR_PAREDE = (30, 30, 35)
    COR_BORDA  = (55, 30, 60)

    def parede(pts):
        return {"polygon": pts, "fill_color": COR_PAREDE, "border_color": COR_BORDA, "show_border": True}

    return {
        "nome": "corredor",
        "background_texture": "texturas/cenario/chaointeiro.png",
        "background_bounds": (0, 0, 1600, 750),
        "camera_bounds": (0, 0, 1600, 750),
        "viewport_margin": 100,
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
        "interactables": [inter_placa, inter_pote],
        "foreground": [
            # Poltrona: ajuste so o valor de escala para mudar o tamanho.
            # Base: x=158, y=400, w=164, h=197 (escala=1.0)  ← mude y_base para subir/descer
            foreground_img("texturas/objetos/urso.png", 1321, 76, 92, 201, escala=2.5, draw_above_player=False),
            foreground_surface(sprite_pote_mel, 1355, 118, 25, 18, escala=1.0, draw_above_player=False),
        ],
        "lights": [
            {"x": 1341, "y": 127, "rx": 55, "ry": 68, "steps": 24},
        ],
        "colliders": [
            # Urso Estatua
            colisao_estatica(1331, 41, 79, 208),
            colisao_estatica(0, 0, 460, 180),
            colisao_estatica(540, 0, 1060, 180),
            colisao_estatica(460, 0, 80, 130),
            colisao_estatica(0, 600, 130, 150),
            colisao_estatica(210, 600, 1390, 150),
            colisao_estatica(130, 680, 80, 70),
            colisao_estatica(0, 180, 12, 420),
            colisao_estatica(1588, 180, 12, 170),
            colisao_estatica(1588, 430, 12, 170),
        ],
        "transicoes": [
            {
                "trigger": pygame.Rect(460, 130, 80, 20),
                "target": "sala_1",
                "spawn": (500, 650),
            },
            {
                "trigger": pygame.Rect(1588, 350, 12, 80),
                "target": "sala_2",
                "spawn": (40, 375),
            },
            {
                "trigger": pygame.Rect(130, 600, 80, 20),
                "target": "biblioteca",
                "spawn": (500, 260),
            },
        ],
    }
