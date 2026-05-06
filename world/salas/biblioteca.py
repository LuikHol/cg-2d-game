import pygame

from objects.components import ComponenteColisaoEstatica
from objects.objeto_interagivel import ObjetoInterativo
from render.collectible_sprites import get_collectible_sprite
from world.salas.utils import poligono_de_chao, foreground_img, foreground_surface


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

    livro_pickup = [(318, 640), (358, 640), (358, 700), (318, 700)]
    livro_coala = [(198, 348), (238, 348), (238, 388), (198, 388)]

    inter_livro_laranja = ObjetoInterativo(
        "livro_laranja",
        livro_pickup,
        None,
        None,
        {
            "type": "pickup",
            "item": "livro_laranja",
            "mensagem": "Voce pegou o Livro Laranja!",
        },
        show_border=False,
    )

    inter_livro_coala = ObjetoInterativo(
        "livro_coala",
        livro_coala,
        (120, 80, 40),
        (160, 110, 55),
        {
            "type": "paper",
            "title": "",
            "lines": [],
            "texture_path": "texturas/documentos/livro_coala.png",
        },
        show_border=False,
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
        ],
        "portas_visuais": [],
        "interactables": [inter_livro_laranja, inter_livro_coala],
        "foreground": [
            foreground_img("texturas/objetos/estante_livros1.png", 575, 388, 189, 221, escala=1.19),
            foreground_img("texturas/objetos/estante_livros3.png", 755, 388, 189, 221, escala=1.19),
            foreground_img("texturas/objetos/coala.png", 301, 520, 81, 169, escala=2.7),
        ],
        "lights": [
            {"x": 344, "y": 598, "rx": 54, "ry": 42, "steps": 24},
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
            # Armários 1 (topo esquerdo)
            colisao_estatica(61, 89, 363, 218),
            # Armários 2 (lateral esquerda)
            colisao_estatica(14, 91, 47, 505),
            # Armários 3 (topo direito)
            colisao_estatica(570, 98, 418, 218),
            # Armários 4 (lateral direita)
            colisao_estatica(936, 97, 52, 509),
            # Armários 5 (centro-baixo direito)
            colisao_estatica(568, 540, 417, 76),
            # Estátua coala
            colisao_estatica(307, 580, 68, 90),
            # Mesa
            colisao_estatica(153, 357, 130, 143),
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
                "spawn": (169, 580),
            }
        ],
    }
