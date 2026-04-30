import runpy
from pathlib import Path

from menu.main_menu import menu_principal


def executar_jogo():
    caminho_jogo = Path(__file__).with_name("test_game.py")
    try:
        runpy.run_path(str(caminho_jogo), run_name="__main__")
    except SystemExit:
        # test_game.py chama sys.exit() ao finalizar; voltamos ao menu.
        pass


def main():
    acao = menu_principal()
    if acao == "jogar":
        executar_jogo()


if __name__ == "__main__":
    main()
