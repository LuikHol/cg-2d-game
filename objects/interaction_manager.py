import pygame
from render.viewport import world_to_viewport
from render.textura import scanline_texture


class InteractionManager:
    def __init__(self, paper_texture=None):
        self.font_prompt = pygame.font.SysFont(None, 28)
        self.font_world = pygame.font.SysFont(None, 34)
        self.font_paper_title = pygame.font.SysFont(None, 38)
        self.font_paper_body = pygame.font.SysFont(None, 30)
        self.paper_texture = paper_texture

        self.prompt_target = None
        self.world_message = ""
        self.world_message_pos = (0, 0)
        self.world_message_timer = 0.0

        self.paper_open = None
        self._paper_was_pressed = False
        self._paper_can_close = False

    def update(self, keys, actor_rect, interactables, dt):
        paper_pressed = bool(keys[pygame.K_e])

        # Quando o papel estiver aberto, pausa novas interacoes e gerencia apenas fechamento.
        if self.paper_open:
            if not paper_pressed:
                self._paper_can_close = True
            elif paper_pressed and not self._paper_was_pressed and self._paper_can_close:
                self.paper_open = None
                self._paper_can_close = False

            self._paper_was_pressed = paper_pressed
            self.prompt_target = None
            return

        self.prompt_target = None

        for obj in interactables:
            comp = obj.component
            if comp.can_interact(actor_rect):
                self.prompt_target = obj

            triggered, action = comp.try_interact(keys, actor_rect)
            if triggered and action:
                self._apply_action(action, obj)

        if self.world_message_timer > 0.0:
            self.world_message_timer -= dt
        else:
            self.world_message = ""

        self._paper_was_pressed = paper_pressed

    def _apply_action(self, action, obj):
        action_type = action.get("type", "message")

        if action_type == "paper":
            self.paper_open = {
                "title": action.get("title", "Anotacao"),
                "lines": action.get("lines", []),
            }
            self._paper_can_close = False
            return

        # Default: mensagem no mapa, acima do objeto.
        self.world_message = action.get("text", "...")
        self.world_message_pos = obj.get_center()
        self.world_message_timer = float(action.get("duration", 2.6))

    def draw(self, screen, camera, viewport):
        if self.prompt_target:
            px, py = self.prompt_target.get_center()
            sx, sy = world_to_viewport(px, py - 34, camera, viewport)
            prompt_surface = self.font_prompt.render("E: interagir", True, (245, 230, 150))
            bg = prompt_surface.get_rect(center=(sx, sy))
            bg.inflate_ip(14, 8)
            pygame.draw.rect(screen, (20, 20, 20), bg)
            screen.blit(prompt_surface, prompt_surface.get_rect(center=(sx, sy)))

        if self.world_message:
            wx, wy = self.world_message_pos
            sx, sy = world_to_viewport(wx, wy - 56, camera, viewport)
            msg_surface = self.font_world.render(self.world_message, True, (250, 250, 250))
            bg = msg_surface.get_rect(center=(sx, sy))
            bg.inflate_ip(18, 10)
            pygame.draw.rect(screen, (10, 10, 10), bg)
            screen.blit(msg_surface, msg_surface.get_rect(center=(sx, sy)))

        if self.paper_open:
            self._draw_paper_overlay(screen)

    def _draw_paper_overlay(self, screen):
        w, h = screen.get_size()

        # Folha em formato de poligono para reforçar o efeito de "papel".
        paper = [
            (w // 2 - 240, h // 2 - 170),
            (w // 2 + 240, h // 2 - 150),
            (w // 2 + 220, h // 2 + 170),
            (w // 2 - 220, h // 2 + 190),
        ]

        if self.paper_texture is not None:
            scanline_texture(screen, paper, self.paper_texture)
        else:
            pygame.draw.polygon(screen, (233, 222, 188), paper)

        # Borda discreta para evitar contorno forte/estranho.
        pygame.draw.polygon(screen, (95, 82, 54), paper, 1)

        title = self.paper_open.get("title", "Documento")
        lines = self.paper_open.get("lines", [])

        title_surface = self.font_paper_title.render(title, True, (62, 44, 24))
        screen.blit(title_surface, (w // 2 - title_surface.get_width() // 2, h // 2 - 130))

        y = h // 2 - 72
        for line in lines:
            line_surface = self.font_paper_body.render(line, True, (62, 44, 24))
            screen.blit(line_surface, (w // 2 - line_surface.get_width() // 2, y))
            y += 34

        hint = self.font_prompt.render("E: fechar", True, (90, 75, 48))
        screen.blit(hint, (w // 2 - hint.get_width() // 2, h // 2 + 140))