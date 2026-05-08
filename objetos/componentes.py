import pygame


class ComponenteRigidbody:
    def __init__(self):
        self.velocidade = pygame.Vector2(0.0, 0.0)


class ComponenteColisao:
    def __init__(self, largura, altura, offset_x=0.0, offset_y=0.0):
        self.largura = float(largura)
        self.altura = float(altura)
        self.deslocamento = pygame.Vector2(offset_x, offset_y)

    def obter_rect_do_centro(self, center_x, center_y):
        cx = center_x + self.deslocamento.x
        cy = center_y + self.deslocamento.y
        left = int(round(cx - self.largura / 2.0))
        top = int(round(cy - self.altura / 2.0))
        return pygame.Rect(left, top, int(round(self.largura)), int(round(self.altura)))


class ComponenteColisaoEstatica:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(int(x), int(y), int(width), int(height))

    def get_rect(self):
        return self.rect


def colisao_para_rect(collider):
    if isinstance(collider, pygame.Rect):
        return collider
    if hasattr(collider, "get_rect"):
        return collider.get_rect()
    if hasattr(collider, "rect"):
        return collider.rect
    raise TypeError("Unsupported collider type")


def resolver_movimento_alinhado(rect, move_x, move_y, static_colliders):
    # Resolve movimento por eixo para permitir "slide" natural nas paredes.
    rect = rect.copy()

    if move_x != 0:
        rect.x += int(round(move_x))
        for collider in static_colliders:
            wall = colisao_para_rect(collider)
            if rect.colliderect(wall):
                if move_x > 0:
                    rect.right = wall.left
                else:
                    rect.left = wall.right

    if move_y != 0:
        rect.y += int(round(move_y))
        for collider in static_colliders:
            wall = colisao_para_rect(collider)
            if rect.colliderect(wall):
                if move_y > 0:
                    rect.bottom = wall.top
                else:
                    rect.top = wall.bottom

    return rect