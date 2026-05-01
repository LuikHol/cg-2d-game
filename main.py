from menu.main_menu import menu_principal
from test_game import TestGameApp


def executar_jogo():
    app = TestGameApp()
    app.run()


def main():
    acao = menu_principal()
    if acao == "jogar":
        executar_jogo()


if __name__ == "__main__":
    main()
