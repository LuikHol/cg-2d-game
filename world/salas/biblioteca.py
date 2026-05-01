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
    livro_antigo = [(350, 400), (400, 400), (400, 430), (350, 430)]

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

    inter_livro = ObjetoInterativo(
        "livro_antigo",
        livro_antigo,
        (120, 80, 40),
        (160, 110, 55),
        {
            "type": "paper",
            "title": "Catalogo",
            "lines": [
                "Ala sul: tomos perdidos",
                "Ala leste: proibido entrar",
                "Use E para fechar",
            ],
        },
        texture_key="paper",
        show_border=True,
    )

    return {
        "nome": "biblioteca",
        "background_texture": "texturas/cenario/biblioteca/biblioteca.png",
        "background_zoom": 1.0,
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
            inter_livro.como_item_desenhavel(),
        ],
        "portas_visuais": [],
        "interactables": [inter_bilhete, inter_livro],
        "foreground": [
            foreground_img("texturas/objetos/poltrona.png", 158, 450, 167, 197, escala=1.6),
        ],
        "lights": [
            {"x": 310, "y": 180, "rx": 54, "ry": 42, "steps": 24},
        ],
        "colliders": [
            # Parede superior com vao da porta ao centro
            colisao_estatica(1, 8, 443, 225),
            colisao_estatica(561, 8, 443, 225),
            # Parede lateral esquerda
            colisao_estatica(0, 0, 12, 746),
            # Parede lateral direita
            colisao_estatica(985, 5, 10, 739),
            # Parede inferior
            colisao_estatica(0, 715, 1000, 29),
            # Obstaculos internos simples
            colisao_estatica(172, 367, 163, 175),
            colisao_estatica(700, 180, 111, 237),
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
