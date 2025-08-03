from mine.Miner import *
import ipaddress


class PeersStorage:

    def __init__(self) -> None:
        self.peers_path: str = PEERS_PATH

        self.peers: list[dict] = []
        os.makedirs(os.path.dirname(self.peers_path), exist_ok=True)

        self.load_peers()

    def load_peers(self) -> None:
        if os.path.exists(self.peers_path):
            with open(self.peers_path, 'r', encoding='utf-8') as pf:
                self.peers = json.load(pf)
        else:
            self.save_peers()

    def save_peers(self) -> None:
        with open(self.peers_path, 'w', encoding='utf-8') as pf:
            pf.write(json.dumps(self.peers, indent=4, ensure_ascii=False))

    @staticmethod
    def is_ipaddress(ip: str) -> bool:
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def add_peer(self, ip: str, port: int) -> None:
        if not self.is_ipaddress(ip):
            return
        if port < 1024 or port > 65500:
            return
        new_peer: dict = {"ip": ip, "port": port}
        if new_peer in self.peers:
            return
        self.peers.append(new_peer)
        self.save_peers()
