from datetime import datetime
from connection.Node import *


class MainMenu:

    def __init__(self, wallet_name: str = None) -> None:
        if wallet_name:
            self.wallet: 'Wallet' = Wallet(True, wallet_name)
        else:
            self.wallet: 'Wallet' = Wallet(True)
        self.miner: 'Miner' = Miner(self.wallet.private_key,
                                    self.wallet.public_key,
                                    self.wallet.address)
        self.node: 'Node' = Node()

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

    def print_balance(self) -> None:
        self.success_message(
            f'{self.get_balance(self.wallet.address):.8f} BAL$')

    def view_last_ten_blocks(self) -> None:
        print('Last 10 blocks + pending in yellow.'.center(80))
        print('=' * 80)
        for blk in blockchain.pending_blocks:
            self.alert_message(f'Index:  {blk.index}, Hash:  {blk.hash[20:]}...')
            self.alert_message(f'     with {blk.total_transactions} transactions.')
            self.alert_message('~' * 80)
        indexes = list(range(len(blockchain.adjusts_path.storage.chain)))
        last_indexes = indexes[-10:]
        for i in last_indexes[::-1]:
            block: dict = blockchain.adjusts_path.storage.load_block(i)
            print(f'Index:  {block["index"]}, Hash:  {block["hash"][20:]}...')
            print(f'     with {block["total_transactions"]} transactions.')
            print('~' * 80)

    @staticmethod
    def format_timestamp_ns(timestamp_ns: int) -> str:
        timestamp_s = timestamp_ns / 1_000_000_000
        dt = datetime.fromtimestamp(timestamp_s)
        return dt.strftime("%d/%m/%Y/%H:%M:%S")

    def view_transactions_descriptions(self) -> None:
        exists: bool = False
        indexes = list(range(len(blockchain.adjusts_path.storage.chain)))
        last_indexes = indexes[-10:]
        for i in last_indexes[::-1]:
            block: dict = blockchain.adjusts_path.storage.load_block(i)
            for tr in block["transactions"]:
                if tr["receiver"] == self.wallet.address and tr["metadata"] != "0":
                    if not exists:
                        print('Transactions received descriptions'.center(80))
                        print('=' * 80)
                    exists = True
                    print(f'In:  {self.format_timestamp_ns(tr["timestamp"])}')
                    print(f'From:  {tr["sender"]}')
                    print(f'Description:  {tr["metadata"]}')
                    print('~' * 80)
        if not exists:
            self.alert_message('You don`t have descriptions.')

    @staticmethod
    def get_balance(address: str) -> float:
        balance: int = 0
        for i in range(0, len(blockchain.adjusts_path.storage.chain)):
            block: dict = blockchain.adjusts_path.storage.load_block(i)
            if block["miner_address"] == address:
                balance += (block["reward"] + block["total_fees"])
            for tr in block["transactions"]:
                if tr["sender"] == address:
                    balance -= (tr["value"] + tr["fee"])
                if tr["receiver"] == address:
                    balance += tr["value"]
        for blk in blockchain.pending_blocks:
            for tr in blk.transactions:
                if tr["sender"] == address:
                    balance -= (tr["value"] + tr["fee"])
        return balance / DIVISIBLE

    def switch_wallet(self) -> None:
        print('Your Wallets'.center(80))
        print('~' * 80)
        wallets: list[str] = self.wallet.wallet_storage.wallets_pointer.list_wallet_names()
        for i, w in enumerate(wallets):
            print(f'{i + 1}. {w}')
        try:
            to_switch: int = int(input('Input a number of wallet (0 for cancel):  '))
        except ValueError:
            self.error_message()
        else:
            if to_switch > len(wallets):
                self.error_message('Wallet don`t exists.')
                return
            if to_switch == 0:
                self.error_message('Operation canceled!')
                return
            else:
                self.wallet = Wallet(True, wallets[to_switch - 1])
                self.miner = Miner(self.wallet.private_key, self.wallet.public_key,
                                   self.wallet.address)
                self.success_message('Switched!')

    def create_new_wallet(self) -> None:
        print('Create new wallet.'.center(80))
        print('=' * 80)
        try:
            wallet_name: str = str(input('Name of new wallet:  ')).strip()
        except ValueError:
            self.error_message()
            return
        else:
            self.wallet = Wallet(True, wallet_name)
            self.miner = Miner(self.wallet.private_key, self.wallet.public_key,
                               self.wallet.address)
            self.success_message('Wallet created!')

    def delete_wallet(self) -> None:
        print('Delete Wallet'.center(80))
        print('=' * 80)
        wallets: list[str] = self.wallet.wallet_storage.wallets_pointer.list_wallet_names()
        if not wallets:
            self.error_message('No wallets available to delete.')
            return
        for i, w in enumerate(wallets):
            print(f'{i + 1}. {w}')
        try:
            to_delete: int = int(input('Select a wallet to delete (0 to cancel): '))
        except ValueError:
            self.error_message()
            return
        if to_delete == 0:
            self.alert_message('Operation cancelled.')
            return
        if not (1 <= to_delete <= len(wallets)):
            self.error_message('Invalid wallet number.')
            return
        wallet_name: str = wallets[to_delete - 1]
        if wallet_name == self.wallet.wallet_storage.name:
            self.alert_message('You are about to delete the current active wallet.')
        self.alert_message('Warning: Deleting a wallet is irreversible and all funds will be lost.')
        confirm: str = input(f'Type "DELETE {wallet_name}" to confirm: ').strip()
        if confirm != f'DELETE {wallet_name}':
            self.alert_message('Deletion cancelled.')
            return
        success: bool = self.wallet.wallet_storage.wallets_pointer.delete_wallet(wallet_name)
        if success:
            if wallet_name == self.wallet.wallet_storage.name:
                self.wallet = None
                self.miner = None
                self.alert_message('Active wallet was deleted. Please switch to another wallet.')
            self.success_message(f'Wallet "{wallet_name}" deleted successfully.')
        else:
            self.error_message('Wallet not found or could not be deleted.')

    def main(self) -> None:
        self.node.handle.broadcasts.sni.rpb.rni.bc.bp.rc.request_chain()
        if not self.wallet or not self.miner:
                self.create_new_wallet()
        print('BALUE Node CLI'.center(80))
        print('=' * 80)
        self.node.node_infos()
        print('~' * 80)
        self.print_balance()
        print(f'Your balue address:  {self.wallet.address}')
        while True:
            self.node.handle.broadcasts.sni.rpb.rni.bc.bp.rc.request_chain()
            self.node.handle.broadcasts.sni.rpb.rni.bc.bp.broadcast_peers()
            self.node.handle.broadcasts.sni.rpb.request_pending_block()
            if not self.wallet or not self.miner:
                self.create_new_wallet()
            print('~' * 80)
            print(self.wallet.wallet_storage.name.center(80))
            print('=' * 80)
            print('[ 1 ] Consult balance.')
            print('[ 2 ] Consult balue address.')
            print('[ 3 ] Transfer balue.')
            print('[ 4 ] Mine pending.')
            print('[ 5 ] View last ten blocks.')
            print('[ 6 ] View transactions descriptions.')
            print('[ 7 ] Add peer.')
            print('[ 8 ] View your node infos.')
            print('[ 9 ] Switch wallet.')
            print('[ 10 ] Create new wallet.')
            print('[ 11 ] Delete wallet.')
            print('[ 12 ] Add new pending block.')
            print('[ 13 ] Exit.')
            try:
                print('~' * 80)
                option: int = int(input('>>>  '))
                print('~' * 80)
            except ValueError:
                self.error_message()
                continue
            if option == 1:
                self.print_balance()
            elif option == 2:
                print(f'Your balue address:  {self.wallet.address}')
            elif option == 3:
                try:
                    if len(blockchain.pending_blocks) == 0:
                        blockchain.new_pending_block()
                    destination: str = str(input('Destination Balue address:  ')).strip()
                    value: float = float(input('Value:  BAL$ '))
                    fee: float = float(input('Fee:  BAL$ '))
                    if ((value + fee) > blockchain.validations.pending_validations.block_validations.
                            transaction_validations.get_balance(self.wallet.address)):
                        self.error_message('Insuficient balance!')
                        continue
                    if value < 0 or fee < 0:
                        self.error_message('value and rate cannot be less than zero!')
                        continue
                    metadata: str = str(input('Metadata (optional):  ')).strip()
                    if len(metadata) > MAX_METADATA_LENGTH:
                        self.error_message('huge metadada!')
                        continue
                except ValueError:
                    self.error_message()
                    continue
                transaction: 'Transaction' = Transaction(
                    self.wallet.address,
                    destination,
                    int(value * DIVISIBLE),
                    int(fee * DIVISIBLE),
                    blockchain.adjusts_path.adjust_transactions_difficulty(
                        blockchain.get_index()
                    ),
                    metadata or "0"
                )
                transaction.validate(
                    self.wallet.wallet_methods.public_key_to_json(self.wallet.public_key)
                )
                signature = self.wallet.wallet_methods.signature_to_json(
                    self.wallet.wallet_methods.sign_hash(self.wallet.private_key,
                        transaction.hash)
                )
                transaction.sign(signature)
                blockchain.add_transaction_to_pending(transaction)
                self.success_message('Transaction added with success!')
                self.node.handle.broadcasts.sni.rpb.rni.bc.bp.rc.blb.bpb.broadcast_pending_block()
            elif option == 4:
                if len(blockchain.pending_blocks) == 0:
                    self.error_message('there is no pending block!')
                    continue
                try:
                    metadata: str = str(input('add metadata on block ?(optional):  ')).strip()
                except ValueError:
                    self.error_message()
                    continue
                self.error_message(datetime.now().strftime("Mine initialized in %d/%m/%Y/%H:%M:%S"))
                self.miner.mine(metadata or "0")
                self.error_message(datetime.now().strftime("Mine terminated in %d/%m/%Y/%H:%M:%S"))
                self.node.handle.broadcasts.sni.rpb.rni.bc.bp.rc.blb.broadcast_last_block()
                self.success_message(f'Recompensa de {blockchain.adjusts_path.adjust_reward(blockchain.get_index() - 1) / DIVISIBLE:.8f} BAL$ adicionada!')
            elif option == 5:
                self.view_last_ten_blocks()
            elif option == 6:
                self.view_transactions_descriptions()
            elif option == 7:
                try:
                    ip: str = str(input('IP of new peer:  ')).strip()
                    port: int = int(input('PORT of new peer (Input -1 to use defalt port):  '))
                except ValueError:
                    self.error_message()
                    continue
                if port == -1:
                    port = PORT
                self.node.handle.broadcasts.sni.rpb.rni.bc.bp.rc.blb.bpb.peers.add_peer(ip, port)
                self.node.handle.broadcasts.sni.rpb.rni.bc.bp.broadcast_peers()
                self.node.handle.broadcasts.sni.rpb.rni.bc.bp.rc.request_chain()
                self.node.handle.broadcasts.sni.rpb.request_pending_block()
                self.success_message('Peer added with success!')
            elif option == 8:
                self.node.node_infos()
            elif option == 9:
                self.switch_wallet()
            elif option == 10:
                self.create_new_wallet()
            elif option == 11:
                self.delete_wallet()
            elif option == 12:
                if len(blockchain.pending_blocks) > 0:
                    self.error_message('there is still a pending block!')
                    continue
                blockchain.new_pending_block()
                self.node.handle.broadcasts.sni.rpb.rni.bc.bp.rc.blb.bpb.broadcast_pending_block()
                self.success_message('New pending block added with success!')
            elif option == 13:
                print('bye!')
                exit()
            else:
                self.error_message('Input a option between 1/12')
