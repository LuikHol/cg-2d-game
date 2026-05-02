import pygame
from render.pixel import setPixel
from render.preenchimento import scanline_fill


def _rect_para_poligono(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def _desenhar_borda(surface, x, y, w, h, cor):
    for px in range(x, x + w):
        setPixel(surface, px, y, cor)
        setPixel(surface, px, y + h - 1, cor)
    for py in range(y, y + h):
        setPixel(surface, x, py, cor)
        setPixel(surface, x + w - 1, py, cor)


class InventarioHUD:
    def __init__(self, fonte, largura=320, altura=220):
        self.fonte = fonte
        self.aberto = False
        self.largura = largura
        self.altura = altura
        self.indice_selecionado = 0

    def alternar(self):
        self.aberto = not self.aberto

    def mover_selecao(self, delta, inventario):
        itens = inventario.listar() if inventario else []
        if not itens:
            return
        self.indice_selecionado = (self.indice_selecionado + delta) % len(itens)

    def get_item_selecionado(self, inventario):
        itens = inventario.listar() if inventario else []
        if not itens:
            return None
        self.indice_selecionado = min(self.indice_selecionado, len(itens) - 1)
        return itens[self.indice_selecionado]

    def desenhar_hint(self, surface, viewport=None):
        vx0, vy0 = (10, 10)
        if viewport:
            vx0, vy0 = viewport[0], viewport[1]
        texto = self.fonte.render("R: inventario", True, (200, 200, 200))
        surface.blit(texto, (vx0 + 10, vy0 + 34))

    def desenhar(self, surface, inventario, viewport=None):
        if not self.aberto:
            return

        itens = inventario.listar() if inventario else []
        if viewport:
            vx0, vy0, vx1, vy1 = viewport
            vw = vx1 - vx0
            vh = vy1 - vy0
            x = vx0 + (vw - self.largura) // 2
            y = vy0 + (vh - self.altura) // 2
        else:
            sw = surface.get_width()
            sh = surface.get_height()
            x = (sw - self.largura) // 2
            y = (sh - self.altura) // 2

        scanline_fill(surface, _rect_para_poligono(x, y, self.largura, self.altura), (12, 12, 16))
        _desenhar_borda(surface, x, y, self.largura, self.altura, (220, 190, 120))
        _desenhar_borda(surface, x + 2, y + 2, self.largura - 4, self.altura - 4, (90, 76, 44))

        titulo = self.fonte.render("Inventario", True, (255, 220, 80))
        surface.blit(titulo, (x + 14, y + 12))

        if not itens:
            vazio = self.fonte.render("(vazio)", True, (170, 170, 170))
            surface.blit(vazio, (x + 14, y + 48))
        else:
            self.indice_selecionado = min(self.indice_selecionado, len(itens) - 1)
            linha_y = y + 48
            for idx, item in enumerate(itens[:7]):
                selecionado = idx == self.indice_selecionado
                cor = (255, 240, 100) if selecionado else (235, 235, 235)
                prefixo = "> " if selecionado else "  "
                texto_item = self.fonte.render(f"{prefixo}{item}", True, cor)
                surface.blit(texto_item, (x + 14, linha_y))
                linha_y += 24

        dica = self.fonte.render("W/S: selecionar", True, (150, 150, 150))
        surface.blit(dica, (x + 14, y + self.altura - 28))
