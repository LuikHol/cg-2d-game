import pygame

from render.geometry_utils import polygon_centroid
from render.geometry_utils import polygon_bounds


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
        esquerda, topo, direita, base = polygon_bounds(poligono, margem=margem)
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
    def __init__(self, name, polygon, fill_color, border_color, action, texture_key=None, show_border=True):
        self.name = name
        self.polygon = polygon
        self.fill_color = fill_color
        self.border_color = border_color
        self.texture_key = texture_key
        self.show_border = show_border
        self.component = ComponenteInteragivel.do_poligono(polygon, action)

    def get_center(self):
        x, y = polygon_centroid(self.polygon)
        return int(x), int(y)

    def como_item_desenhavel(self):
        return {
            "polygon": self.polygon,
            "fill_color": self.fill_color,
            "border_color": self.border_color,
            "texture_key": self.texture_key,
            "show_border": self.show_border,
        }