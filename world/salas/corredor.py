import pygame

from objects.components import ComponenteColisaoEstatica
from objects.interactable_object import ObjetoInterativo
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

    return {
        "nome": "corredor",
        "background_texture": "texturas/cenario/chaointeiro.png",
        "poligonos": [
            poligono_de_chao([(0, 250), (1000, 250), (1000, 500), (0, 500)], (90, 88, 85), (120, 118, 112)),
            ([(0, 0), (460, 0), (460, 180), (0, 180)], (45, 48, 58), (60, 64, 76)),
            ([(540, 0), (1000, 0), (1000, 180), (540, 180)], (45, 48, 58), (60, 64, 76)),
            ([(0, 500), (1000, 500), (1000, 750), (0, 750)], (45, 48, 58), (60, 64, 76)),
            inter_placa.como_item_desenhavel(),
        ],
        "portas_visuais": [
            ([(988, 320), (1000, 320), (1000, 440), (988, 440)], (170, 125, 70), (220, 180, 110)),
        ],
        "interactables": [inter_placa],
        "colliders": [
            colisao_estatica(0, 0, 460, 180),
            colisao_estatica(540, 0, 460, 180),
            colisao_estatica(0, 500, 1000, 250),
            colisao_estatica(0, 0, 12, 750),
            colisao_estatica(988, 0, 12, 320),
            colisao_estatica(988, 440, 12, 310),
        ],
        "transicoes": [
            {
                "trigger": pygame.Rect(460, 220, 80, 30),
                "target": "sala_1",
                "spawn": (500, 650),
            },
            {
                "trigger": pygame.Rect(988, 320, 12, 120),
                "target": "sala_2",
                "spawn": (40, 375),
            },
        ],
    }
