from blockchain.transaction import *


class Block(Template):

    def __init__(self, index: int, previous_hash: str, difficulty: int,
                 reward: float) -> None:

        self.index: int = index
        self.total_transactions: int = 0
        self.miner_address: str or None = None
        self.metadata: str or None = None
        self.reward: float = reward
        self.transactions: list[dict] = []
        self.merkle_root: str = "0"
        self.compute_merkle_root()
        self.total_fees: float = 0
        self.previous_hash: str = previous_hash
        super().__init__(difficulty)

    def compute_hash(self, validation_timestamp: int, public_key: str,
                     nonce: int, miner_address: str = None, metadata: str = "0") -> str:

        block_dict: dict = {
            "index": self.index,
            "total_transactions": self.total_transactions,
            "miner_address": miner_address,
            "metadata": metadata,
            "reward": self.reward,
            "merkle_root": self.merkle_root,
            "transactions": self.transactions,
            "total_fees": self.total_fees,
            "previous_hash": self.previous_hash,
            "validation_timestamp": validation_timestamp,
            "public_key": public_key,
            "difficulty": self.difficulty,
            "timestamp": self.timestamp,
            "id": self.id,
            "nonce": nonce
        }
        return hashlib.sha256(json.dumps(
            block_dict, sort_keys=True, ensure_ascii=False
        ).encode()).hexdigest()

    def validate(self, public_key: str, miner_address: str = None,
                 metadata: str = "0") -> None:

        prefix: str = "0" * self.difficulty
        nonce: int = 0
        while True:
            validation_timestamp: int = time.time_ns()
            computed_hash: str = self.compute_hash(validation_timestamp,
                                                   public_key, nonce, miner_address, metadata)
            if computed_hash.startswith(prefix):
                self.validation_timestamp = validation_timestamp
                self.nonce = nonce
                self.miner_address = miner_address
                self.public_key = public_key
                self.metadata = metadata
                self.hash = computed_hash
                break
            else: nonce += 1

    def sign(self, signature: str) -> None:
        self.signature = signature

    def compute_merkle_root(self) -> None:
        self.merkle_root = hashlib.sha256(json.dumps(
            self.transactions
        ).encode()).hexdigest()

    def add_transaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction.to_dict())
        self.total_transactions += 1
        self.total_fees += transaction.fee
        self.compute_merkle_root()

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "total_transactions": self.total_transactions,
            "miner_address": self.miner_address,
            "metadata": self.metadata,
            "reward": self.reward,
            "merkle_root": self.merkle_root,
            "transactions": self.transactions,
            "total_fees": self.total_fees,
            "previous_hash": self.previous_hash,
            "validation_timestamp": self.validation_timestamp,
            "public_key": self.public_key,
            "signature": self.signature,
            "difficulty": self.difficulty,
            "timestamp": self.timestamp,
            "id": self.id,
            "nonce": self.nonce,
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Block':
        block = cls(
            index=data["index"],
            previous_hash=data["previous_hash"],
            difficulty=data["difficulty"],
            reward=data["reward"]
        )

        block.total_transactions = data["total_transactions"]
        block.miner_address = data.get("miner_address")
        block.metadata = data.get("metadata")
        block.transactions = data["transactions"]
        block.merkle_root = data["merkle_root"]
        block.total_fees = data["total_fees"]
        block.validation_timestamp = data["validation_timestamp"]
        block.public_key = data["public_key"]
        block.signature = data["signature"]
        block.timestamp = data["timestamp"]
        block.id = data["id"]
        block.nonce = data["nonce"]
        block.hash = data["hash"]

        return block
