from main_cli.WalletManager import *
from datetime import datetime


class DataViews:

    def __init__(self, wallet_name: str = None) -> None:
        self.wallet_manager: 'WalletManager' = WalletManager(wallet_name)
        self.messages: 'Messages' = Messages()

    def view_last_ten_blocks(self) -> None:
        print('Last 10 blocks + pending in yellow.'.center(80))
        print('=' * 80)
        for blk in blockchain.pending_blocks:
            self.messages.alert_message(f'Index:  {blk.index}, Hash:  {blk.hash[:20]}...')
            self.messages.alert_message(f'     with {blk.total_transactions} transactions.')
            self.messages.alert_message('~' * 80)
        indexes = list(range(len(blockchain.adjusts_path.storage.chain)))
        last_indexes = indexes[-10:]
        for i in last_indexes[::-1]:
            block: dict = blockchain.adjusts_path.storage.load_block(i)
            print(f'Index:  {block["index"]}, Hash:  {block["hash"][:20]}...')
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
                if tr["receiver"] == self.wallet_manager.wallet.address and tr["metadata"] != "0":
                    if not exists:
                        print('Transactions received descriptions'.center(80))
                        print('=' * 80)
                    exists = True
                    print(f'In:  {self.format_timestamp_ns(tr["timestamp"])}')
                    print(f'From:  {tr["sender"]}')
                    print(f'Description:  {tr["metadata"]}')
                    print('~' * 80)
        if not exists:
            self.messages.alert_message('You don`t have descriptions.')

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

    def print_balance(self) -> None:
        self.messages.success_message(
            f'{self.get_balance(self.wallet_manager.wallet.address):.8f} BAL$')
