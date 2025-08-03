from connection.handle.Handle import *
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

    def node_infos(self) -> None:
        print(f'Local IP:  {self.local_ip}')
        print(f'Public IP:  {self.public_ip}')
        print(f'PORT:  {self.port}')
