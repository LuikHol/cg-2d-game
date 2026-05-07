import pygame

from objetos.componentes import ComponenteColisaoEstatica


def criar_creditos():
    """
    Sala de créditos: uma sala vazia que apenas carrega a tela de créditos.
    """
    colisao_estatica = ComponenteColisaoEstatica

    return {
        "nome": "creditos",
        "textura_fundo": "texturas/cenario/corredor/chaocorredor2.png",
        "zoom_fundo": 1.0,
        "poligonos": [],
        "portas_visuais": [],
        "interagiveis": [],
        "primeiro_plano": [],
        "luzes": [],
        "colisores": [
            colisao_estatica(0, 0, 1000, 750),
        ],
        "transicoes": [],
    }
