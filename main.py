from menu.main_menu import menu_principal
from render.splash_screen import exibir_splash_screen
from test_game import TestGameApp
from configs.menu_config import LARGURA, ALTURA


def executar_jogo():
    app = TestGameApp()
    app.run()


def main():
    if not exibir_splash_screen(LARGURA, ALTURA, duracao=3.2):
        return

    acao = menu_principal()
    if acao == "jogar":
        executar_jogo()


if __name__ == "__main__":
    main()
