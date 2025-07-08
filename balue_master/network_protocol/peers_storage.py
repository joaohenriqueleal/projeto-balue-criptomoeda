from network_protocol.template_peers import *
import ipaddress


class PeersStorage:

    def __init__(self) -> None:
        self.peers: list[dict] = []

        self.peers_path: str = 'balue/nodes/peers/peers.json'
        os.makedirs(os.path.dirname(self.peers_path), exist_ok=True)
        self.load_peers()

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

    def add_peer(self, ip: str, port: int) -> str:
        if self.is_valid_ip(ip) and 45_000 > port > 1024:
            new_peer: dict = {"ip": ip, "port": port}
            if (ip == LOCAL_IP or ip == PUBLIC_IP) and port == PORT:
                return 'Não pode adicionar você mesmo!'
            for peer in self.peers:
                if peer == new_peer:
                    return 'Peer já existe!'
            self.peers.append(new_peer)
            self.save_peers()
            return 'Peer adicionado com sucesso!'
        else:
            return 'Node inválido!'
