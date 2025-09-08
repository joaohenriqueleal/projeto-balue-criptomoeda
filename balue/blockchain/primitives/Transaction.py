from interfaces.PrimitivesInterface import *


class Transaction(PrimitivesInterface):

    def __init__(self, sender: str, receiver: str, value: int,
                 fee: int, difficulty: int, metadata: str = "0") -> None:

        self.sender: str = sender
        self.receiver: str = receiver
        self.value: int = value
        self.fee: int = fee

        super().__init__(difficulty, metadata)

    def compute_hash(self, public_key: str, nonce: int, validation_timestamp: int,
                     miner_address: str = None, metadata: str = None) -> str:

        trx_dict: dict = {
            "sender": self.sender,
            "receiver": self.receiver,
            "value": self.value,
            "fee": self.fee,
            "id": self.id,
            "version": self.version,
            "timestamp": self.timestamp,
            "validation_timestamp": validation_timestamp,
            "public_key": public_key,
            "nonce": nonce,
            "difficulty": self.difficulty,
            "metadata": self.metadata
        }
        return self.hasher.hasher(
            trx_dict
        )

    def validate(self, public_key: str, miner_address: str = None,
                 metadata: str = "0") -> None:

        prefix: str = "0" * self.difficulty
        nonce: int = 0
        while True:
            validation_timestamp: int = time.time_ns()
            computed_hash: str = self.compute_hash(
                public_key, nonce, validation_timestamp
            )
            if computed_hash.startswith(prefix):
                self.validation_timestamp = validation_timestamp
                self.public_key = public_key
                self.hash = computed_hash
                self.nonce = nonce
                return
            nonce += 1

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "value": self.value,
            "fee": self.fee,
            "id": self.id,
            "version": self.version,
            "timestamp": self.timestamp,
            "validation_timestamp": self.validation_timestamp,
            "public_key": self.public_key,
            "signature": self.signature,
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "metadata": self.metadata,
            "hash": self.hash
        }

    def sign(self, signature: str) -> None:
        self.signature = signature
