import hashlib
import time
import json
import uuid


class Transaction:

    def __init__(self, sender: str, receiver: str, value: float,
                 fees: float, signature: str or None, public_key: str or None, metadata: str or None):

        self.sender = sender
        self.receiver = receiver
        self.value = value
        self.fees = fees
        self.timestamp = time.time_ns()
        self.signature = signature
        self.public_key = public_key
        self.transaction_identifier = str(uuid.uuid4())
        self.metadata = metadata if metadata is not None else "0"
        self.hash = self.calculate_transaction_hash()

    def calculate_transaction_hash(self):
        tr_dict = {
            "sender": self.sender,
            "receiver": self.receiver,
            "value": self.value,
            "fees": self.fees,
            "timestamp": self.timestamp,
            "public_key": self.public_key,
            "transaction_identifier": self.transaction_identifier,
            "metadata": self.metadata
        }
        tr_json = json.dumps(tr_dict, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(tr_json.encode()).hexdigest()

    def transaction_to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "value": self.value,
            "fees": self.fees,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "public_key": self.public_key,
            "transaction_identifier": self.transaction_identifier,
            "metadata": self.metadata,
            "hash": self.hash
        }
