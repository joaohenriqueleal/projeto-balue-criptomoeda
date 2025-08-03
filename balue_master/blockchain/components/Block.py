from blockchain.components.Transaction import *


class Block(ComponentsTemplate):

    def __init__(self, index: int, previous_hash: str, difficulty: int,
                 reward: int) -> None:

        self.index: int = index

        self.total_transactions: int = 0
        self.total_fees: int = 0

        self.transactions: list[dict] = []
        self.merkle_root: str = self.compute_merkle_root()

        self.reward: int = reward
        self.miner_address: Optional[str] = None

        self.previous_hash: str = previous_hash
        super().__init__(difficulty)

    def compute_merkle_root(self) -> str:
        return hashlib.sha256(json.dumps(
            self.transactions, sort_keys=True, ensure_ascii=False)
        .encode()).hexdigest()

    def compute_hash(self, public_key: str, validation_timestamp: int, nonce: int,
                     miner_address: str = None, metadata: str = None) -> str:

        block_dict: dict = {
            "index": self.index,
            "total_transactions": self.total_transactions,
            "total_fees": self.total_fees,
            "transactions": self.transactions,
            "merkle_root": self.merkle_root,
            "reward": self.reward,
            "miner_address": miner_address,
            "previous_hash": self.previous_hash,
            "id": self.id,
            "timestamp": self.timestamp,
            "validation_timestamp": validation_timestamp,
            "public_key": public_key,
            "difficulty": self.difficulty,
            "nonce": nonce,
            "metadata": metadata
        }
        return hashlib.sha256(json.dumps(
            block_dict, sort_keys=True, ensure_ascii=False)
        .encode()).hexdigest()

    def validate(self, public_key: str, miner_address: str = None,
                 metadata: str = "0") -> None:
        prefix: str = "0" * self.difficulty
        nonce: int = 0
        while True:
            validation_timestamp: int = time.time_ns()
            computed_hash: str = self.compute_hash(
                public_key, validation_timestamp,
                nonce, miner_address, metadata
            )
            if computed_hash.startswith(prefix):
                self.public_key = public_key
                self.nonce = nonce
                self.hash = computed_hash
                self.validation_timestamp = validation_timestamp
                self.miner_address = miner_address
                self.metadata = metadata
                return
            nonce += 1

    def add_transaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction.to_dict())
        self.total_transactions += 1
        self.total_fees += transaction.fee
        self.merkle_root = self.compute_merkle_root()

    def sign(self, signature: str) -> None:
        self.signature = signature

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "total_transactions": self.total_transactions,
            "total_fees": self.total_fees,
            "transactions": self.transactions,
            "merkle_root": self.merkle_root,
            "reward": self.reward,
            "miner_address": self.miner_address,
            "previous_hash": self.previous_hash,
            "id": self.id,
            "timestamp": self.timestamp,
            "validation_timestamp": self.validation_timestamp,
            "public_key": self.public_key,
            "signature": self.signature,
            "difficulty": self.difficulty,
            "nonce": self.nonce,
            "metadata": self.metadata,
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

        block.total_transactions = data.get("total_transactions", 0)
        block.total_fees = data.get("total_fees", 0)
        block.transactions = data.get("transactions", [])
        block.merkle_root = data.get("merkle_root", block.compute_merkle_root())
        block.miner_address = data.get("miner_address")

        block.id = data.get("id")
        block.timestamp = data.get("timestamp")
        block.validation_timestamp = data.get("validation_timestamp")
        block.public_key = data.get("public_key")
        block.signature = data.get("signature")
        block.nonce = data.get("nonce")
        block.metadata = data.get("metadata")
        block.hash = data.get("hash")

        return block
