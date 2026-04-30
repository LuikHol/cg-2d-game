import pygame


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
        xs = [p[0] for p in poligono]
        ys = [p[1] for p in poligono]
        esquerda = int(min(xs) - margem)
        topo = int(min(ys) - margem)
        largura = int(max(xs) - min(xs) + 2 * margem)
        altura = int(max(ys) - min(ys) + 2 * margem)
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