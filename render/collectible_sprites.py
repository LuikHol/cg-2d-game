import pygame

from render.pixel import setPixel

_sprite_cache = {}


def _desenhar_pattern(pattern, palette, pixel_size):
    largura = len(pattern[0]) * pixel_size
    altura = len(pattern) * pixel_size
    surf = pygame.Surface((largura, altura), pygame.SRCALPHA)

    for py, row in enumerate(pattern):
        for px, value in enumerate(row):
            cor = palette.get(value)
            if cor is None or cor[3] <= 0:
                continue
            for dy in range(pixel_size):
                for dx in range(pixel_size):
                    setPixel(surf, px * pixel_size + dx, py * pixel_size + dy, cor)

    return surf


def get_collectible_sprite(item_name, pixel_size=1):
    """Retorna sprite pixel-art em cache para itens coletaveis."""
    item = str(item_name)
    tamanho_pixel = max(1, int(pixel_size))
    chave = (item, tamanho_pixel)
    em_cache = _sprite_cache.get(chave)
    if em_cache is not None:
        return em_cache

    if item == "coroa_vermelha":
        pattern = [
            "1001001",
            "1011101",
            "1111111",
            "0111110",
            "0111110",
        ]
        palette = {
            "0": (0, 0, 0, 0),
            "1": (210, 40, 40, 255),
            "2": (140, 20, 20, 255),
            "3": (255, 200, 60, 255),
        }
        # Aplica variação de tom nas ultimas linhas e joia central.
        surf = pygame.Surface((len(pattern[0]) * tamanho_pixel, len(pattern) * tamanho_pixel), pygame.SRCALPHA)
        for py, row in enumerate(pattern):
            for px, value in enumerate(row):
                if value == "0":
                    continue
                cor = palette["1"] if py < len(pattern) - 2 else palette["2"]
                if (px, py) == (3, 1):
                    cor = palette["3"]
                for dy in range(tamanho_pixel):
                    for dx in range(tamanho_pixel):
                        setPixel(surf, px * tamanho_pixel + dx, py * tamanho_pixel + dy, cor)
    elif item == "pote_mel":
        pattern = [
            "0011100",
            "0122210",
            "1233321",
            "1233321",
            "1222221",
            "0111110",
        ]
        palette = {
            "0": (0, 0, 0, 0),
            "1": (104, 56, 22, 255),
            "2": (218, 132, 38, 255),
            "3": (250, 184, 72, 255),
        }
        surf = _desenhar_pattern(pattern, palette, tamanho_pixel)
    elif item == "livro_laranja":
        pattern = [
            "0111110",
            "1111111",
            "1122211",
            "1111111",
            "1122211",
            "1111111",
            "0111110",
        ]
        palette = {
            "0": (0, 0, 0, 0),
            "1": (210, 100, 15, 255),
            "2": (180, 30, 30, 255),
        }
        surf = _desenhar_pattern(pattern, palette, tamanho_pixel)
    else:
        raise ValueError(f"Unknown collectible sprite: {item}")

    _sprite_cache[chave] = surf
    return surf
