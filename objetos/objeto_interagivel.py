import pygame

from render.utils_geometrias import centroide_poligono
from render.utils_geometrias import limites_poligono


class ComponenteInteragivel:
    """Componente base de interacao por area no mundo."""

    def __init__(self, retangulo_area, acao, tecla=pygame.K_e):
        self.retangulo_area = retangulo_area
        self.acao = acao
        self.tecla = tecla
        self._estava_pressionado = False

    @classmethod
    def do_poligono(cls, poligono, acao, tecla=pygame.K_e, margem=4):
        """Cria componente a partir do bounding box de um poligono."""
        esquerda, topo, direita, base = limites_poligono(poligono, margem=margem)
        largura = int(direita - esquerda)
        altura = int(base - topo)
        return cls(pygame.Rect(esquerda, topo, largura, altura), acao, tecla)

    def pode_interagir(self, retangulo_ator):
        """Retorna True se o ator colide com a area interativa."""
        return retangulo_ator.colliderect(self.retangulo_area)

    def tentar_interagir(self, teclas, retangulo_ator):
        """Dispara a acao apenas na borda de subida da tecla."""
        pressionado = bool(teclas[self.tecla])
        acionado = False

        if pressionado and not self._estava_pressionado and self.pode_interagir(retangulo_ator):
            acionado = True

        self._estava_pressionado = pressionado
        return acionado, self.acao if acionado else None


class ObjetoInterativo:
    def __init__(self, nome, poligono, cor_preenchimento, cor_borda, acao, chave_textura=None, mostrar_borda=True):
        self.name = nome
        self.polygon = poligono
        self.fill_color = cor_preenchimento
        self.border_color = cor_borda
        self.texture_key = chave_textura
        self.show_border = mostrar_borda
        self.component = ComponenteInteragivel.do_poligono(poligono, acao)

    def obter_centro(self):
        x, y = centroide_poligono(self.polygon)
        return int(x), int(y)

    def como_item_desenhavel(self):
        return {
            "poligono": self.polygon,
            "cor_preenchimento": self.fill_color,
            "cor_borda": self.border_color,
            "chave_textura": self.texture_key,
            "mostrar_borda": self.show_border,
        }