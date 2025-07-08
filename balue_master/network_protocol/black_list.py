from network_protocol.peers_storage import *


class BlackListPeersStorage(PeersTemplate):

    def __init__(self) -> None:
        self.peers_path: str = 'balue/nodes/black_list/black_list.json'
        os.makedirs(os.path.dirname(self.peers_path), exist_ok=True)
        super().__init__()

    def load_peers(self) -> None:
        if os.path.exists(self.peers_path):
            with open(self.peers_path, 'r', encoding='utf-8') as peers_path:
                self.peers = json.load(peers_path)
        else: self.save_peers()

    def save_peers(self) -> None:
        with open(self.peers_path, 'w', encoding='utf-8') as peers_path:
            peers_path.write(json.dumps(self.peers, ensure_ascii=False, indent=4))

    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def add_peer(self, ip: str, port: int) -> None:
        if self.is_valid_ip(ip) and 45_000 > port > 1024:
            new_peer: dict = {"ip": ip, "port": port}
            if ip == LOCAL_IP or ip == PUBLIC_IP and port == PORT:
                return None
            for peer in self.peers:
                if peer == new_peer:
                    return
            self.peers.append(new_peer)
            self.save_peers()
