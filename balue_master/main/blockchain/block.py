from main.blockchain.transaction import *


class Block:

    def __init__(self, index: int, difficulty: int, reward: float,
                 previous_hash: str) -> None:
        self.index = index
        self.timestamp = time.time_ns()
        self.mine_timestamp = 0
        self.id = str(uuid.uuid4())
        self.difficulty = difficulty
        self.nonce = 0
        self.reward = reward
        self.total_fees = 0
        self.transactions = []
        self.merkle_root = "0"
        self.miner_address = None
        self.miner_public_key = None
        self.miner_signature = None
        self.previous_hash = previous_hash
        self.hash = "0"

    def compute_merkle_root(self) -> str:
        return hashlib.sha256(
            json.dumps(self.transactions, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def add_transaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction.transaction_to_dict())
        self.total_fees += transaction.fees

    def compute_hash(self, miner_address: str, miner_public_key: str,
                     nonce: int) -> str or int:

        mine_timestamp = time.time_ns()
        merkle_root = self.compute_merkle_root()
        block_dict = {
            "index": self.index,
            "timestamp": self.timestamp,
            "mine_timestamp": mine_timestamp,
            "id": self.id,
            "difficulty": self.difficulty,
            "nonce": nonce,
            "reward": self.reward,
            "total_fees": self.total_fees,
            "transactions": self.transactions,
            "merkle_root": merkle_root,
            "miner_address": miner_address,
            "miner_public_key": miner_public_key,
            "previous_hash": self.previous_hash
        }
        return merkle_root, mine_timestamp, hashlib.sha256(
            json.dumps(block_dict, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def mine_block(self, miner_address: str, miner_public_key: str) -> None:
        nonce = 0
        prefix = "0" * self.difficulty
        while True:
            merkle_root, mine_timestamp, computed_hash = self.compute_hash(miner_address,
                miner_public_key, nonce)
            if computed_hash.startswith(prefix):
                self.hash = computed_hash
                self.nonce = nonce
                self.mine_timestamp = mine_timestamp
                self.merkle_root = merkle_root
                self.miner_address = miner_address
                self.miner_public_key = miner_public_key
                break
            else: nonce += 1

    def sign_block(self, signature: str) -> None:
        self.miner_signature = signature

    def block_to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "mine_timestamp": self.mine_timestamp,
            "id": self.id,
            "difficulty": self.difficulty,
            "nonce": self.nonce,
            "reward": self.reward,
            "total_fees": self.total_fees,
            "transactions": self.transactions,
            "merkle_root": self.merkle_root,
            "miner_address": self.miner_address,
            "miner_public_key": self.miner_public_key,
            "miner_signature": self.miner_signature,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, blk: dict) -> 'Block':
        block = cls(
            index=blk["index"],
            difficulty=blk["difficulty"],
            reward=blk["reward"],
            previous_hash=blk["previous_hash"]
        )
        block.timestamp = blk["timestamp"]
        block.mine_timestamp = blk["mine_timestamp"]
        block.id = blk["id"]
        block.nonce = blk["nonce"]
        block.total_fees = blk["total_fees"]
        block.transactions = blk["transactions"]  # já está no formato de dicionários
        block.merkle_root = blk["merkle_root"]
        block.miner_address = blk["miner_address"]
        block.miner_public_key = blk["miner_public_key"]
        block.miner_signature = blk["miner_signature"]
        block.hash = blk["hash"]
        return block
