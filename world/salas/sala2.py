import pygame

from objects.components import ComponenteColisaoEstatica
from objects.objeto_interagivel import ObjetoInterativo


def criar_sala2():
    colisao_estatica = ComponenteColisaoEstatica
    largura_sala = 5600

    pergaminho_sala2 = [(5300, 350), (5390, 350), (5390, 380), (5300, 380)]

    inter_pergaminho = ObjetoInterativo(
        "pergaminho",
        pergaminho_sala2,
        (170, 155, 110),
        None,
        {
            "type": "paper",
            "title": "Folha de Papel",
            "lines": [
                "Corredor 2",
                "Nao olhe para tras",
                "Use E para fechar",
            ],
        },
        texture_key="paper",
        show_border=False,
    )

    parede_teto = [(0, 0), (largura_sala, 0), (largura_sala, 180), (0, 180)]
    parede_chao = [(0, 600), (largura_sala, 600), (largura_sala, 750), (0, 750)]

    parede_esq_cima = [(0, 180), (12, 180), (12, 320), (0, 320)]
    parede_esq_baixo = [(0, 440), (12, 440), (12, 600), (0, 600)]
    parede_dir = [(largura_sala - 12, 180), (largura_sala, 180), (largura_sala, 600), (largura_sala - 12, 600)]

    COR_PAREDE = (30, 30, 35)
    COR_BORDA = (55, 30, 60)
    COR_OBSTACULO = (58, 60, 72)
    COR_OBSTACULO_BORDA = (92, 96, 118)

    def parede(pts):
        return {
            "polygon": pts,
            "fill_color": COR_PAREDE,
            "border_color": COR_BORDA,
            "show_border": True,
        }

    def obstaculo(pts):
        # Obstaculos preenchidos por scanline_fill em render/desenhar_item.
        return {
            "polygon": pts,
            "fill_color": COR_OBSTACULO,
            "border_color": COR_OBSTACULO_BORDA,
            "show_border": True,
        }

    # Slalom alternado: obriga o player a subir/descer durante a fuga.
    obstaculos_retangulares = [
        (730, 180, 115, 170),
        (1090, 430, 115, 170),
        (1490, 180, 120, 170),
        (1890, 430, 115, 170),
        (2310, 180, 200, 200),
        (2730, 430, 110, 170),
        (3150, 180, 120, 170),
        (3570, 430, 115, 170),
        (3990, 180, 120, 200),
        (4410, 430, 120, 170),
        (4830, 180, 115, 200),
    ]

    obstaculos_poligonos = [
        [
            (x, y),
            (x + w, y),
            (x + w, y + h),
            (x, y + h),
        ]
        for x, y, w, h in obstaculos_retangulares
    ]

    return {
        "nome": "sala_2",
        "background_texture": "texturas/cenario/chaointeiro.png",
        "background_bounds": (0, 0, largura_sala, 750),
        "camera_bounds": (0, 0, largura_sala, 750),
        "camera_viewport_width": 1000,
        "camera_viewport_height": 750,
        "viewport_margin": 100,
        "background_scale": 1.5,
        "tile_world_width": 1600,
        "poligonos": [
            parede(parede_teto),
            parede(parede_chao),
            parede(parede_esq_cima),
            parede(parede_esq_baixo),
            parede(parede_dir),
            *[obstaculo(pts) for pts in obstaculos_poligonos],
            inter_pergaminho.como_item_desenhavel(),
        ],
        "portas_visuais": [
            ([(0, 320), (16, 320), (16, 440), (0, 440)], (170, 125, 70), (220, 180, 110)),
        ],
        "interactables": [inter_pergaminho],
        "colliders": [
            colisao_estatica(0, 0, largura_sala, 180),
            colisao_estatica(0, 600, largura_sala, 150),
            colisao_estatica(0, 180, 12, 140),
            colisao_estatica(0, 440, 12, 160),
            colisao_estatica(largura_sala - 12, 180, 12, 420),
            *[colisao_estatica(x, y, w, h) for x, y, w, h in obstaculos_retangulares],
        ],
        "transicoes": [
            {
                "trigger": pygame.Rect(0, 350, 12, 80),
                "target": "corredor",
                "spawn": (1540, 390),
            }
        ],
    }
