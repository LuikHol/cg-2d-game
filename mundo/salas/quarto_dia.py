import pygame

from objetos.componentes import ComponenteColisaoEstatica
from objetos.objeto_interagivel import ObjetoInterativo
from mundo.salas.utils import poligono_de_chao, foreground_img


def criar_quarto_dia():
    colisao_estatica = ComponenteColisaoEstatica

    sala_x_min = 18
    sala_x_max = 982
    sala_y_min = 225
    sala_y_max = 720

    porta_x_min = 460
    porta_x_max = 540
    porta_y = sala_y_max

    caixa_brinquedos = [(864, 180), (980, 180), (980, 239), (864, 239)]
    urso_pelucia = [(259, 67), (361, 67), (361, 305), (259, 305)]
    princesa = [(54, 500), (140, 500), (140, 650), (54, 650)]
    livro= [(548,54), (548,140), (689,140), (689,64)]

    inter_caixa_brinquedos = ObjetoInterativo(
        "caixa de brinquedos",
        caixa_brinquedos,
        None,
        None,
        {
            "tipo": "mensagem",
            "texto": "Uma caixa cheia de brinquedos.",
            "duracao": 2.8,
        },
        mostrar_borda=False,
    )

    inter_urso_pelucia = ObjetoInterativo(
        "urso de pelucia",
        urso_pelucia,
        None,
        None,
        {
            "tipo": "mensagem",
            "texto": "O urso guardião.",
            "duracao": 2.8,
        },
        mostrar_borda=False,
    )

    inter_princesa = ObjetoInterativo(
        "princesa",
        princesa,
        None,
        None,
        {
            "tipo": "mensagem",
            "texto": "Como a Princesa veio parar aqui?",
            "duracao": 2.8,
        },
        mostrar_borda=False,
    )

    inter_livro = ObjetoInterativo(
        "livro",
        livro,
        None,
        None,
        {
            "tipo": "mensagem",
            "texto": "Um brinquedo esquecido bem no meio da sala.",
            "duracao": 2.8,
        },
        mostrar_borda=False,
    )

    return {
        "nome": "quarto_dia",
        "textura_fundo": "texturas/cenario/quarto_menino/quarto_dia.png",
        "zoom_fundo": 1.0,
        "poligonos": [
            poligono_de_chao(
                [
                    (sala_x_min, sala_y_min),
                    (sala_x_max, sala_y_min),
                    (sala_x_max, sala_y_max),
                    (sala_x_min, sala_y_max),
                ],
                (120, 80, 40),
                (100, 65, 30),
            ),
        ],
        "alfa_escuridao": 50,
        "portas_visuais": [],
        "interagiveis": [
            inter_caixa_brinquedos,
            inter_urso_pelucia,
            inter_princesa,
            inter_livro,
        ],
        "primeiro_plano": [
            foreground_img("texturas/objetos/abajour.png", 287, 680, 46, 130, escala=6),
            foreground_img("texturas/objetos/poltrona_dia.png", 158, 450, 167, 197, escala=1.80),
            foreground_img("texturas/objetos/colcha_cama.png", 700, 273, 104, 82, escala=1),
        ],
        "luzes": [
            {"x": 310, "y": 180, "rx": 54, "ry": 42, "steps": 24},
        ],
        "colisores": [
            # Parede superior (faixa de pedra no topo do PNG)
            colisao_estatica(1, 8, 995, 225),
            # Parede lateral esquerda
            colisao_estatica(0, 0, 12, 746),
            # Parede lateral direita
            colisao_estatica(985, 5, 10, 739),
            # Parede inferior com vao da porta
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
            # Urso de pelucia
            colisao_estatica(259, 57, 102, 248),
            # Abajor
            colisao_estatica(285, 683, 55, 43),
            # Poltrona
            colisao_estatica(172, 367, 163, 175),
            # Armario (canto superior esquerdo)
            colisao_estatica(35, 32, 187, 282),
            # Princesa
            colisao_estatica(54, 548, 86, 141),
            # Caixa de brinquedos
            colisao_estatica(864, 180, 116, 59),
            # Cama
            colisao_estatica(698, 337, 111, 80),
        ],
        "transicoes": [
            {
                "gatilho": pygame.Rect(
                    porta_x_min,
                    porta_y - 10,
                    porta_x_max - porta_x_min,
                    42,
                ),
                "destino": "creditos",
                "posicao_spawn": (500, 375),
            }
        ],
    }