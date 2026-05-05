from pathlib import Path

import pygame

from configs.audio_config import EXTENSOES_SUPORTADAS, PASTA_SFX_PADRAO, VOLUME_SFX_PADRAO

_sons_em_cache: dict[Path, pygame.mixer.Sound] = {}


def _find_sound_by_name(file_name: str, sound_dir: str = PASTA_SFX_PADRAO) -> Path:
    base_dir = Path(__file__).resolve().parent
    folder = base_dir / sound_dir
    candidate = folder / file_name

    if not candidate.exists() or not candidate.is_file():
        raise FileNotFoundError(f"Arquivo de efeito sonoro nao encontrado: {candidate}")

    if candidate.suffix.lower() not in EXTENSOES_SUPORTADAS:
        raise ValueError(
            f"Formato nao suportado para {candidate.name}. "
            "Use mp3, ogg ou wav."
        )

    return candidate


def tocar_efeito(
    file_name: str,
    sound_dir: str = PASTA_SFX_PADRAO,
    volume: float = VOLUME_SFX_PADRAO,
) -> pygame.mixer.Sound:
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    sound_path = _find_sound_by_name(file_name, sound_dir)
    sound = _sons_em_cache.get(sound_path)
    if sound is None:
        sound = pygame.mixer.Sound(str(sound_path))
        _sons_em_cache[sound_path] = sound

    sound.set_volume(max(0.0, min(1.0, volume)))
    sound.play()
    return sound


def tocar_efeito_se_existir(
    file_name: str,
    sound_dir: str = PASTA_SFX_PADRAO,
    volume: float = VOLUME_SFX_PADRAO,
) -> bool:
    try:
        tocar_efeito(file_name=file_name, sound_dir=sound_dir, volume=volume)
        return True
    except FileNotFoundError:
        return False
