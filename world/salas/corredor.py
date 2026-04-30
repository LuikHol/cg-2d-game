import pygame

from objects.components import ComponenteColisaoEstatica
from objects.objeto_interagivel import ObjetoInterativo


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
        "background_texture": "texturas/cenario/corredor/corredor.png",
        "background_zoom": 1.0,
        "background_bounds": (0, 0, 1600, 750),
        "camera_bounds": (0, 0, 1600, 750),
        "vinheta_inferior": [
            (0.58, (48, 40, 72, 45)),
            (0.70, (40, 32, 62, 70)),
            (0.82, (30, 24, 50, 95)),
        ],
        "poligonos": [
            # Item interativo da placa.
            inter_placa.como_item_desenhavel(),
        ],
        "portas_visuais": [
            ([(1588, 320), (1600, 320), (1600, 440), (1588, 440)], (170, 125, 70), (220, 180, 110)),
        ],
        "interactables": [inter_placa],
        "colliders": [
            colisao_estatica(0, 0, 1600, 250),
            colisao_estatica(0, 460, 1600, 290),
            colisao_estatica(0, 0, 12, 750),
            colisao_estatica(1588, 0, 12, 320),
            colisao_estatica(1588, 440, 12, 310),
        ],
        "transicoes": [
            {
                "trigger": pygame.Rect(460, 220, 80, 30),
                "target": "sala_1",
                "spawn": (500, 650),
            },
            {
                "trigger": pygame.Rect(1588, 320, 12, 120),
                "target": "sala_2",
                "spawn": (40, 375),
            },
        ],
    }
