from abc import ABC, abstractmethod
from typing import Optional
from mine.Hasher import *
from balueConf import *
import uuid
import time


class PrimitivesInterface(ABC):

    @abstractmethod
    def __init__(self, difficulty: int, metadata: str = "0") -> None:
        self.id: str = str(uuid.uuid4())
        self.version: str = VERSION

        self.timestamp: int = time.time_ns()
        self.validation_timestamp: int = 0

        self.signature: Optional[str] = None
        self.public_key: Optional[str] = None

        self.hasher: 'Hasher' = Hasher()
        self.nonce: int = 0
        self.difficulty: int = difficulty

        self.hash: str = "0" * 64
        self.metadata: str = metadata

    @abstractmethod
    def compute_hash(self, public_key: str, nonce: int, validation_timestamp: int,
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
