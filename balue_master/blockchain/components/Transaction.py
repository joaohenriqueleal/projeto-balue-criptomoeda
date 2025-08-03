from blockchain.components.ComponentsTemplate import *
import hashlib
import json


class Transaction(ComponentsTemplate):

    def __init__(self, sender: str, receiver: str, value: int, fee: int,
                 difficulty: int, metadata: str = "0") -> None:

        self.sender: str = sender
        self.receiver: str = receiver
        self.value: int = value
        self.fee: int = fee
        super().__init__(difficulty, metadata)

    def compute_hash(self, public_key: str, validation_timestamp: int, nonce: int,
                     miner_address: str = None, metadata: str = None) -> str:

        tr_dict: dict = {
            "sender": self.sender,
            "receiver": self.receiver,
            "value": self.value,
            "fee": self.fee,
            "id": self.id,
            "timestamp": self.timestamp,
            "validation_timestamp": validation_timestamp,
            "public_key": public_key,
            "difficulty": self.difficulty,
            "nonce": nonce,
            "metadata": self.metadata
        }
        return hashlib.sha256(json.dumps(
            tr_dict, sort_keys=True, ensure_ascii=False
        ).encode()).hexdigest()

    def validate(self, public_key: str, miner_address: str = None,
                 metadata: str = "0") -> None:

        prefix: str = "0" * self.difficulty
        nonce: int = 0
        while True:
            validation_timestamp: int = time.time_ns()
            computed_hash: str = self.compute_hash(
                public_key, validation_timestamp, nonce
            )
            if computed_hash.startswith(prefix):
                self.validation_timestamp = validation_timestamp
                self.hash = computed_hash
                self.nonce = nonce
                self.public_key = public_key
                return
            nonce += 1

    def sign(self, signature: str) -> None:
        self.signature = signature

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "value": self.value,
            "fee": self.fee,
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
