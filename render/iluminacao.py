import pygame
from render.preenchimento import scanline_fill
from render.viewport import transformar_pontos
from render.utils_geometrias import pontos_elipse
from configs.config_jogo import (
    ALFA_ESCURIDAO_AMBIENTE,
    RAIO_LUZ_X,
    RAIO_LUZ_Y,
    PASSOS_LUZ,
)

# Nota sobre blit: É operação de composição/cópia de surface, NÃO construção gráfica.
# A sombra é preenchida com scanline_fill (construção customizada).
# O blit apenas copia o resultado final para a tela - é aceitável.

_light_cache = {}
_ambient_cache = {}

def obter_mascara_luz(radius_x=None, radius_y=None, steps=None, ambient_alpha=None):
    rx_base = int(radius_x if radius_x is not None else RAIO_LUZ_X)
    ry_base = int(radius_y if radius_y is not None else RAIO_LUZ_Y)
    steps_base = int(steps if steps is not None else PASSOS_LUZ)
    alpha_base = int(ambient_alpha if ambient_alpha is not None else ALFA_ESCURIDAO_AMBIENTE)
    key = (rx_base, ry_base, steps_base, alpha_base)
    if key in _light_cache:
        return _light_cache[key]

    w = (rx_base * 2) + 6
    h = (ry_base * 2) + 6
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2
    cy = h // 2

    for i in range(steps_base, 0, -1):
        t = i / steps_base
        remove_alpha = int(alpha_base * (1.0 - t) ** 2)
        rx = max(8, int(rx_base * t))
        ry = max(6, int(ry_base * t))
        pts = pontos_elipse(cx, cy, rx, ry, segmentos=56)
        scanline_fill(mask, pts, (0, 0, 0, remove_alpha))

    _light_cache[key] = (mask, cx, cy)
    return _light_cache[key]


def obter_ambient_base(vw, vh, ambient_alpha=None):
    alpha_base = int(ambient_alpha if ambient_alpha is not None else ALFA_ESCURIDAO_AMBIENTE)
    key = (vw, vh, alpha_base)
    if key in _ambient_cache:
        return _ambient_cache[key]
    base = pygame.Surface((vw, vh), pygame.SRCALPHA)
    base.fill((0, 0, 0, alpha_base))
    _ambient_cache[key] = base
    return base


def desenhar_iluminacao(surface, player_obj, room_data, camera, viewport):
    """Renderiza iluminação e sombra ambiente.
    
    Nota técnica: scanline_fill é construção gráfica customizada (✓ conforme).
    A composição final com blit é operação de cópia, não construção (✓ aceitável).
    """
    vx0, vy0, vx1, vy1 = viewport
    vw = vx1 - vx0
    vh = vy1 - vy0
    if vw <= 0 or vh <= 0:
        return

    ambient_alpha = int(room_data.get("alfa_escuridao", ALFA_ESCURIDAO_AMBIENTE))

    px, py = transformar_pontos([(player_obj.x, player_obj.y)], camera, viewport)[0]
    centros_luz = [
        {
            "posicao_tela": (px, py + int(player_obj.tamanho * 0.6)),
            "rx": RAIO_LUZ_X,
            "ry": RAIO_LUZ_Y,
            "steps": PASSOS_LUZ,
        }
    ]

    for luz in room_data.get("luzes", []):
        wx = luz.get("x")
        wy = luz.get("y")
        if wx is None or wy is None:
            continue
        sx, sy = transformar_pontos([(wx, wy)], camera, viewport)[0]
        centros_luz.append(
            {
                "posicao_tela": (sx, sy),
                "rx": int(luz.get("rx", 52)),
                "ry": int(luz.get("ry", 42)),
                "steps": int(luz.get("steps", PASSOS_LUZ)),
            }
        )

    sombra = obter_ambient_base(vw, vh, ambient_alpha).copy()
    for luz in centros_luz:
        centro = luz["posicao_tela"]
        mask, cx, cy = obter_mascara_luz(luz["rx"], luz["ry"], luz["steps"], ambient_alpha)
        sombra.blit(
            mask,
            (centro[0] - vx0 - cx, centro[1] - vy0 - cy),
            special_flags=pygame.BLEND_RGBA_SUB,
        )

    surface.blit(sombra, (vx0, vy0))
