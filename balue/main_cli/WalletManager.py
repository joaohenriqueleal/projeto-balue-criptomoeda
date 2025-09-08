from main_cli.Messages import *
from connection.Node import *


class WalletManager:

    def __init__(self, wallet_name: str = None) -> None:
        self.messages: 'Messages' = Messages()
        if wallet_name:
            self.wallet: 'Wallet' = Wallet(True, wallet_name)
        else:
            self.wallet: 'Wallet' = Wallet(True)
        self.miner: 'Miner' = Miner(self.wallet.private_key,
                                    self.wallet.public_key,
                                    self.wallet.address)

    def switch_wallet(self, self_wallet: bool = True) -> None:
        print('Your Wallets'.center(80))
        print('~' * 80)
        if not self_wallet:
            wallets_pointer: 'WalletsPointer' = WalletsPointer()
            wallets: list[str] = wallets_pointer.list_wallet_names()
        else:
            wallets: list[str] = self.wallet.wallet_storage.wallets_pointer.list_wallet_names()
        for i, w in enumerate(wallets):
            print(f'{i + 1}. {w}')
        try:
            to_switch: int = int(input('Input a number of wallet (0 for cancel):  '))
        except ValueError:
            self.messages.error_message()
        else:
            if to_switch > len(wallets):
                self.messages.error_message('Wallet don`t exists.')
                return
            if to_switch == 0:
                self.messages.error_message('Operation canceled!')
                return
            else:
                self.wallet = Wallet(True, wallets[to_switch - 1])
                self.miner = Miner(self.wallet.private_key, self.wallet.public_key,
                                   self.wallet.address)
                self.messages.success_message('Switched!')

    def create_new_wallet(self) -> None:
        print('Create new wallet.'.center(80))
        print('=' * 80)
        try:
            wallet_name: str = str(input('Name of new wallet:  ')).strip()
        except ValueError:
            self.messages.error_message()
            return
        else:
            self.wallet = Wallet(True, wallet_name)
            self.miner = Miner(self.wallet.private_key, self.wallet.public_key,
                               self.wallet.address)
            self.messages.success_message('Wallet created!')

    def delete_wallet(self) -> None:
        print('Delete Wallet'.center(80))
        print('=' * 80)
        wallets: list[str] = self.wallet.wallet_storage.wallets_pointer.list_wallet_names()
        if not wallets:
            self.messages.error_message('No wallets available to delete.')
            return
        for i, w in enumerate(wallets):
            print(f'{i + 1}. {w}')
        try:
            to_delete: int = int(input('Select a wallet to delete (0 to cancel): '))
        except ValueError:
            self.messages.error_message()
            return
        if to_delete == 0:
            self.messages.alert_message('Operation cancelled.')
            return
        if not (1 <= to_delete <= len(wallets)):
            self.messages.error_message('Invalid wallet number.')
            return
        wallet_name: str = wallets[to_delete - 1]
        if wallet_name == self.wallet.wallet_storage.name:
            self.messages.alert_message('You are about to delete the current active wallet.')
        self.messages.alert_message('Warning: Deleting a wallet is irreversible and all funds will be lost.')
        confirm: str = input(f'Type "DELETE {wallet_name}" to confirm: ').strip()
        if confirm != f'DELETE {wallet_name}':
            self.messages.alert_message('Deletion cancelled.')
            return
        success: bool = self.wallet.wallet_storage.wallets_pointer.delete_wallet(wallet_name)
        if success:
            if wallet_name == self.wallet.wallet_storage.name and len(self.wallet.wallet_storage.wallets_pointer.wallets) > 0:
                self.wallet = None
                self.miner = None
                self.messages.alert_message('Active wallet was deleted. Please switch to another wallet.')
                self.switch_wallet(False)
            self.messages.success_message(f'Wallet "{wallet_name}" deleted successfully.')
        else:
            self.messages.error_message('Wallet not found or could not be deleted.')
