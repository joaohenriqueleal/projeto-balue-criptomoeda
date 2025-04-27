from balue_master.src.main.blockchain.transaction import *


class Block:

    def __init__(self, index: int, previous_hash: str, difficulty: int,
                 miner_address: str or None, miner_public_key: str or None,
                 miner_signature: str or None, reward: float):

        self.index =  index
        self.timestamp = time.time_ns()
        self.transactions = []
        self.block_identifier = str(uuid.uuid4())
        self.difficulty = difficulty
        self.nonce = 0
        self.reward = reward
        self.total_transactions_fees = 0.0
        self.miner_address = miner_address
        self.miner_public_key = miner_public_key
        self.previous_hash = previous_hash
        self.hash = "0"
        self.miner_signature = miner_signature

    def calculate_block_hash(self, nonce):
        block_dict = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "block_identifier": self.block_identifier,
            "difficulty": self.difficulty,
            "reward": self.reward,
            "total_transactions_fees": self.total_transactions_fees,
            "nonce": nonce,
            "miner_address": self.miner_address,
            "miner_public_key": self.miner_public_key,
            "previous_hash": self.previous_hash
        }
        block_json = json.dumps(block_dict, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(block_json.encode()).hexdigest()

    def mine_block(self):
        prefixo = "0" * self.difficulty
        nonce = 0
        while True:
            hash_calculado = self.calculate_block_hash(nonce)
            if hash_calculado.startswith(prefixo):
                self.hash = hash_calculado
                self.nonce = nonce
                break
            else:
                nonce += 1

    def add_transaction(self, transaction: Transaction):
        self.total_transactions_fees += transaction.fees
        self.transactions.append(transaction.transaction_to_dict())

    @classmethod
    def from_dict(cls, data: dict):
        block = cls(
            index=data["index"],
            previous_hash=data["previous_hash"],
            difficulty=data["difficulty"],
            miner_address=data.get("miner_address"),
            miner_public_key=data.get("miner_public_key"),
            miner_signature=data.get("miner_signature"),
            reward=data["reward"]
        )
        block.timestamp = data["timestamp"]
        block.transactions = data["transactions"]
        block.block_identifier = data["block_identifier"]
        block.total_transactions_fees = data["total_transactions_fees"]
        block.nonce = data["nonce"]
        block.hash = data["hash"]
        return block

    def block_to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "block_identifier": self.block_identifier,
            "difficulty": self.difficulty,
            "reward": self.reward,
            "total_transactions_fees": self.total_transactions_fees,
            "nonce": self.nonce,
            "miner_address": self.miner_address,
            "miner_public_key": self.miner_public_key,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "miner_signature": self.miner_signature
        }
