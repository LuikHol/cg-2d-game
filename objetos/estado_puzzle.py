# Estado global do puzzle do tapete.

# Slots: 0=esquerda(coroa), 1=topo(livro), 2=direita(pote).
_ORDEM = ["coroa_vermelha", "livro_laranja", "pote_mel"]
_slots = [None, None, None]


def colocar_item(slot_index, item_name):
    # Coloca qualquer item no slot escolhido, sem validar correspondencia.
    # Retorna True se aceito (slot vazio), False caso contrario.
    # A verificacao de acerto fica por conta de tapete_resolvido().
    if slot_index < 0 or slot_index >= len(_slots):
        return False
    if _slots[slot_index] is not None:
        return False
    _slots[slot_index] = item_name
    return True


def slot_preenchido(slot_index):
    return _slots[slot_index] is not None


def tapete_resolvido():
    # So True quando os tres itens estao nos slots corretos (ordem exata).
    return _slots == _ORDEM


def retirar_item(slot_index):
    # Remove e retorna o item do slot (None se vazio).
    if slot_index < 0 or slot_index >= len(_slots):
        return None
    item = _slots[slot_index]
    _slots[slot_index] = None
    return item


def obter_slots():
    return list(_slots)


def obter_ordem():
    return list(_ORDEM)
