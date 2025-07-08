from mine.miner import *


class PeersTemplate(ABC):

    def __init__(self) -> None:
        self.peers: list[dict] = []

        self.peers_path: str
        self.load_peers()

    def load_peers(self):
        pass

    def save_peers(self):
        pass

    @staticmethod
    def is_valid_ip(ip: str):
        pass

    def add_peer(self, ip: str, port: int):
        pass
