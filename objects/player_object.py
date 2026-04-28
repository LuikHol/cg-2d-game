import pygame
from pathlib import Path
from render.poligono import desenhar_poligono
from render.scanline import scanline_fill
from render.textura import scanline_texture
from render.viewport import transformar_pontos
from render.clipping import clip_polygon_sutherland_hodgman
from objects.components import RigidbodyComponent, ColliderComponent, resolve_axis_aligned_motion


class PlayerObject:
    def __init__(self, x, y, tamanho=20):
        self.x = float(x)
        self.y = float(y)
        self.tamanho = tamanho
        self.velocidade = 250  # unidades de mundo por segundo
        self.rigidbody = RigidbodyComponent()
        self.collider = ColliderComponent(tamanho * 1.4, tamanho * 1.4)
        self.direction = "right"   # right | left | up | down
        self.moving = False
        self.anim_fps = 16.0
        self.anim_timer = 0.0
        self.anim_index = 0

        target_h = max(16, int(self.tamanho * 2.5))

        # Novo formato: 3 arquivos separados por direcao (4 frames cada).
        strip_down = Path("texturas/menino1.png")
        strip_side = Path("texturas/menino2.png")
        strip_up = Path("texturas/menino3.png")
        if strip_down.exists() and strip_side.exists() and strip_up.exists():
            down_frames = self._carregar_frames_da_faixa(strip_down, target_h)
            right_frames = self._carregar_frames_da_faixa(strip_side, target_h)
            up_frames = self._carregar_frames_da_faixa(strip_up, target_h)
            left_frames = [self._espelhar_superficie_x(f) for f in right_frames]

            down_frames, up_frames, right_frames, left_frames = self._normalizar_animacoes(
                down_frames,
                up_frames,
                right_frames,
                left_frames,
            )

            self.animations = {
                "down": down_frames,
                "up": up_frames,
                "right": right_frames,
                "left": left_frames,
            }
            self.frame_count = 4
            return

        self.sprite_sheet = pygame.image.load("texturas/menino.png").convert_alpha()
        sheet_w = self.sprite_sheet.get_width()
        sheet_h = self.sprite_sheet.get_height()

        # Spritesheet do menino: grade 4x3 (frente/lado/costas).
        # A linha do meio contem lados esquerdo e direito separados por colunas.
        usa_grade_4x3 = True

        if usa_grade_4x3:
            frame_w = sheet_w // 4
            frame_h = sheet_h // 3
            up_head_extra = max(2, frame_h // 12)

            rows = []
            for row in range(3):
                row_frames = []
                for col in range(4):
                    extra_top = up_head_extra if row == 2 else 0
                    y = max(0, row * frame_h - extra_top)
                    h = min(sheet_h - y, frame_h + extra_top)
                    r = pygame.Rect(col * frame_w, y, frame_w, h)
                    row_frames.append(self.sprite_sheet.subsurface(r).copy())
                rows.append(row_frames)

            # Escala baseada no conteudo real do sprite (ignorando transparencias extras).
            target_h = max(16, int(self.tamanho * 3.5))

            scale = target_h / max(1, frame_h)

            def preparar_frames(frames):
                preparados = []
                for frame in frames:
                    preparados.append(
                        pygame.transform.smoothscale(
                            frame,
                            (
                                max(1, int(frame_w * scale)),
                                max(1, int(frame_h * scale)),
                            ),
                        )
                    )
                return preparados

            down_frames = preparar_frames(rows[0])
            # Todos os 4 frames laterais estao virados para a direita;
            # left e gerado espelhando.
            right_frames = preparar_frames(rows[1])
            left_frames = [self._espelhar_superficie_x(f) for f in right_frames]
            up_frames = preparar_frames(rows[2])

            # Normaliza todos os frames para o mesmo tamanho e ancora no "pe"
            # para evitar tremores ao trocar entre frente/costas/lados.
            down_frames, up_frames, right_frames, left_frames = self._normalizar_animacoes(
                down_frames,
                up_frames,
                right_frames,
                left_frames,
            )

            self.animations = {
                "down": down_frames,
                "up": up_frames,
                "right": right_frames,
                "left": left_frames,
            }
            self.frame_count = 4
        else:
            # Fallback para o spritesheet antigo em uma linha.
            self.frame_count = 5
            frame_w = sheet_w // self.frame_count
            frame_h = sheet_h
            base_frames = []
            for i in range(self.frame_count):
                r = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
                base_frames.append(self.sprite_sheet.subsurface(r).copy())

            target_h = max(16, int(self.tamanho * 3.5))
            base_frames_preparados = []
            for frame in base_frames:
                corte = self._recortar_alpha(frame)
                scale = target_h / max(1, corte.get_height())
                base_frames_preparados.append(
                    pygame.transform.smoothscale(
                        corte,
                        (
                            max(1, int(corte.get_width() * scale)),
                            max(1, int(corte.get_height() * scale)),
                        ),
                    )
                )
            base_frames = base_frames_preparados
            base_frames_left = [self._espelhar_superficie_x(frame) for frame in base_frames]
            self.animations = {
                "down": base_frames,
                "up": base_frames,
                "right": base_frames,
                "left": base_frames_left,
            }

    def _recortar_alpha(self, surface):
        bounds = surface.get_bounding_rect(min_alpha=1)
        if bounds.width <= 0 or bounds.height <= 0:
            return surface
        return surface.subsurface(bounds).copy()

    def _carregar_frames_da_faixa(self, image_path, target_h):
        strip = pygame.image.load(str(image_path)).convert_alpha()
        frame_count = 4
        frame_w = strip.get_width() // frame_count
        frame_h = strip.get_height()
        frames_raw = []
        for i in range(frame_count):
            r = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
            frames_raw.append(strip.subsurface(r).copy())

        # Usa o fundo da faixa como referencia e recorta por frame,
        # depois ancora todos no pe para evitar "samba".
        bg_color = frames_raw[0].get_at((0, 0))[:3]
        crops = []
        max_crop_w = 1
        max_crop_h = 1
        for frame in frames_raw:
            b = self._bounds_not_bg(frame, bg_color, tolerance=18)
            if b is None:
                b = pygame.Rect(0, 0, frame_w, frame_h)
            crop = frame.subsurface(b).copy()
            crops.append(crop)
            if crop.get_width() > max_crop_w:
                max_crop_w = crop.get_width()
            if crop.get_height() > max_crop_h:
                max_crop_h = crop.get_height()

        scale = target_h / max(1, max_crop_h)
        frames = []
        target_canvas_w = max(1, int(max_crop_w * scale))
        target_canvas_h = max(1, int(max_crop_h * scale))

        for cropped in crops:
            scaled = pygame.transform.smoothscale(
                cropped,
                (
                    max(1, int(cropped.get_width() * scale)),
                    max(1, int(cropped.get_height() * scale)),
                ),
            )
            canvas = pygame.Surface((target_canvas_w, target_canvas_h), pygame.SRCALPHA)
            # Centraliza em x e ancora no pe para estabilizar a caminhada.
            x = (target_canvas_w - scaled.get_width()) // 2
            y = target_canvas_h - scaled.get_height()
            canvas.blit(scaled, (x, y))
            frames.append(
                canvas
            )
        return frames

    def _bounds_not_bg(self, surface, bg_color, tolerance=18):
        w, h = surface.get_size()
        min_x, min_y = w, h
        max_x, max_y = -1, -1

        for y in range(h):
            for x in range(w):
                r, g, b, _ = surface.get_at((x, y))
                if (
                    abs(r - bg_color[0]) > tolerance
                    or abs(g - bg_color[1]) > tolerance
                    or abs(b - bg_color[2]) > tolerance
                ):
                    if x < min_x:
                        min_x = x
                    if y < min_y:
                        min_y = y
                    if x > max_x:
                        max_x = x
                    if y > max_y:
                        max_y = y

        if max_x < min_x or max_y < min_y:
            return None
        return pygame.Rect(min_x, min_y, (max_x - min_x) + 1, (max_y - min_y) + 1)

    def _normalizar_animacoes(self, down_frames, up_frames, right_frames, left_frames):
        grupos = [down_frames, up_frames, right_frames, left_frames]
        todos = [frame for grupo in grupos for frame in grupo]
        max_w = max(frame.get_width() for frame in todos)
        max_h = max(frame.get_height() for frame in todos)

        def padronizar(grupo):
            saida = []
            for frame in grupo:
                w, h = frame.get_size()
                canvas = pygame.Surface((max_w, max_h), pygame.SRCALPHA)
                # Centraliza em x e ancora no pe (base do sprite).
                canvas.blit(frame, ((max_w - w) // 2, max_h - h))
                saida.append(canvas)
            return saida

        return padronizar(down_frames), padronizar(up_frames), padronizar(right_frames), padronizar(left_frames)

    def _espelhar_superficie_x(self, surface):
        return pygame.transform.flip(surface, True, False)

    def mover(self, dx, dy, dt, static_colliders):
        self.rigidbody.velocity.x = dx * self.velocidade
        self.rigidbody.velocity.y = dy * self.velocidade
        self.moving = (dx != 0 or dy != 0)


        atual = self.collider.get_rect_from_center(self.x, self.y)
        move_x = self.rigidbody.velocity.x * dt
        move_y = self.rigidbody.velocity.y * dt
        resolvido = resolve_axis_aligned_motion(atual, move_x, move_y, static_colliders)

        self.x = float(resolvido.centerx)
        self.y = float(resolvido.centery)

        if self.moving:
            if abs(dx) >= abs(dy):
                self.direction = "right" if dx > 0 else "left"
            else:
                self.direction = "down" if dy > 0 else "up"

        # animação
        if self.moving:
            self.anim_timer += dt
            frame_time = 1.0 / self.anim_fps
            while self.anim_timer >= frame_time:
                self.anim_timer -= frame_time
                self.anim_index = (self.anim_index + 1) % self.frame_count
        else:
            self.anim_index = 0

    def get_pontos(self):
        # Representa o player como um losango centrado em (x, y)
        t = self.tamanho
        return [
            (self.x,     self.y - t),   # topo
            (self.x + t, self.y),        # direita
            (self.x,     self.y + t),    # base
            (self.x - t, self.y),        # esquerda
        ]

    def draw(self, screen, camera, viewport, textura=None):
        # Culling simples no mundo antes de converter para a tela.
        if not (camera[0] <= self.x <= camera[2] and camera[1] <= self.y <= camera[3]):
            return

        # Se os frames existem, desenha sprite animado.
        if hasattr(self, "animations") and self.animations:
            sx, sy = transformar_pontos([(self.x, self.y)], camera, viewport)[0]
            frames_dir = self.animations.get(self.direction, self.animations.get("down", []))
            if not frames_dir:
                frames_dir = next(iter(self.animations.values()))
            frame = frames_dir[self.anim_index % len(frames_dir)]

            # Ancora visual no pe do personagem.
            rect = frame.get_rect(midbottom=(sx, sy + self.tamanho))
            screen.blit(frame, rect)
            return

        # Fallback para o desenho poligonal anterior.
        pontos = self.get_pontos()
        clip = clip_polygon_sutherland_hodgman(pontos, *camera)
        if len(clip) >= 3:
            tela = transformar_pontos(clip, camera, viewport)
            if textura:
                scanline_texture(screen, tela, textura)
            else:
                scanline_fill(screen, tela, (220, 200, 0))
            desenhar_poligono(screen, tela, (255, 255, 80))
        
