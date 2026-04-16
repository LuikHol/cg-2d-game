def flood_fill(surface, x, y, new_color, border_color):
    stack = [(x, y)]

    while stack:
        x, y = stack.pop()

        if not (0 <= x < surface.get_width() and 0 <= y < surface.get_height()):
            continue

        current = surface.get_at((x, y))[:3]

        if current == border_color or current == new_color:
            continue

        surface.set_at((x, y), new_color)

        stack.append((x+1, y))
        stack.append((x-1, y))
        stack.append((x, y+1))
        stack.append((x, y-1))