import pygame

from objetos.componentes import ComponenteColisaoEstatica
from objetos.objeto_interagivel import ObjetoInterativo
from mundo.salas.utils import poligono_de_chao, foreground_img


def criar_sala1():
    colisao_estatica = ComponenteColisaoEstatica

    sala1_x_min = 18
    sala1_x_max = 982
    sala1_y_min = 225
    sala1_y_max = 720

    porta_sala1_x_min = 460
    porta_sala1_x_max = 540
    porta_sala1_y = sala1_y_max

    quadro_familia = [(875, 225), (940, 225), (940, 265), (875, 265)]

    inter_quadro = ObjetoInterativo(
        "quadro",
        quadro_familia,
        None,
        None,
        {
            "tipo": "mensagem",
            "texto": "Sinto sua falta...",
            "duracao": 2.8,
        },
        mostrar_borda=False,
    )

    coroa_pickup = [(255, 260), (390, 260), (325, 310), (255, 310)]
    inter_coroa = ObjetoInterativo(
        "coroa_vermelha",
        coroa_pickup,
        None,
        None,
        {
            "tipo": "coletar",
            "item": "coroa_vermelha",
            "mensagem": "Voce pegou a Coroa Vermelha!",
        },
        mostrar_borda=False,
    )

    return {
        "nome": "sala_1",
        "textura_fundo": "texturas/cenario/quarto_menino/quarto.png",
        "zoom_fundo": 1.0,
        "poligonos": [
            poligono_de_chao(
                [
                    (sala1_x_min, sala1_y_min),
                    (sala1_x_max, sala1_y_min),
                    (sala1_x_max, sala1_y_max),
                    (sala1_x_min, sala1_y_max),
                ],
                (120, 80, 40),
                (100, 65, 30),
            ),
            inter_quadro.como_item_desenhavel(),
        ],
        "portas_visuais": [],
        "interagiveis": [inter_coroa, inter_quadro],
        "primeiro_plano": [
            foreground_img("texturas/objetos/abajour.png", 287, 680, 46, 130, escala=6),
            foreground_img("texturas/objetos/poltrona.png", 158, 450, 167, 197, escala=1.80),
        ],
        "luzes": [
            {"x": 310, "y": 180, "rx": 54, "ry": 42, "steps": 24},
        ],
        "colidores": [
            # Parede superior (faixa de pedra no topo do PNG)
            colisao_estatica(1, 8, 995, 225),
            # Parede lateral esquerda
            colisao_estatica(0, 0, 12, 746),
            # Parede lateral direita
            colisao_estatica(985, 5, 10, 739),
            # Parede inferior com vão da porta
            colisao_estatica(0, 715, 443, 29),
            colisao_estatica(561, 715, 443, 29),
            # Cadeira menino
            colisao_estatica(411, 182, 211, 123),
            # Mesa brinquedo
            colisao_estatica(696, 507, 200, 114),
            # Bola
            colisao_estatica(885, 387, 90, 111),
            # Mesa menino
            colisao_estatica(411, 182, 211, 123),
            # Estatua Gata
            colisao_estatica(259, 57, 102, 248),
            # Abajor
            colisao_estatica(285, 683, 55, 43),
            # Poltrona
            colisao_estatica(172, 367, 163, 175),
            # Armário (canto superior esquerdo)
            colisao_estatica(35, 32, 187, 282),
            # Cama (lado direito)
            colisao_estatica(701, 180, 111, 237),
        ],
        "transicoes": [
            {
                "gatilho": pygame.Rect(
                    porta_sala1_x_min,
                    porta_sala1_y - 10,
                    porta_sala1_x_max - porta_sala1_x_min,
                    42,
                ),
                "destino": "corredor",
                "posicao_spawn": (498, 200),
            }
        ],
    }
