from blockchain.primitives.Transaction import *


class Block(PrimitivesInterface):

    def __init__(self, index: int, previous_hash: str,
                 reward: int, difficulty: int) -> None:

        super().__init__(difficulty)

        self.index: int = index

        self.total_transactions: int = 0
        self.total_fees: int = 0

        self.transactions: list[dict] = []
        self.merkle_root: str = "0" * 64
        self.compute_merkle_root()

        self.reward: int = reward
        self.miner_address: Optional[str] = None

        self.previous_hash: str = previous_hash

    def compute_merkle_root(self) -> None:
        if not self.transactions:
            self.merkle_root = "0" * 64
            return

        hashes = [tx["hash"] for tx in self.transactions]

        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])
            new_hashes = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                new_hashes.append(self.hasher.hasher(combined))
            hashes = new_hashes

        self.merkle_root = hashes[0]

    def compute_hash(self, public_key: str, nonce: int, validation_timestamp: int,
                     miner_address: str = None, metadata: str = None) -> str:

        block_dict: dict = {
            "index": self.index,
            "total_transactions": self.total_transactions,
            "total_fees": self.total_fees,
            "transactions": self.transactions,
            "merkle_root": self.merkle_root,
            "reward": self.reward,
            "miner_address": miner_address,
            "id": self.id,
            "version": self.version,
            "timestamp": self.timestamp,
            "validation_timestamp": validation_timestamp,
            "public_key": public_key,
            "nonce": nonce,
            "difficulty": self.difficulty,
            "metadata": metadata,
            "previous_hash": self.previous_hash
        }
        return self.hasher.hasher(
            block_dict
        )

    def validate(self, public_key: str, miner_address: str = None,
                 metadata: str = "0") -> None:

        prefix: str = "0" * self.difficulty
        nonce: int = 0
        while True:
            validation_timestamp: int = time.time_ns()
            computed_hash: str = self.compute_hash(
                public_key, nonce, validation_timestamp,
                miner_address, metadata
            )
            if computed_hash.startswith(prefix):
                self.validation_timestamp = validation_timestamp
                self.miner_address = miner_address
                self.public_key = public_key
                self.hash = computed_hash
                self.metadata = metadata
                self.nonce = nonce
                return
            nonce += 1
            if nonce % 100_000 == 0:
                print(f'\033[;31m[INFO] Actual nonce:  {nonce}\033[m /'
                      f' \033[38;5;15;48;5;54mMining block #{self.index}\033[0m'
                      f' \033[33m with {self.difficulty} of difficulty... \033[m')

    def sign(self, signature: str) -> None:
        self.signature = signature

    def add_transaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction.to_dict())
        self.total_transactions += 1
        self.total_fees += transaction.fee
        self.compute_merkle_root()

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "total_transactions": self.total_transactions,
            "total_fees": self.total_fees,
            "transactions": self.transactions,
            "merkle_root": self.merkle_root,
            "reward": self.reward,
            "miner_address": self.miner_address,
            "id": self.id,
            "version": self.version,
            "timestamp": self.timestamp,
            "validation_timestamp": self.validation_timestamp,
            "public_key": self.public_key,
            "signature": self.signature,
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Block':
        block = cls(
            index=data["index"],
            previous_hash=data.get("previous_hash", "0" * 64),
            reward=data["reward"],
            difficulty=data["difficulty"]
        )

        block.total_transactions = data.get("total_transactions", 0)
        block.total_fees = data.get("total_fees", 0)
        block.transactions = data.get("transactions", [])
        block.merkle_root = data.get("merkle_root", "0" * 64)
        block.miner_address = data.get("miner_address")
        block.id = data.get("id")
        block.version = data.get("version")
        block.timestamp = data.get("timestamp")
        block.validation_timestamp = data.get("validation_timestamp")
        block.public_key = data.get("public_key")
        block.signature = data.get("signature")
        block.nonce = data.get("nonce")
        block.metadata = data.get("metadata")
        block.hash = data.get("hash")

        return block
