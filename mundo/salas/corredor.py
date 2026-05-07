import pygame

from objetos.componentes import ComponenteColisaoEstatica
from objetos.objeto_interagivel import ObjetoInterativo
from mundo.salas.utils import foreground_img, poligono_de_chao


def criar_corredor():
    colisao_estatica = ComponenteColisaoEstatica

    pote_corredor = [(1358, 246), (1382, 246), (1382, 268), (1358, 268)]

    inter_pote = ObjetoInterativo(
        "pote",
        pote_corredor,
        None,
        None,
        {
            "tipo": "coletar",
            "item": "pote_mel",
            "mensagem": "Voce pegou um Pote de Mel!",
        },
        mostrar_borda=False,
    )

    # Layout do corredor:
    # Teto y=0..180, chão y=600..750, corredor passável y=180..600
    # Porta sala_1: x=460..540, abertura vertical menor (y=130..180)
    # Quarto da rainha: y=350..430 na parede esquerda
    # Porta sala_2: y=350..430 (abertura vertical menor)
    # Biblioteca: x=130..210, abertura vertical menor (y=600..680)

    # Teto em duas partes com vão para porta sala_1
    parede_teto_esq = [(0, 0), (460, 0), (460, 180), (0, 180)]
    parede_teto_dir = [(540, 0), (1600, 0), (1600, 180), (540, 180)]
    # Tampa superior do vão da sala_1 para reduzir altura vertical da abertura
    parede_teto_centro = [(460, 0), (540, 0), (540, 130), (460, 130)]

    # Chão com vao no canto inferior esquerdo para a biblioteca
    parede_chao_esq = [(0, 600), (130, 600), (130, 750), (0, 750)]
    parede_chao_dir = [(210, 600), (1600, 600), (1600, 750), (210, 750)]
    # Tampa inferior do vão da biblioteca para reduzir altura vertical da abertura
    parede_chao_centro = [(130, 680), (210, 680), (210, 750), (130, 750)]

    # Parede lateral esq com vao para o quarto da rainha
    parede_esq_cima = [(0, 180), (12, 180), (12, 350), (0, 350)]
    parede_esq_baixo = [(0, 430), (12, 430), (12, 600), (0, 600)]

    # Parede lateral dir com vão para porta sala_2
    parede_dir_cima  = [(1588, 180), (1600, 180), (1600, 350), (1588, 350)]
    parede_dir_baixo = [(1588, 430), (1600, 430), (1600, 600), (1588, 600)]

    COR_PAREDE = (30, 30, 35)
    COR_BORDA  = (55, 30, 60)

    def parede(pts):
        return {"poligono": pts, "cor_preenchimento": COR_PAREDE, "cor_borda": COR_BORDA, "mostrar_borda": True}

    return {
        "nome": "corredor",
        "textura_fundo": "texturas/cenario/corredor/chaocorredor1.png",
        "limites_fundo": (0, 0, 1600, 750),
        "limites_camera": (0, 0, 1600, 750),
        "margem_viewport": 60,
        "escala_fundo": 1.5,
        "largura_tile_mundo": 1600,
        "poligonos": [
            parede(parede_teto_esq),
            parede(parede_teto_dir),
            parede(parede_teto_centro),
            parede(parede_chao_esq),
            parede(parede_chao_dir),
            parede(parede_chao_centro),
            parede(parede_esq_cima),
            parede(parede_esq_baixo),
            parede(parede_dir_cima),
            parede(parede_dir_baixo),
        ],
        "portas_visuais": [],
        "interagiveis": [inter_pote],
        "primeiro_plano": [
            foreground_img("texturas/objetos/urso.png", 1321, 76, 92, 201, escala=2.5, draw_above_player=False),
        ],
        "luzes": [
            {"x": 1341, "y": 127, "rx": 55, "ry": 68, "steps": 24},
        ],
        "colidores": [
            # Urso Estatua
            colisao_estatica(1331, 41, 79, 208),
            colisao_estatica(0, 0, 460, 180),
            colisao_estatica(540, 0, 1060, 180),
            colisao_estatica(460, 0, 80, 130),
            colisao_estatica(0, 600, 130, 150),
            colisao_estatica(210, 600, 1390, 150),
            colisao_estatica(130, 680, 80, 70),
            colisao_estatica(0, 180, 12, 170),
            colisao_estatica(0, 430, 12, 170),
            colisao_estatica(1588, 180, 12, 170),
            colisao_estatica(1588, 430, 12, 170),
            # Porta sala_2 (removida dinamicamente quando puzzle e resolvido)
            colisao_estatica(1588, 350, 12, 80),
        ],
        "transicoes": [
            {
                "gatilho": pygame.Rect(460, 130, 80, 20),
                "destino": "sala_1",
                "posicao_spawn": (500, 650),
            },
            {
                "gatilho": pygame.Rect(0, 350, 12, 80),
                "destino": "quarto_rainha",
                "posicao_spawn": (959, 430),
            },
            {
                "gatilho": pygame.Rect(1588, 350, 12, 80),
                "destino": "sala_2",
                "posicao_spawn": (40, 375),
            },
            {
                "gatilho": pygame.Rect(130, 600, 80, 20),
                "destino": "biblioteca",
                "posicao_spawn": (500, 260),
            },
        ],
    }
