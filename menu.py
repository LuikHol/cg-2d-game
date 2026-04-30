import math
from pathlib import Path

import pygame

from configs.menu_config import (
    ALTURA,
    COR_BOTAO,
    COR_BOTAO_BORDA,
    COR_BOTAO_HOVER,
    COR_FUNDO,
    COR_TEXTO,
    COR_TITULO,
    FONTE_BOTAO,
    FONTE_TITULO,
    QUADROS_POR_SEGUNDO,
    LARGURA,
    TITULO_MENU,
)
from render.pixel import setPixel
from render.scanline import scanline_fill

ANIMACOES_MENU = None
CACHE_COROAS = {}


def retangulo_para_poligono(rect):
    return [
        (rect.left, rect.top),
        (rect.right, rect.top),
        (rect.right, rect.bottom),
        (rect.left, rect.bottom),
    ]


def desenhar_borda_retangulo(surface, rect, cor):
    for x in range(rect.left, rect.right):
        setPixel(surface, x, rect.top, cor)
        setPixel(surface, x, rect.bottom - 1, cor)
    for y in range(rect.top, rect.bottom):
        setPixel(surface, rect.left, y, cor)
        setPixel(surface, rect.right - 1, y, cor)


def desenhar_painel(surface, rect, cor_preenchimento, cor_borda):
    scanline_fill(surface, retangulo_para_poligono(rect), cor_preenchimento)
    desenhar_borda_retangulo(surface, rect, cor_borda)


def carregar_quadros_da_faixa(caminho_imagem, altura_alvo):
    faixa = pygame.image.load(str(caminho_imagem)).convert_alpha()
    quantidade_quadros = 4
    largura_quadro = faixa.get_width() // quantidade_quadros
    altura_quadro = faixa.get_height()

    quadros_originais = []
    for indice in range(quantidade_quadros):
        retangulo = pygame.Rect(indice * largura_quadro, 0, largura_quadro, altura_quadro)
        quadros_originais.append(faixa.subsurface(retangulo).copy())

    recortes = []
    largura_max_recorte = 1
    altura_max_recorte = 1
    for quadro in quadros_originais:
        limites = quadro.get_bounding_rect(min_alpha=1)
        if limites.width <= 0 or limites.height <= 0:
            limites = pygame.Rect(0, 0, largura_quadro, altura_quadro)
        else:
            folga = 1
            x = max(0, limites.x - folga)
            y = max(0, limites.y - folga)
            w = min(largura_quadro - x, limites.width + (2 * folga))
            h = min(altura_quadro - y, limites.height + (2 * folga))
            limites = pygame.Rect(x, y, w, h)

        recorte = quadro.subsurface(limites).copy()
        recortes.append(recorte)
        largura_max_recorte = max(largura_max_recorte, recorte.get_width())
        altura_max_recorte = max(altura_max_recorte, recorte.get_height())

    escala = altura_alvo / max(1, altura_max_recorte)
    largura_canvas_alvo = max(1, int(largura_max_recorte * escala))
    altura_canvas_alvo = max(1, int(altura_max_recorte * escala))

    quadros = []
    for recorte in recortes:
        quadro_escalado = pygame.transform.scale(
            recorte,
            (
                max(1, int(recorte.get_width() * escala)),
                max(1, int(recorte.get_height() * escala)),
            ),
        )
        canvas = pygame.Surface((largura_canvas_alvo, altura_canvas_alvo), pygame.SRCALPHA)
        pos_x = (largura_canvas_alvo - quadro_escalado.get_width()) // 2
        pos_y = altura_canvas_alvo - quadro_escalado.get_height()
        canvas.blit(quadro_escalado, (pos_x, pos_y))
        quadros.append(canvas)
    return quadros


def normalizar_animacoes(quadros_baixo, quadros_cima, quadros_direita, quadros_esquerda):
    todos = quadros_baixo + quadros_cima + quadros_direita + quadros_esquerda
    largura_max = max(q.get_width() for q in todos)
    altura_max = max(q.get_height() for q in todos)

    def padronizar(grupo):
        saida = []
        for quadro in grupo:
            w, h = quadro.get_size()
            canvas = pygame.Surface((largura_max, altura_max), pygame.SRCALPHA)
            canvas.blit(quadro, ((largura_max - w) // 2, altura_max - h))
            saida.append(canvas)
        return saida

    return (
        padronizar(quadros_baixo),
        padronizar(quadros_cima),
        padronizar(quadros_direita),
        padronizar(quadros_esquerda),
    )


def obter_animacoes_menu():
    global ANIMACOES_MENU
    if ANIMACOES_MENU is not None:
        return ANIMACOES_MENU

    altura_alvo = 190
    faixa_baixo = Path("texturas/personagem/menino1.png")
    faixa_lado = Path("texturas/personagem/menino2.png")
    faixa_cima = Path("texturas/personagem/menino3.png")

    if faixa_baixo.exists() and faixa_lado.exists() and faixa_cima.exists():
        quadros_baixo = carregar_quadros_da_faixa(faixa_baixo, altura_alvo)
        quadros_direita = carregar_quadros_da_faixa(faixa_lado, altura_alvo)
        quadros_cima = carregar_quadros_da_faixa(faixa_cima, altura_alvo)
        quadros_esquerda = [pygame.transform.flip(q, True, False) for q in quadros_direita]

        quadros_baixo, quadros_cima, quadros_direita, quadros_esquerda = normalizar_animacoes(
            quadros_baixo,
            quadros_cima,
            quadros_direita,
            quadros_esquerda,
        )

        ANIMACOES_MENU = {
            "down": quadros_baixo,
            "up": quadros_cima,
            "right": quadros_direita,
            "left": quadros_esquerda,
        }
        return ANIMACOES_MENU

    # Fallback visual caso os arquivos nao existam.
    fallback = pygame.Surface((96, 140), pygame.SRCALPHA)
    scanline_fill(
        fallback,
        [(22, 24), (74, 24), (74, 120), (22, 120)],
        (112, 100, 196),
    )
    ANIMACOES_MENU = {"down": [fallback] * 4, "up": [fallback] * 4, "right": [fallback] * 4, "left": [fallback] * 4}
    return ANIMACOES_MENU


def obter_coroa(tamanho_pixel=4):
    chave = max(1, int(tamanho_pixel))
    if chave in CACHE_COROAS:
        return CACHE_COROAS[chave]

    padrao = [
        "00100100",
        "00111100",
        "01111110",
        "11111111",
        "01111110",
        "00111100",
    ]
    largura = len(padrao[0]) * chave
    altura = len(padrao) * chave
    surface = pygame.Surface((largura, altura), pygame.SRCALPHA)
    dourado = (246, 210, 74, 255)
    dourado_escuro = (179, 128, 26, 255)
    joia = (220, 70, 80, 255)

    for py, linha in enumerate(padrao):
        for px, valor in enumerate(linha):
            if valor == "0":
                continue
            cor = dourado
            if py >= len(padrao) - 2:
                cor = dourado_escuro
            if (px, py) in {(3, 2), (4, 2)}:
                cor = joia
            inicio_x = px * chave
            inicio_y = py * chave
            for dy in range(chave):
                for dx in range(chave):
                    setPixel(surface, inicio_x + dx, inicio_y + dy, cor)

    CACHE_COROAS[chave] = surface
    return surface


def desenhar_personagem_menu(surface, tempo_segundos):
    animacoes = obter_animacoes_menu()
    indice_frame = int(tempo_segundos * 6.0) % 4
    sprite = animacoes["down"][indice_frame % len(animacoes["down"])]
    coroa = obter_coroa(5)

    centro_x = int(LARGURA * 0.78)
    base_y = 300 + int(math.sin(tempo_segundos * 2.2) * 6)
    sprite_rect = sprite.get_rect(midbottom=(centro_x, base_y))

    surface.blit(sprite, sprite_rect)

    oscilacao_coroa = int(math.sin(tempo_segundos * 3.0) * 7)
    coroa_rect = coroa.get_rect(
        midbottom=(centro_x, sprite_rect.top + coroa.get_height() + oscilacao_coroa - 8)
    )
    surface.blit(coroa, coroa_rect)


def menu_principal():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Menu Principal")
    relogio = pygame.time.Clock()

    fonte_titulo = pygame.font.SysFont(FONTE_TITULO, 54, bold=True)
    fonte_botao = pygame.font.SysFont(FONTE_BOTAO, 32, bold=True)

    botoes = [
        {"rotulo": "Jogar", "acao": "jogar", "rect": pygame.Rect(90, 276, 260, 58)},
        {"rotulo": "Sair", "acao": "sair", "rect": pygame.Rect(90, 348, 260, 58)},
    ]
    indice_selecionado = 0
    rodando = True

    while rodando:
        _dt = relogio.tick(QUADROS_POR_SEGUNDO) / 1000.0
        tempo = pygame.time.get_ticks() / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_w, pygame.K_UP):
                    indice_selecionado = (indice_selecionado - 1) % len(botoes)
                elif evento.key in (pygame.K_s, pygame.K_DOWN):
                    indice_selecionado = (indice_selecionado + 1) % len(botoes)
                elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    acao = botoes[indice_selecionado]["acao"]
                    if acao == "jogar":
                        return "jogar"
                    pygame.quit()
                    return "sair"
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return "sair"
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for indice, botao in enumerate(botoes):
                    if botao["rect"].collidepoint(evento.pos):
                        indice_selecionado = indice
                        if botao["acao"] == "jogar":
                            return "jogar"
                        pygame.quit()
                        return "sair"

        tela.fill(COR_FUNDO)

        titulo = fonte_titulo.render(TITULO_MENU, True, COR_TITULO)
        tela.blit(titulo, titulo.get_rect(midleft=(88, 106)))

        desenhar_personagem_menu(tela, tempo)

        for indice, botao in enumerate(botoes):
            esta_hover = botao["rect"].collidepoint(mouse_pos)
            ativo = esta_hover or indice == indice_selecionado
            cor_botao = COR_BOTAO_HOVER if ativo else COR_BOTAO
            desenhar_painel(tela, botao["rect"], cor_botao, COR_BOTAO_BORDA)
            texto = fonte_botao.render(botao["rotulo"], True, COR_TEXTO)
            tela.blit(texto, texto.get_rect(center=botao["rect"].center))

        pygame.display.flip()

    pygame.quit()
    return "sair"


if __name__ == "__main__":
    menu_principal()
