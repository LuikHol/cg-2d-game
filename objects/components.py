import pygame


class RigidbodyComponent:
    def __init__(self):
        self.velocity = pygame.Vector2(0.0, 0.0)


class ColliderComponent:
    def __init__(self, width, height, offset_x=0.0, offset_y=0.0):
        self.width = float(width)
        self.height = float(height)
        self.offset = pygame.Vector2(offset_x, offset_y)

    def get_rect_from_center(self, center_x, center_y):
        cx = center_x + self.offset.x
        cy = center_y + self.offset.y
        left = int(round(cx - self.width / 2.0))
        top = int(round(cy - self.height / 2.0))
        return pygame.Rect(left, top, int(round(self.width)), int(round(self.height)))


class ComponenteColisaoEstatica:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(int(x), int(y), int(width), int(height))

    def get_rect(self):
        return self.rect


def collider_to_rect(collider):
    if isinstance(collider, pygame.Rect):
        return collider
    if hasattr(collider, "get_rect"):
        return collider.get_rect()
    if hasattr(collider, "rect"):
        return collider.rect
    raise TypeError("Unsupported collider type")


def resolve_axis_aligned_motion(rect, move_x, move_y, static_colliders):
    # Resolve movimento por eixo para permitir "slide" natural nas paredes.
    rect = rect.copy()

    if move_x != 0:
        rect.x += int(round(move_x))
        for collider in static_colliders:
            wall = collider_to_rect(collider)
            if rect.colliderect(wall):
                if move_x > 0:
                    rect.right = wall.left
                else:
                    rect.left = wall.right

    if move_y != 0:
        rect.y += int(round(move_y))
        for collider in static_colliders:
            wall = collider_to_rect(collider)
            if rect.colliderect(wall):
                if move_y > 0:
                    rect.bottom = wall.top
                else:
                    rect.top = wall.bottom

    return rect