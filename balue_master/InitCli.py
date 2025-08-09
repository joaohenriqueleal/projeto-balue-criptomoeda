from main_cli.MainMenu import *


class Init:

    def __init__(self) -> None:
        self.wallets_pointer: 'WalletsPointer' = WalletsPointer()

    def init(self) -> None:
        if len(self.wallets_pointer.wallets) == 0:
            print('Create your first Wallet'.center(80))
            print('=' * 80)
            while True:
                try:
                    wallet_name: str = str(input('New wallet name:  ')).strip()
                    main_menu: 'MainMenu' = MainMenu(wallet_name)
                    Messages.success_message('Wallet created!')
                    main_menu.main()
                    break
                except ValueError:
                    Messages.error_message()
                    print('~' * 80)
                    continue
        else:
            main_menu: 'MainMenu' = MainMenu()
            main_menu.main()


if __name__ == '__main__':
    init: 'Init' = Init()
    init.init()
