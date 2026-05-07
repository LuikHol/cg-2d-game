class RoomManager:
    def __init__(self, rooms, initial_room, cooldown=0.20):
        self.rooms = rooms
        self.current_room = initial_room
        self._cooldown = float(cooldown)
        self._timer = 0.0
        self._locked = set()

    def trancar_sala(self, target):
        self._locked.add(target)

    def destrancar_sala(self, target):
        self._locked.discard(target)

    def obter_sala(self):
        return self.rooms[self.current_room]

    def atualizar(self, player, dt):
        if self._timer > 0.0:
            self._timer -= dt
            return None

        room = self.obter_sala()
        player_rect = player.collider.obter_rect_do_centro(player.x, player.y)
        for transicao in room["transicoes"]:
            if player_rect.colliderect(transicao["gatilho"]):
                alvo = transicao["destino"]
                if alvo in self._locked:
                    self._timer = self._cooldown
                    return {"bloqueado": True, "destino": alvo}
                sala_origem = self.current_room
                self.current_room = alvo
                spawn_x, spawn_y = transicao["posicao_spawn"]
                player.x = float(spawn_x)
                player.y = float(spawn_y)
                self._timer = self._cooldown
                return {
                    "origem": sala_origem,
                    "destino": self.current_room,
                    "posicao_spawn": (float(spawn_x), float(spawn_y)),
                }

        return None