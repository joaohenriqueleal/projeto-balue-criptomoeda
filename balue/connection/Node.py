from connection.handle.Handle import *
import concurrent.futures
import requests


class Node:

    def __init__(self) -> None:
        self.handle: 'Handle' = Handle()

        self.local_ip: str = self.get_local_ip()
        self.public_ip: str = self.get_public_ip()
        self.port: int = self.handle.port

    @staticmethod
    def get_local_ip() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            return f"Erro ao obter IP local: {e}"

    @staticmethod
    def get_public_ip() -> str:
        try:
            response = requests.get("https://api.ipify.org", timeout=5)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            return f"Erro ao obter IP público: {e}"

    @staticmethod
    def count_peers(ip: str, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            payload: dict = {
                "header": COUNT_HEADER,
                "body": {
                    "port": PORT
                }
            }
            try:
                s.settimeout(SECOND_TIMEOUT)
                s.connect((ip, port))
                s.sendall(json.dumps(payload).encode())
                return True
            except:
                return False

    def network_infos(self) -> None:
        peers = self.handle.broadcasts.sni.rpb.rni.bc.bp.rc.blb.bpb.peers.peers

        if {"ip": self.local_ip, "port": self.port} in peers or {"ip": self.public_ip, "port": self.port} in peers:
            total_nodes = len(peers)
        else:
            total_nodes = len(peers) + 1

        print(f'Total Balue nodes:  {total_nodes}')

        online_nodes: int = 1
        peers_to_check = [
            peer for peer in peers
            if not ((peer["ip"] == self.local_ip or peer["ip"] == self.public_ip) and peer["port"] == self.port)
        ]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(lambda p: self.count_peers(p["ip"], p["port"]), peers_to_check)

        for is_online in results:
            if is_online:
                online_nodes += 1

        print(f'\033[;32m🟢\033[m Online nodes:  {online_nodes}')

    def node_infos(self) -> None:
        print(f'Local IP:  {self.local_ip}  (LAN)')
        print(f'Public IP:  {self.public_ip}  (GLOBAL)')
        print(f'PORT:  {self.port}')
        print('~' * 80)
        print('Network infos'.center(80))
        print('~' * 80)
        self.network_infos()
