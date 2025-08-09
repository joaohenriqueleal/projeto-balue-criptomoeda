from main_cli.DataViews import *


class Actions:

    def __init__(self, wallet_name: str = None) -> None:
        self.data_views: 'DataViews' = DataViews(wallet_name)
        self.messages: 'Messages' = Messages()
        self.node: 'Node' = Node()

    def print_address(self) -> None:
        print(f'Your balue address:  {self.data_views.wallet_manager.wallet.address}')

    def transfer(self) -> None:
        try:
            if len(blockchain.pending_blocks) == 0:
                blockchain.new_pending_block()
            destination: str = str(input('Destination Balue address:  ')).strip()
            value: float = float(input('Value:  BAL$ '))
            fee: float = float(input('Fee:  BAL$ '))
            if ((value + fee) > blockchain.validations.pending_validations.block_validations.
                    transaction_validations.get_balance(self.data_views.wallet_manager.wallet.address)):
                self.messages.error_message('Insuficient balance!')
                return
            if value < 0 or fee < 0:
                self.messages.error_message('value and rate cannot be less than zero!')
                return
            metadata: str = str(input('Metadata (optional):  ')).strip()
            if len(metadata) > MAX_METADATA_LENGTH:
                self.messages.error_message('huge metadada!')
                return
        except ValueError:
            self.messages.error_message()
            return
        transaction: 'Transaction' = Transaction(
            self.data_views.wallet_manager.wallet.address,
            destination,
            int(value * DIVISIBLE),
            int(fee * DIVISIBLE),
            blockchain.adjusts_path.adjust_transactions_difficulty(
                blockchain.get_index()
            ),
            metadata or "0"
        )
        transaction.validate(
            self.data_views.wallet_manager.wallet.wallet_methods.public_key_to_json(
                self.data_views.wallet_manager.wallet.public_key
            )
        )
        signature = self.data_views.wallet_manager.wallet.wallet_methods.signature_to_json(
            self.data_views.wallet_manager.wallet.wallet_methods.sign_hash(
                self.data_views.wallet_manager.wallet.private_key,
                transaction.hash
            )
        )
        transaction.sign(signature)
        blockchain.add_transaction_to_pending(transaction)
        self.messages.success_message('Transaction added with success!')
        self.node.handle.broadcasts.sni.rpb.rni.bc.bp.rc.blb.bpb.broadcast_pending_block()

    def mine(self) -> None:
        if len(blockchain.pending_blocks) == 0:
            self.messages.error_message('there is no pending block!')
            return
        try:
            metadata: str = str(input('add metadata on block ?(optional):  ')).strip()
        except ValueError:
            self.messages.error_message()
            return
        self.messages.error_message(datetime.now().strftime("Mine initialized in %d/%m/%Y/%H:%M:%S"))
        self.data_views.wallet_manager.miner.mine(metadata or "0")
        self.messages.error_message(datetime.now().strftime("Mine terminated in %d/%m/%Y/%H:%M:%S"))
        self.node.handle.broadcasts.sni.rpb.rni.bc.bp.rc.blb.broadcast_last_block()
        self.messages.success_message(
            f'Recompensa de {blockchain.adjusts_path.adjust_reward(blockchain.get_index() - 1) / DIVISIBLE:.8f} BAL$ adicionada!')
        blockchain.new_pending_block()

    def add_peer(self) -> None:
        try:
            ip: str = str(input('IP of new peer:  ')).strip()
            port: int = int(input('PORT of new peer (Input -1 to use defalt port):  '))
        except ValueError:
            self.messages.error_message()
            return
        if port == -1:
            port = PORT
        self.node.handle.broadcasts.sni.rpb.rni.bc.bp.rc.blb.bpb.peers.add_peer(ip, port)
        self.node.handle.broadcasts.sni.rpb.rni.bc.bp.broadcast_peers()
        self.node.handle.broadcasts.sni.rpb.rni.bc.bp.rc.request_chain()
        self.node.handle.broadcasts.sni.rpb.request_pending_block()
        self.messages.success_message('Peer added with success!')

    def new_pending(self) -> None:
        if len(blockchain.pending_blocks) > 0:
            self.messages.error_message('there is still a pending block!')
            return
        blockchain.new_pending_block()
        self.node.handle.broadcasts.sni.rpb.rni.bc.bp.rc.blb.bpb.broadcast_pending_block()
        self.messages.success_message('New pending block added with success!')
