import pygame

from objetos.componentes import ComponenteColisaoEstatica
from objetos.objeto_interagivel import ObjetoInterativo


def criar_sala2():
    colisao_estatica = ComponenteColisaoEstatica
    largura_sala = 5600

    parede_teto = [(0, 0), (largura_sala, 0), (largura_sala, 180), (0, 180)]
    parede_chao = [(0, 600), (largura_sala, 600), (largura_sala, 750), (0, 750)]

    parede_esq_cima = [(0, 180), (12, 180), (12, 320), (0, 320)]
    parede_esq_baixo = [(0, 440), (12, 440), (12, 600), (0, 600)]

    parede_dir_cima  = [(largura_sala - 12, 180), (largura_sala, 180), (largura_sala, 320), (largura_sala - 12, 320)]
    parede_dir_baixo = [(largura_sala - 12, 440), (largura_sala, 440), (largura_sala, 600), (largura_sala - 12, 600)]

    COR_PAREDE = (30, 30, 35)
    COR_BORDA = (55, 30, 60)
    COR_OBSTACULO = (58, 60, 72)
    COR_OBSTACULO_BORDA = (92, 96, 118)

    def parede(pts):
        return {
            "poligono": pts,
            "cor_preenchimento": COR_PAREDE,
            "cor_borda": COR_BORDA,
            "mostrar_borda": True,
        }

    def obstaculo(pts):
        return {
            "poligono": pts,
            "cor_preenchimento": COR_OBSTACULO,
            "cor_borda": COR_OBSTACULO_BORDA,
            "mostrar_borda": True,
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
        "textura_fundo": "texturas/cenario/corredor/chaocorredor2.png",
        "limites_fundo": (0, 0, largura_sala, 750),
        "limites_camera": (0, 0, largura_sala, 750),
        "largura_camera": 1000,
        "altura_camera": 750,
        "margem_viewport": 100,
        "escala_fundo": 1.5,
        "largura_tile_mundo": 1600,
        "poligonos": [
            parede(parede_teto),
            parede(parede_chao),
            parede(parede_esq_cima),
            parede(parede_esq_baixo),
            parede(parede_dir_cima),
            parede(parede_dir_baixo),
            *[obstaculo(pts) for pts in obstaculos_poligonos],
        ],
        "portas_visuais": [],
        "interagiveis": [],
        "luzes": [
            {"x": largura_sala - 60, "y": 380, "rx": 200, "ry": 160, "steps": 36},
        ],
        "colidores": [
            colisao_estatica(0, 0, largura_sala, 180),
            colisao_estatica(0, 600, largura_sala, 150),
            colisao_estatica(0, 180, 12, 140),
            colisao_estatica(0, 440, 12, 160),
            colisao_estatica(largura_sala - 12, 180, 12, 140),
            colisao_estatica(largura_sala - 12, 440, 12, 160),
            *[colisao_estatica(x, y, w, h) for x, y, w, h in obstaculos_retangulares],
        ],
        "transicoes": [
            {
                "gatilho": pygame.Rect(0, 350, 12, 80),
                "destino": "corredor",
                "posicao_spawn": (1540, 390),
            }
        ],
    }
