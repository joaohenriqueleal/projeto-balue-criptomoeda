from blockchain.validations import *


class Blockchain:

    def __init__(self) -> None:
        self.pending_block: list['Block'] = []
        self.validations: Validations = Validations()
        self.create_genesis()

    def create_genesis(self) -> None:
        if len(self.validations.adjusts.storage.chain) == 0:
            self.new_pending_block()

    def new_pending_block(self) -> None:
        if len(self.pending_block) == 0:
            new_block: 'Block' = Block(self.index(), self.get_previous_hash(),
                                       self.validations.adjusts.adjust_difficulty(self.index()),
                                       self.validations.adjusts.adjust_reward(self.index()))
            self.pending_block.append(new_block)

    def index(self) -> int:
        return len(self.validations.adjusts.storage.chain)

    def get_previous_hash(self) -> str:
        if len(self.validations.adjusts.storage.chain) == 0:
            return "0"
        else:
            return self.validations.adjusts.storage.load_block(
                len(self.validations.adjusts.storage.chain) - 1
            )["hash"]

    def add_pending_block_to_chain(self) -> None:
        if len(self.pending_block) > 0:
            p: 'Block' = self.pending_block[0]
            if p.hash != "0" and p.nonce != 0 and p.miner_address:
                self.validations.adjusts.storage.add_block(p.to_dict())
                self.pending_block = []

    def add_transaction_to_pending(self, transaction: Transaction) -> None:
        if len(self.pending_block) == 0:
            self.new_pending_block()
            self.pending_block[0].add_transaction(transaction)
        else:
            self.pending_block[0].add_transaction(transaction)

    def mine_pending(self, public_key: str, miner_address: str,
                     metadata: str = "0") -> None:
            if len(self.pending_block) > 0:
                self.pending_block[0].validate(public_key,
                                               miner_address, metadata)

    def sign_pending(self, signature: str) -> None:
        if len(self.pending_block) > 0:
            self.pending_block[0].sign(signature)


blockchain: 'Blockchain' = Blockchain()
