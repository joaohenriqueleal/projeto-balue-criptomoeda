from abc import ABC, abstractmethod
from typing import Optional
import uuid
import time


class ComponentsTemplate(ABC):

    @abstractmethod
    def __init__(self, difficulty: int, metadata: str = "0") -> None:
        self.id: str = str(uuid.uuid4())

        self.timestamp: int = time.time_ns()
        self.validation_timestamp: int = 0

        self.public_key: Optional[str] = None
        self.signature: Optional[str] = None

        self.difficulty: int = difficulty
        self.nonce: int = 0

        self.metadata: str = metadata
        self.hash: str = "0" * 32

    @abstractmethod
    def compute_hash(self, public_key: str, validation_timestamp: int, nonce: int,
                     miner_address: str = None, metadata: str = None) -> str:
        pass

    @abstractmethod
    def validate(self, public_key: str, miner_address: str = None,
                 metadata: str = "0") -> None:
        pass

    @abstractmethod
    def sign(self, signature: str) -> None:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass
