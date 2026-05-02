import pygame

from objects.components import ComponenteColisaoEstatica
from objects.objeto_interagivel import ObjetoInterativo
from world.salas.utils import poligono_de_chao, foreground_img


def criar_biblioteca():
    colisao_estatica = ComponenteColisaoEstatica

    sala_x_min = 18
    sala_x_max = 982
    sala_y_min = 225
    sala_y_max = 720

    # Porta para o corredor fica na parte superior da biblioteca
    porta_x_min = 460
    porta_x_max = 540
    porta_y_topo = sala_y_min

    bilhete_biblioteca = [(250, 560), (330, 560), (330, 590), (250, 590)]

    inter_bilhete = ObjetoInterativo(
        "bilhete_biblioteca",
        bilhete_biblioteca,
        (185, 175, 120),
        (225, 210, 140),
        {
            "type": "message",
            "text": "Silencio... esta biblioteca guarda segredos.",
            "duration": 2.8,
        },
    )

    return {
        "nome": "biblioteca",
        "background_texture": "texturas/cenario/biblioteca/biblioteca.png",
        "background_zoom": 1.0,
        "viewport_margin": 50,
        "poligonos": [
            poligono_de_chao(
                [
                    (sala_x_min, sala_y_min),
                    (sala_x_max, sala_y_min),
                    (sala_x_max, sala_y_max),
                    (sala_x_min, sala_y_max),
                ],
                (110, 78, 52),
                (92, 62, 42),
            ),
            inter_bilhete.como_item_desenhavel(),
        ],
        "portas_visuais": [],
        "interactables": [inter_bilhete],
        "foreground": [
        ],
        "lights": [
        ],
        "colliders": [
            # Parede superior com vao da porta ao centro
            colisao_estatica(1, 8, 443, 225),
        ],
        "transicoes": [
            {
                "trigger": pygame.Rect(
                    porta_x_min,
                    porta_y_topo,
                    porta_x_max - porta_x_min,
                    30,
                ),
                "target": "corredor",
                "spawn": (170, 470),
            }
        ],
    }
