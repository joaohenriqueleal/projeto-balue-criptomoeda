class Messages:

    @staticmethod
    def error_message(msg: str = None) -> None:
        if msg:
            print(f'\033[;31m{msg}\033[m')
        else:
            print(f'\033[;31mInput a valida value!\033[m')

    @staticmethod
    def success_message(msg: str = None) -> None:
        if msg:
            print(f'\033[;32m{msg}\033[m')
        else:
            print(f'\033[;32mSuccess!\033[m')

    @staticmethod
    def alert_message(msg: str) -> None:
        print(f'\033[;33m{msg}\033[m')
