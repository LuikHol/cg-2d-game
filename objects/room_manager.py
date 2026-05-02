class RoomManager:
    def __init__(self, rooms, initial_room, cooldown=0.20):
        self.rooms = rooms
        self.current_room = initial_room
        self._cooldown = float(cooldown)
        self._timer = 0.0

    def get_room(self):
        return self.rooms[self.current_room]

    def update(self, player, dt):
        if self._timer > 0.0:
            self._timer -= dt
            return None

        room = self.get_room()
        player_rect = player.collider.get_rect_from_center(player.x, player.y)
        for transicao in room["transicoes"]:
            if player_rect.colliderect(transicao["trigger"]):
                sala_origem = self.current_room
                self.current_room = transicao["target"]
                spawn_x, spawn_y = transicao["spawn"]
                player.x = float(spawn_x)
                player.y = float(spawn_y)
                self._timer = self._cooldown
                return {
                    "source": sala_origem,
                    "target": self.current_room,
                    "spawn": (float(spawn_x), float(spawn_y)),
                }

        return None