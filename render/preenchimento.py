from render.pixel import setPixel
from render.scanline_core import iter_scanline_spans


# Cache de spans scanline - armazena resultado da rasterização geométrica
class CacheScanlineSpans:
    def __init__(self):
        self.cache = {}
    
    def obter_chave(self, pontos):
        """Cria chave de cache baseada apenas em geometria (pontos)."""
        return tuple(pontos)
    
    def obter_spans_cacheados(self, pontos):
        """Retorna spans cacheados se existirem."""
        chave = self.obter_chave(pontos)
        return self.cache.get(chave)
    
    def cachear_spans(self, pontos, spans):
        """Armazena resultado de scanline em cache."""
        chave = self.obter_chave(pontos)
        self.cache[chave] = spans
    
    def limpar(self):
        """Limpa todo o cache."""
        self.cache.clear()

# Instancia global do cache
_cache_scanline = CacheScanlineSpans()


def interpola_cor(c0, c1, t):
    """Interpola duas cores RGB(A) no fator t em [0, 1]."""
    t = max(0.0, min(1.0, float(t)))
    n = min(len(c0), len(c1))
    return tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(n))


def preencher_scanline(superficie, pontos, cor):
    """Preenche poligono - cache de spans rasterização geométrica."""
    # Tenta recuperar spans do cache
    spans_cacheados = _cache_scanline.obter_spans_cacheados(pontos)
    
    if spans_cacheados is None:
        # Se não está em cache, calcula spans e armazena
        spans = list(iter_scanline_spans(pontos))
        _cache_scanline.cachear_spans(pontos, spans)
    else:
        # Usa spans cacheados
        spans = spans_cacheados
    
    # Preenche pixels com spans (sempre via setPixel para compliance)
    for y, x_ini, x_fim, _y_min, _y_max in spans:
        for x in range(x_ini, x_fim + 1):
            setPixel(superficie, x, y, cor)


# Alias para compatibilidade
scanline_fill = preencher_scanline


def scanline_texture(surface, pontos, textura):
    ys = [p[1] for p in pontos]
    y_min = int(min(ys))
    y_max = int(max(ys))

    largura_tex = textura.get_width()
    altura_tex = textura.get_height()

    for y, x_ini, x_fim, _scan_y_min, _scan_y_max in iter_scanline_spans(pontos):
        for x in range(x_ini, x_fim + 1):
            u = (x - x_ini) / max(1, (x_fim - x_ini))
            v = (y - y_min) / max(1, (y_max - y_min))

            tex_x = int(u * (largura_tex - 1))
            tex_y = int(v * (altura_tex - 1))

            cor = textura.get_at((tex_x, tex_y))
            setPixel(surface, x, y, cor)


def scanline_fill_gradiente(surface, pontos, cores):
    """Preenche poligono interpolando cores por vertice via scanline."""
    if not pontos or not cores or len(pontos) != len(cores):
        return

    ys = [p[1] for p in pontos]
    y_min = int(min(ys))
    y_max = int(max(ys))
    n = len(pontos)

    for y in range(y_min, y_max):
        intersecoes = []

        for i in range(n):
            x0, y0 = pontos[i]
            x1, y1 = pontos[(i + 1) % n]
            c0 = cores[i]
            c1 = cores[(i + 1) % n]

            if y0 == y1:
                continue

            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0
                c0, c1 = c1, c0

            if y < y0 or y >= y1:
                continue

            t = (y - y0) / (y1 - y0)
            x = x0 + t * (x1 - x0)
            cor_y = interpola_cor(c0, c1, t)
            intersecoes.append((x, cor_y))

        intersecoes.sort(key=lambda item: item[0])

        for i in range(0, len(intersecoes), 2):
            if i + 1 >= len(intersecoes):
                continue

            x_ini, cor_ini = intersecoes[i]
            x_fim, cor_fim = intersecoes[i + 1]
            if x_fim == x_ini:
                continue

            for x in range(int(x_ini), int(x_fim) + 1):
                t = (x - x_ini) / (x_fim - x_ini)
                cor = interpola_cor(cor_ini, cor_fim, t)
                setPixel(surface, x, y, cor)


def limpar_cache_scanline():
    """Limpa cache de spans scanline - chamar ao trocar salas para economizar memória."""
    _cache_scanline.limpar()
