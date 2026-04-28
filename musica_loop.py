from pathlib import Path

import pygame
from configs.audio_config import (
    DESVANECIMENTO_MS_PADRAO,
    EXTENSOES_SUPORTADAS,
    PASTA_MUSICA_PADRAO,
    VOLUME_MUSICA_PADRAO,
)

_current_music: Path | None = None


def _find_music_file(music_dir: str = PASTA_MUSICA_PADRAO) -> Path:
    base_dir = Path(__file__).resolve().parent
    folder = base_dir / music_dir

    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Pasta de musica nao encontrada: {folder}")

    candidates = sorted(
        file_path
        for file_path in folder.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in EXTENSOES_SUPORTADAS
    )

    if not candidates:
        raise FileNotFoundError(
            f"Nenhum arquivo de audio encontrado em {folder}. "
            "Use mp3, ogg ou wav."
        )

    return candidates[0]


def _find_music_by_name(file_name: str, music_dir: str = PASTA_MUSICA_PADRAO) -> Path:
    base_dir = Path(__file__).resolve().parent
    folder = base_dir / music_dir
    candidate = folder / file_name

    if not candidate.exists() or not candidate.is_file():
        raise FileNotFoundError(f"Arquivo de musica nao encontrado: {candidate}")

    if candidate.suffix.lower() not in EXTENSOES_SUPORTADAS:
        raise ValueError(
            f"Formato nao suportado para {candidate.name}. "
            "Use mp3, ogg ou wav."
        )

    return candidate


def _play_path(music_path: Path, volume: float = VOLUME_MUSICA_PADRAO, fade_ms: int = DESVANECIMENTO_MS_PADRAO) -> Path:
    global _current_music

    if not pygame.mixer.get_init():
        pygame.mixer.init()

    volume = max(0.0, min(1.0, volume))

    # Evita recarregar a mesma musica sem necessidade.
    if _current_music == music_path and pygame.mixer.music.get_busy():
        pygame.mixer.music.set_volume(volume)
        return music_path

    pygame.mixer.music.fadeout(max(0, int(fade_ms)))
    pygame.mixer.music.load(str(music_path))
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)
    _current_music = music_path
    return music_path


def iniciar_musica_loop(music_dir: str = PASTA_MUSICA_PADRAO, volume: float = VOLUME_MUSICA_PADRAO) -> Path:
    music_path = _find_music_file(music_dir)
    return _play_path(music_path, volume=volume)


def trocar_musica(
    file_name: str,
    music_dir: str = PASTA_MUSICA_PADRAO,
    volume: float = VOLUME_MUSICA_PADRAO,
    fade_ms: int = DESVANECIMENTO_MS_PADRAO,
) -> Path:
    music_path = _find_music_by_name(file_name, music_dir)
    return _play_path(music_path, volume=volume, fade_ms=fade_ms)


def trocar_musica_se_existir(
    file_name: str,
    fallback_to_first: bool = True,
    music_dir: str = PASTA_MUSICA_PADRAO,
    volume: float = VOLUME_MUSICA_PADRAO,
    fade_ms: int = DESVANECIMENTO_MS_PADRAO,
) -> Path:
    try:
        return trocar_musica(
            file_name=file_name,
            music_dir=music_dir,
            volume=volume,
            fade_ms=fade_ms,
        )
    except FileNotFoundError:
        if not fallback_to_first:
            raise
        return iniciar_musica_loop(music_dir=music_dir, volume=volume)


def parar_musica() -> None:
    global _current_music
    pygame.mixer.music.stop()
    _current_music = None
