import pygame
from objects.components import StaticColliderComponent
from objects.interactable_object import InteractableObject


def build_rooms():
    colisao_estatica = StaticColliderComponent
    sala1_x_min = 18
    sala1_x_max = 982
    sala1_y_min = 225
    sala1_y_max = 720
    porta_sala1_x_min = 460
    porta_sala1_x_max = 540
    porta_sala1_y = sala1_y_max

    def poligono_chao(pontos, cor_preenchimento, cor_borda):
        return {
            "polygon": pontos,
            "fill_color": cor_preenchimento,
            "border_color": cor_borda,
            "skip_on_background": True,
        }

    bilhete_sala1 = [(250, 520), (330, 520), (330, 550), (250, 550)]
    placa_corredor = [(470, 355), (530, 355), (530, 395), (470, 395)]
    pergaminho_sala2 = [(700, 620), (790, 620), (790, 650), (700, 650)]

    inter_bilhete = InteractableObject(
        "bilhete",
        bilhete_sala1,
        (185, 175, 120),
        (225, 210, 140),
        {
            "type": "message",
            "text": "ola",
            "duration": 2.8,
        },
    )

    inter_placa = InteractableObject(
        "placa",
        placa_corredor,
        (88, 110, 120),
        (110, 145, 160),
        {
            "type": "message",
            "text": "corredor da ala leste",
            "duration": 2.8,
        },
    )

    inter_pergaminho = InteractableObject(
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

    # Coroa vermelha (pickup) sobre a estatua gata
    coroa_pickup = [(280, 225), (380, 225), (380, 280), (280, 280)]
    inter_coroa = InteractableObject(
        "coroa_vermelha",
        coroa_pickup,
        None,
        None,
        {
            "type": "pickup",
            "item": "coroa_vermelha",
            "mensagem": "Voce pegou a Coroa Vermelha!",
        },
        show_border=False,
    )

    sala1 = {
        "nome": "sala_1",
        "background_texture": "world/quarto.png",
        "background_zoom": 1.0,
        "poligonos": [
            poligono_chao(
                [(sala1_x_min, sala1_y_min), (sala1_x_max, sala1_y_min), (sala1_x_max, sala1_y_max), (sala1_x_min, sala1_y_max)],
                (120, 80, 40),
                (100, 65, 30),
            ),
            inter_bilhete.as_draw_item(),
        ],
        "portas_visuais": [
            # Porta invisivel: apenas vao entre as paredes + trigger de transicao.
        ],
        "interactables": [inter_bilhete, inter_coroa],
        "lights": [
            # Luz fixa sobre a estatua gata.
            {"x": 310, "y": 180, "rx": 54, "ry": 42, "steps": 24},
        ],
        "colliders": [
            # Parede superior (faixa de pedra no topo do PNG)
            colisao_estatica(1, 8, 995, 225),
            # Parede lateral esquerda
            colisao_estatica(0, 173, 43, 547),
            # Parede lateral direita
            colisao_estatica(957, 173, 43, 547),
            # Parede inferior com vão da porta
            colisao_estatica(0, 720, 460, 30),
            colisao_estatica(540, 720, 460, 30),
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
            colisao_estatica(291, 589, 39, 134),
            # Poltrona
            colisao_estatica(232, 351, 76, 50),
            colisao_estatica(182, 498, 84, 68),
            colisao_estatica(172, 357, 47, 135),
            # Armário (canto superior esquerdo)
            colisao_estatica(35, 32, 187, 282),
            # Cama (lado direito)
            colisao_estatica(701, 180, 111, 237),
        ],
        "transicoes": [
            {
                "trigger": pygame.Rect(porta_sala1_x_min, porta_sala1_y - 10, porta_sala1_x_max - porta_sala1_x_min, 42),
                "target": "corredor",
                "spawn": (500, 290),
            }
        ],
    }

    corredor = {
        "nome": "corredor",
        "background_texture": "texturas/cenario/chaointeiro.png",
        "poligonos": [
            poligono_chao([(0, 250), (1000, 250), (1000, 500), (0, 500)], (90, 88, 85), (120, 118, 112)),
            ([(0, 0), (460, 0), (460, 180), (0, 180)], (45, 48, 58), (60, 64, 76)),
            ([(540, 0), (1000, 0), (1000, 180), (540, 180)], (45, 48, 58), (60, 64, 76)),
            ([(0, 500), (1000, 500), (1000, 750), (0, 750)], (45, 48, 58), (60, 64, 76)),
            inter_placa.as_draw_item(),
        ],
        "portas_visuais": [
            # Entrada para sala_1 invisivel: mantem somente abertura geometrica.
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

    sala2 = {
        "nome": "sala_2",
        "background_texture": "texturas/cenario/chaointeiro.png",
        "poligonos": [
            poligono_chao([(0, 120), (1000, 120), (1000, 750), (0, 750)], (105, 78, 58), (90, 62, 44)),
            ([(0, 0), (1000, 0), (1000, 120), (0, 120)], (74, 70, 92), (98, 94, 118)),
            ([(620, 420), (760, 420), (760, 560), (620, 560)], (52, 55, 72), (75, 80, 100)),
            inter_pergaminho.as_draw_item(),
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

    return {
        "sala_1": sala1,
        "corredor": corredor,
        "sala_2": sala2,
    }