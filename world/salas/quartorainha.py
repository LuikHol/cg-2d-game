import pygame

from objects.components import ComponenteColisaoEstatica
from objects.objeto_interagivel import ObjetoInterativo
from world.salas.utils import poligono_de_chao


def criar_quarto_rainha():
    colisao_estatica = ComponenteColisaoEstatica
    # Porta para o corredor fica na lateral direita do quarto.
    porta_corredor = pygame.Rect(982, 376, 15, 117)

    bilhete_biblioteca = [(737, 448), (767, 448), (767, 495), (737, 495)]

    inter_bilhete = ObjetoInterativo(
        "bilhete_biblioteca",
        bilhete_biblioteca,
        (185, 175, 120),
        (225, 210, 140),
        {
            "type": "message",
            "text": "Do calor da realeza, ao dourado da docura, os tres guardioes carregam a chave da abertura",
            "duration": 2.8,
        },
    )

    return {
        "nome": "quarto_rainha",
        "background_texture": "texturas/cenario/quarto_rainha/quartorainha.png",
        "background_zoom": 1.0,
        "viewport_margin": 50,
        "poligonos": [
        ],
        "portas_visuais": [],
        "interactables": [inter_bilhete],
        "foreground": [
        ],
        "lights": [
            {"x": 290, "y": 492, "rx": 52, "ry": 56, "steps": 24},
            {"x": 467, "y": 332, "rx": 56, "ry": 50, "steps": 24},
            {"x": 639, "y": 492, "rx": 54, "ry": 51, "steps": 24},
        ],
        "colliders": [
            # Parede superior com vao da porta ao centro
            colisao_estatica(1, 0, 17, 747),
            colisao_estatica(4, 735, 988, 13),
            colisao_estatica(992, 487, 8, 261),
            colisao_estatica(988, 12, 2, 358),
            colisao_estatica(985, 0, 13, 367),
            colisao_estatica(8, 198, 987, 60),
            colisao_estatica(721, 112, 190, 225),
            colisao_estatica(258, 210, 63, 87),
            colisao_estatica(748, 625, 64, 84),
            colisao_estatica(98, 628, 72, 104),
            colisao_estatica(20, 381, 187, 163),
            colisao_estatica(900, 495, 94, 193),
            colisao_estatica(881, 531, 53, 115),

        ],
        "transicoes": [
            {
                "trigger": porta_corredor,
                "target": "corredor",
                "spawn": (40, 390),
            }
        ],
    }
