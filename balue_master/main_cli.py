from network_protocol.node import *
from datetime import datetime
from decimal import Decimal


class MainCli:

    def __init__(self) -> None:
        self.wallet = Wallet(True)
        self.miner = Miner(self.wallet.private_key, self.wallet.public_key, self.wallet.address)
        self.node = Node()

        self.node.broadcasts.broadcast_peers()
        self.node.broadcasts.request_chain()

    def get_balance(self) -> float:
        address: str = self.wallet.address
        balance: float = 0
        for blk in blockchain.pending_block:
            for tr in blk.transactions:
                if tr["sender"] == address:
                    balance -= (tr["value"] + tr["fee"])
        for i in range(0, len(blockchain.validations.adjusts.storage.chain)):
            blk = blockchain.validations.adjusts.storage.load_block(i)
            if blk["miner_address"] == address:
                balance += (blk["reward"] + blk["total_fees"])
            for tr in blk["transactions"]:
                if tr["sender"] == address:
                    balance -= (tr["value"] + tr["fee"])
                if tr["receiver"] == address:
                    balance += tr["value"]
        return balance

    @staticmethod
    def format_timestamp(timestamp_ns: int) -> str:
        timestamp_sec = timestamp_ns / 1_000_000_000
        dt = datetime.fromtimestamp(timestamp_sec)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def print_transactions_descriptions(self) -> None:
        for i in range(0, len(blockchain.validations.adjusts.storage.chain)):
            blk: dict = blockchain.validations.adjusts.storage.load_block(i)
            for tr in blk["transactions"]:
                if tr["receiver"] == self.wallet.address and tr["metadata"] != "0":
                    print(f'Of: {tr["sender"]}')
                    print(f'In: {self.format_timestamp(tr["validation_timestamp"])}')
                    print(f'On block: #{blk["index"]}')
                    print(f'Description:  {tr["metadata"]}')
                    print('~' * 80)

    @staticmethod
    def print_last_blocks() -> None:
        chain_length = len(blockchain.validations.adjusts.storage.chain)
        start_index = max(0, chain_length - 10)

        for pending_blk in blockchain.pending_block[::-1]:
            print(f'\033[93mBlock #{pending_blk.index}, Hash:  {pending_blk.hash[:20]}...')
            print(f'    with {pending_blk.total_transactions} transactions.\033[0m')

        for i in range(start_index, chain_length)[::-1]:
            blk: dict = blockchain.validations.adjusts.storage.load_block(i)
            print(f'Block #{blk["index"]}, Hash:  {blk["hash"][:20]}...')
            print(f'    with {blk["total_transactions"]} transactions.')
            print('~' * 80)

    def print_acquaintance_peers(self) -> None:
        for peer in self.node.broadcasts.peers.peers:
            print(f'{peer["ip"]}:{peer["port"]}')
            print('~' * 80)

    @staticmethod
    def message_error(msg: str) -> None:
        print(f'\033[;31m{msg}\033[m')

    @staticmethod
    def success_message(msg) -> None:
        print(f'\033[;32m{msg}\033[m')

    def main(self) -> None:
        print('=' * 80)
        self.node.peer_infos()
        print('~' * 80)
        self.success_message(f'Balance:  {Decimal(self.get_balance()):.8f} BAL$')
        print(f'Balue address:  {self.wallet.address}')
        print('=' * 80)
        while True:
            print('[ 1 ] to see your balance.')
            print('[ 2 ] to see your Balue address.')
            print('[ 3 ] to transfer Balue.')
            print('[ 4 ] to mine Balue.')
            print('[ 5 ] to see transactions descriptions.')
            print('[ 6 ] to see last 10 block + the pending in yellow.')
            print('[ 7 ] to add new peer on your list.')
            print('[ 8 ] to see acquaintances peers.')
            print('[ 9 ] to add new pending block.')
            print('[ 10 ] to see infos about your node.')
            print('[ 11 ] to exit.')
            try:
                print('=' * 80)
                opc = int(input('>>>  '))
                print('=' * 80)
            except ValueError:
                self.message_error('input a valid int!')
                continue
            if opc == 1:
                 self.success_message(f'Balance:  {Decimal(self.get_balance()):.8f} BAL$')
            elif opc == 2:
                print(f'Balue address:  {self.wallet.address}')
            if opc == 3:
                try:
                    if len(blockchain.pending_block) > 0:
                        if blockchain.pending_block[0].total_transactions >= MAX_TRANSACTIONS_PER_BLOCK:
                            self.message_error('Pending block is full! Please wait for the next one!')
                            continue
                    value: float = float(input('Valor da transação:  '))
                    fee: float = float(input('How much fee do you want to pay for the transaction?  '))
                    receiver: str = str(input('Receiver address:  ')).strip()
                    metadata: str = str(input('Description (optional):  ')).strip()
                    if value + fee > self.get_balance():
                        self.message_error('Insuficient balance!')
                    blockchain.new_pending_block()
                    t: 'Transaction' = Transaction(self.wallet.address, receiver, value, fee,
                                        blockchain.validations.adjusts.adjust_transactions_difficulty(blockchain.index()),
                                        metadata)
                    t.validate(self.wallet.wallet_methods.public_key_to_json(self.wallet.public_key))
                    sign = self.wallet.wallet_methods.sign_hash(self.wallet.private_key, t.hash)
                    t.sign(self.wallet.wallet_methods.signature_to_json(sign))

                    blockchain.add_transaction_to_pending(t)
                    self.node.broadcasts.broadcast_pending_block()
                    self.success_message('Transaction added with success!')
                except ValueError:
                    self.message_error('Input a valid Value.')
            elif opc == 4:
                if len(blockchain.pending_block) > 0:
                    if blockchain.validations.adjusts.min_transactions(blockchain.index()) > blockchain.pending_block[0].total_transactions:
                        self.message_error('block has not yet reached the minimum number of transactions to mine')
                        continue
                else:
                    blockchain.new_pending_block()
                    self.node.broadcasts.broadcast_pending_block()
                    if blockchain.validations.adjusts.min_transactions(blockchain.index()) > blockchain.pending_block[0].total_transactions:
                        self.message_error('block has not yet reached the minimum number of transactions to mine')
                        continue
                try:
                    metadata: str = str(input('Description in block (opcional):  '))
                    print('=' * 80)
                except ValueError:
                    self.message_error('Input a valid value!')
                    continue
                now = datetime.now()
                print(now.strftime("\033[;31mMine Initialized in %y-%m-%d %H:%M:%S\033[m"))
                self.miner.unique_mine(metadata)
                now = datetime.now()
                self.node.broadcasts.broadcast_last_block()
                print(now.strftime("\033[;31mMine terminated in %y-%m-%d %H:%M:%S\033[m"))
                self.success_message(f'Block #{len(blockchain.validations.adjusts.storage.chain) - 1} Mined!')
                self.success_message(f'New balance:  {self.get_balance():.8f} BAL$')
            elif opc == 5:
                print('DESCRIPTIONS'.center(80))
                print('=' * 80)
                self.print_transactions_descriptions()
            elif opc == 6:
                print('BLOCKS'.center(80))
                print('=' * 80)
                self.print_last_blocks()
                self.node.broadcasts.request_chain()
            elif opc == 7:
                try:
                    ip: str = str(input('IP do peer:  ')).strip()
                    port: int = int(input('PORT:  '))
                    feedback: str = self.node.broadcasts.peers.add_peer(ip, port)
                    self.node.broadcasts.broadcast_peers()
                    self.node.broadcasts.request_chain()
                    print(feedback)
                except ValueError:
                    self.message_error('Input a valid PORT!')
            elif opc == 8:
                print('NODES'.center(80))
                print('=' * 80)
                self.print_acquaintance_peers()
            elif opc == 9:
                blockchain.new_pending_block()
                self.node.broadcasts.broadcast_pending_block()
                self.success_message('Novo bloco pendente adicionado!')
            elif opc == 10:
                self.node.peer_infos()
            elif opc == 11:
                exit()
            print('=' * 80)


if __name__ == '__main__':
    main: 'MainCli' = MainCli()
    main.main()
