import pygame

from objects.components import ComponenteColisaoEstatica
from objects.interactable_object import ObjetoInterativo
from world.salas.utils import poligono_de_chao


def criar_sala2():
    colisao_estatica = ComponenteColisaoEstatica

    pergaminho_sala2 = [(700, 620), (790, 620), (790, 650), (700, 650)]

    inter_pergaminho = ObjetoInterativo(
        "pergaminho",
        pergaminho_sala2,
        (170, 155, 110),
        None,
        {
            "type": "paper",
            "title": "Folha de Papel",
            "lines": [
                "Registro da sala 2",
                "Acesso liberado ao corredor",
                "Use E para fechar",
            ],
        },
        texture_key="paper",
        show_border=False,
    )

    return {
        "nome": "sala_2",
        "background_texture": "texturas/cenario/chaointeiro.png",
        "poligonos": [
            poligono_de_chao([(0, 120), (1000, 120), (1000, 750), (0, 750)], (105, 78, 58), (90, 62, 44)),
            ([(0, 0), (1000, 0), (1000, 120), (0, 120)], (74, 70, 92), (98, 94, 118)),
            ([(620, 420), (760, 420), (760, 560), (620, 560)], (52, 55, 72), (75, 80, 100)),
            inter_pergaminho.como_item_desenhavel(),
        ],
        "portas_visuais": [
            ([(0, 320), (16, 320), (16, 440), (0, 440)], (170, 125, 70), (220, 180, 110)),
        ],
        "interactables": [inter_pergaminho],
        "colliders": [
            colisao_estatica(0, 0, 1000, 120),
            colisao_estatica(984, 0, 16, 750),
            colisao_estatica(0, 734, 1000, 16),
            colisao_estatica(620, 420, 140, 140),
        ],
        "transicoes": [
            {
                "trigger": pygame.Rect(0, 320, 16, 120),
                "target": "corredor",
                "spawn": (960, 375),
            }
        ],
    }
