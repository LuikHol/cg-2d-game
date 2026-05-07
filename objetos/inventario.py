class Inventario:
    def __init__(self):
        self._itens = []

    def adicionar(self, nome_item):
        if nome_item not in self._itens:
            self._itens.append(nome_item)

    def tem(self, nome_item):
        return nome_item in self._itens

    def remover(self, nome_item):
        if nome_item in self._itens:
            self._itens.remove(nome_item)

    def listar(self):
        return list(self._itens)
