from blockchain.Adjusts import *


class Blockchain:

    def __init__(self) -> None:
        self.chain_version: str = VERSION
        self.adjusts = Adjusts()

        self.pending_blocks: list['Block'] = []
        self.create_genesis()

    def create_genesis(self) -> None:
        if len(self.adjusts.storage.chain) == 0:
            self.new_pending_block()

    def new_pending_block(self) -> None:
        if len(self.pending_blocks) == 0:
            block: 'Block' = Block(
                self.get_index(),
                self.get_previous_hash(),
                self.adjusts.adjust_reward(self.get_index()),
                self.adjusts.adjust_difficulty(self.get_index())
            )
            self.pending_blocks.append(block)

    def get_index(self) -> int:
        return len(self.adjusts.storage.chain)

    def get_previous_hash(self) -> str:
        if len(self.adjusts.storage.chain) == 0:
            return "0" * 64
        return self.adjusts.storage.load_block(self.get_index() - 1)["hash"]

    def add_mined_block_to_chain(self) -> None:
        if len(self.pending_blocks) > 0:
            p: 'Block' = self.pending_blocks[0]
            if p.hash != "0" * 64 and p.miner_address and p.signature:
                self.adjusts.storage.add_block(p.to_dict())
                self.pending_blocks = []

    def validate_pending(self, public_key: str, miner_address: str,
                         metadata: str = "0") -> None:
        if len(self.pending_blocks) > 0:
            self.pending_blocks[0].validate(public_key, miner_address, metadata)

    def sign_pending(self, signature: str) -> None:
        if len(self.pending_blocks) > 0:
            self.pending_blocks[0].sign(signature)

    def add_transaction_to_pending(self, transaction: Transaction) -> None:
        if len(self.pending_blocks) > 0:
            self.pending_blocks[0].add_transaction(transaction)


blockchain: 'Blockchain' = Blockchain()
