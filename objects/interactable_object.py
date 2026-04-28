from objects.interaction_component import InteractableComponent


class InteractableObject:
    def __init__(self, name, polygon, fill_color, border_color, action, texture_key=None, show_border=True):
        self.name = name
        self.polygon = polygon
        self.fill_color = fill_color
        self.border_color = border_color
        self.texture_key = texture_key
        self.show_border = show_border
        self.component = InteractableComponent.from_polygon(polygon, action)

    def get_center(self):
        x = sum(p[0] for p in self.polygon) / len(self.polygon)
        y = sum(p[1] for p in self.polygon) / len(self.polygon)
        return int(x), int(y)

    def as_draw_item(self):
        return {
            "polygon": self.polygon,
            "fill_color": self.fill_color,
            "border_color": self.border_color,
            "texture_key": self.texture_key,
            "show_border": self.show_border,
        }