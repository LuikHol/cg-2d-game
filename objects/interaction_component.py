import pygame


class InteractableComponent:
    def __init__(self, area_rect, action, key=pygame.K_e):
        self.area_rect = area_rect
        self.action = action
        self.key = key
        self._was_pressed = False

    @classmethod
    def from_polygon(cls, polygon, action, key=pygame.K_e, padding=4):
        xs = [p[0] for p in polygon]
        ys = [p[1] for p in polygon]
        left = int(min(xs) - padding)
        top = int(min(ys) - padding)
        width = int(max(xs) - min(xs) + 2 * padding)
        height = int(max(ys) - min(ys) + 2 * padding)
        return cls(pygame.Rect(left, top, width, height), action, key)

    def can_interact(self, actor_rect):
        return actor_rect.colliderect(self.area_rect)

    def try_interact(self, keys, actor_rect):
        pressed = bool(keys[self.key])
        triggered = False

        if pressed and not self._was_pressed and self.can_interact(actor_rect):
            triggered = True

        self._was_pressed = pressed
        return triggered, self.action if triggered else None