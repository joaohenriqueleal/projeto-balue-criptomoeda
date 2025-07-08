from abc import ABC, abstractmethod
import uuid
import time


class Template(ABC):

    @abstractmethod
    def __init__(self, difficulty: int, metadata: str = "0") -> None:
        self.validation_timestamp: int = 0
        self.public_key: str or None = None
        self.signature: str or None = None
        self.difficulty: int = difficulty
        self.metadata: str = metadata
        self.timestamp: int = time.time_ns()
        self.id: str = str(uuid.uuid4())
        self.nonce: int = 0
        self.hash: str = "0"

    @abstractmethod
    def compute_hash(self, validation_timestamp: int, public_key: str,
                     nonce: int, miner_address: str = None,
                     metadata: str = "0") -> str:
        pass

    @abstractmethod
    def validate(self, public_key: str, miner_address: str = None,
                 metadata: str = "0") -> None:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @abstractmethod
    def sign(self, signature: str) -> None:
        pass
