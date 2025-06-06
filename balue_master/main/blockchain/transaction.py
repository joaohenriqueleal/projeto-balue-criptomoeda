import time
import hashlib
import uuid
import json


class Transaction:

    def __init__(self, sender: str, receiver: str, value: float,
                 fees: float, public_key: str, metadata: str,
                 transaction_difficulty: int) -> None:

        self.sender = sender
        self.receiver = receiver
        self.value = value
        self.fees = fees
        self.timestamp = time.time_ns()
        self.validation_timestamp = 0
        self.id = str(uuid.uuid4())
        self.metadata = metadata
        self.public_key = public_key
        self.signature = None
        self.nonce = 0
        self.difficulty = transaction_difficulty
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        nonce = 0
        prefix = "0" * self.difficulty
        while True:
            validation_timestamp = time.time_ns()
            trx_dict = {
                "sender": self.sender,
                "receiver": self.receiver,
                "value": self.value,
                "fees": self.fees,
                "timestamp": self.timestamp,
                "validation_timestamp": validation_timestamp,
                "id": self.id,
                "metadata": self.metadata,
                "public_key": self.public_key,
                "nonce": nonce,
                "difficulty": self.difficulty
            }
            computed_hash = hashlib.sha256(
                json.dumps(trx_dict, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            if computed_hash.startswith(prefix):
                self.nonce = nonce
                self.validation_timestamp = validation_timestamp
                return computed_hash
            else: nonce += 1

    def sign_transaction(self, signature: str) -> None:
        self.signature = signature

    def transaction_to_dict(self) -> dict:
         return {
             "sender": self.sender,
             "receiver": self.receiver,
             "value": self.value,
             "fees": self.fees,
             "timestamp": self.timestamp,
             "validation_timestamp": self.validation_timestamp,
             "id": self.id,
             "metadata": self.metadata,
             "public_key": self.public_key,
             "signature": self.signature,
             "nonce": self.nonce,
             "difficulty": self.difficulty,
             "hash": self.hash
        }
