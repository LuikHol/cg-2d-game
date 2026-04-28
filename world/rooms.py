import pygame
from objects.components import StaticColliderComponent
from objects.interactable_object import InteractableObject


def build_rooms():
    sc = StaticColliderComponent
    sala1_xmin = 18
    sala1_xmax = 982
    sala1_ymin = 225
    sala1_ymax = 720
    porta_sala1_xmin = 460
    porta_sala1_xmax = 540
    porta_sala1_y = sala1_ymax

    def floor_polygon(pontos, fill_color, border_color):
        return {
            "polygon": pontos,
            "fill_color": fill_color,
            "border_color": border_color,
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

    sala1 = {
        "nome": "sala_1",
        "background_texture": "world/quarto.png",
        "background_zoom": 1.0,
        "poligonos": [
            floor_polygon(
                [(sala1_xmin, sala1_ymin), (sala1_xmax, sala1_ymin), (sala1_xmax, sala1_ymax), (sala1_xmin, sala1_ymax)],
                (120, 80, 40),
                (100, 65, 30),
            ),
            # Paredes laterais roxas
            ([(0, 225), (18, 225), (18, 750), (0, 750)], (77, 78, 143), (77, 78, 143)),
            ([(982, 225), (1000, 225), (1000, 750), (982, 750)], (77, 78, 143), (77, 78, 143)),
            # Parede inferior com vao da porta no centro
            ([(18, 690), (460, 690), (460, 750), (18, 750)], (77, 78, 143), (77, 78, 143)),
            ([(540, 690), (982, 690), (982, 750), (540, 750)], (77, 78, 143), (77, 78, 143)),
            ([(460, 720), (540, 720), (540, 750), (460, 750)], (30, 20, 45), (30, 20, 45)),
            inter_bilhete.as_draw_item(),
        ],
        "portas_visuais": [
            # Porta invisivel: apenas vao entre as paredes + trigger de transicao.
        ],
        "interactables": [inter_bilhete],
        "colliders": [
            sc(0, 0, 1000, 225),
            sc(0, 225, 18, 495),
            sc(982, 225, 18, 495),
            sc(18, 720, 442, 30),
            #parede inferior
            sc(537, 673, 463, 71),
            #colisões cama
            sc(612, 341, 117, 96),
            sc(601, 176, 132, 54),
            sc(517, 160, 49, 138),
        ],
        "transicoes": [
            {
                "trigger": pygame.Rect(porta_sala1_xmin, porta_sala1_y - 10, porta_sala1_xmax - porta_sala1_xmin, 42),
                "target": "corredor",
                "spawn": (500, 290),
            }
        ],
    }

    corredor = {
        "nome": "corredor",
        "background_texture": "texturas/cenario/chaointeiro.png",
        "poligonos": [
            floor_polygon([(0, 250), (1000, 250), (1000, 500), (0, 500)], (90, 88, 85), (120, 118, 112)),
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
            sc(0, 0, 460, 180),
            sc(540, 0, 460, 180),
            sc(0, 500, 1000, 250),
            sc(0, 0, 12, 750),
            sc(988, 0, 12, 320),
            sc(988, 440, 12, 310),
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
            floor_polygon([(0, 120), (1000, 120), (1000, 750), (0, 750)], (105, 78, 58), (90, 62, 44)),
            ([(0, 0), (1000, 0), (1000, 120), (0, 120)], (74, 70, 92), (98, 94, 118)),
            ([(620, 420), (760, 420), (760, 560), (620, 560)], (52, 55, 72), (75, 80, 100)),
            inter_pergaminho.as_draw_item(),
        ],
        "portas_visuais": [
            ([(0, 320), (16, 320), (16, 440), (0, 440)], (170, 125, 70), (220, 180, 110)),
        ],
        "interactables": [inter_pergaminho],
        "colliders": [
            sc(0, 0, 1000, 120),
            sc(984, 0, 16, 750),
            sc(0, 734, 1000, 16),
            sc(620, 420, 140, 140),
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