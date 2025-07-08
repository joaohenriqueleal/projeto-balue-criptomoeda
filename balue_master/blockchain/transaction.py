from blockchain.template import *
import hashlib
import json


class Transaction(Template):

    def __init__(self, sender: str, receiver: str, value: float,
                 fee: float, difficulty: int, metadata: str) -> None:

        self.sender: str = sender
        self.receiver: str = receiver
        self.value: float = value
        self.fee: float = fee
        super().__init__(difficulty, metadata)

    def compute_hash(self, validation_timestamp: int, public_key: str,
                     nonce: int, miner_address: str = None, metadata = None) -> str:
        trx_dict: dict = {
            "sender": self.sender,
            "receiver": self.receiver,
            "value": self.value,
            "fee": self.fee,
            "validation_timestamp": validation_timestamp,
            "public_key": public_key,
            "difficulty": self.difficulty,
            "timestamp": self.timestamp,
            "id": self.id,
            "metadata": self.metadata,
            "nonce": nonce
        }
        return hashlib.sha256(json.dumps(
            trx_dict, sort_keys=True, ensure_ascii=False
        ).encode()).hexdigest()

    def validate(self, public_key: str, miner_address: str = None,
                 metadata = None) -> None:

        prefix: str = "0" * self.difficulty
        nonce: int = 0
        while True:
            validation_timestamp: int = time.time_ns()
            computed_hash: str = self.compute_hash(validation_timestamp,
                                                   public_key, nonce)
            if computed_hash.startswith(prefix):
                self.public_key = public_key
                self.validation_timestamp = validation_timestamp
                self.nonce = nonce
                self.hash = computed_hash
                break
            else: nonce += 1

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "value": self.value,
            "fee": self.fee,
            "validation_timestamp": self.validation_timestamp,
            "public_key": self.public_key,
            "signature": self.signature,
            "difficulty": self.difficulty,
            "timestamp": self.timestamp,
            "id": self.id,
            "metadata": self.metadata,
            "nonce": self.nonce,
            "hash": self.hash
        }

    def sign(self, signature: str) -> None:
        self.signature = signature
