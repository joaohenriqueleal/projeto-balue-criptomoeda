from mine.miner import *
import ipaddress
import socket
import threading
import requests


class Node:

    def __init__(self, port: int=8888) -> None:
        self.peers_path = 'balue/peers.json'
        os.makedirs(os.path.dirname(self.peers_path), exist_ok=True)

        self.public_ip = self.get_public_ip()
        self.local_ip = self.get_local_ip()
        self.port = port
        self.peers = []
        self.load_peers()

        thread_node = threading.Thread(target=self.start_node)
        thread_node.start()

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            return f"Erro ao obter IP: {e}"

    def get_public_ip(self):
        try:
            response = requests.get("https://api.ipify.org")
            return response.text
        except Exception as e:
            return f"Erro ao obter IP público: {e}"

    def save_peers(self) -> None:
        with open(self.peers_path, 'w', encoding='utf-8') as peers_file:
            json.dump(self.peers, peers_file, indent=4, ensure_ascii=False)

    def load_peers(self) -> None:
        if os.path.exists(self.peers_path):
            with open(self.peers_path, 'r', encoding='utf-8') as peers_file:
                self.peers = json.load(peers_file)
        else: self.save_peers()

    def ip_is_valid(self, ip: str) -> bool:
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def add_peer(self, ip: str, port: int) -> bool:
        if (ip == self.local_ip or ip == self.public_ip) and self.port == port:
            return False
        for peer in self.peers:
            if peer["ip"] == ip and peer["port"] == port:
                return False
        if not self.ip_is_valid(ip):
            return False
        if port < 1024 or port > 49151:
            return False
        new_peer = {"ip": ip, "port": port}
        self.peers.append(new_peer)
        self.save_peers()
        return True

    def peer_infos(self) -> None:
        print(f'IP público:  {self.public_ip}')
        print(f'IP local:  {self.local_ip}')
        print(f'PORTA:  {self.port}')

    def broadcast_pending_block(self) -> None:
        pending = chain_state.pending_block[0]
        for peer in self.peers:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.settimeout(5)
                    s.connect((peer["ip"], peer["port"]))
                    s.sendall(json.dumps(pending.block_to_dict()).encode())
                except: continue

    def broadcast_last_block(self) -> None:
        last_block = chain_state.load_block(len(chain_state.chain) - 1)
        for peer in self.peers:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.settimeout(5)
                    s.connect((peer["ip"], peer["port"]))
                    s.sendall(json.dumps(last_block).encode())
                except: continue

    def request_chain(self) -> None:
        for peer in self.peers:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                requisicao = {"type": "request_chain", "len": len(chain_state.chain), "port": self.port}
                try:
                    s.settimeout(5)
                    s.connect((peer["ip"], peer["port"]))
                    s.sendall(json.dumps(requisicao).encode())
                except: continue

    def broadcast_chain(self, length, ip, port) -> None:
        for i in range(length, len(chain_state.chain)):
            blk = chain_state.load_block(i)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.settimeout(5)
                    s.connect((ip, port))
                    s.sendall(json.dumps(blk).encode())
                    time.sleep(0.05)
                except: pass

    def broadcast_peers(self) -> None:
        for peer in self.peers:
            for peer_to_send in self.peers:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        s.settimeout(5)
                        s.connect((peer["ip"], peer["port"]))
                        s.sendall(json.dumps(peer_to_send).encode())
                        time.sleep(0.05)
                    except: pass

    def start_node(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', self.port))
        s.listen()
        while True:
            conn, addr = s.accept()
            thread_handle = threading.Thread(target=self.handle, args=(conn, addr,))
            thread_handle.start()
            time.sleep(0.1)

    def handle(self, conn, addr) -> None:
        with conn:
            while True:
                data = conn.recv(20004).decode()
                if not data:
                    break
                else:
                    data = json.loads(data)
                    if "index" in data:
                        if not data["miner_address"] and data["hash"] == "0" and data["nonce"] == 0:
                            if chain_state.validate_pending_block(data):
                                if len(chain_state.pending_block) > 0:
                                    if len(data["transactions"]) >= len(chain_state.pending_block[0].transactions):
                                        chain_state.pending_block = []
                                        chain_state.pending_block.append(Block.from_dict(data))
                                    else:
                                        break
                                else:
                                    chain_state.pending_block = []
                                    chain_state.pending_block.append(Block.from_dict(data))
                            else:
                                break
                        else:
                            chain_state.add_block(data)
                            if chain_state.chain_is_valid():
                                chain_state.save_chain()
                                if len(chain_state.pending_block) > 0:
                                    if data["index"] == chain_state.pending_block[0].index:
                                        chain_state.pending_block = []
                                else: break
                            else:
                                chain_state.chain.pop()
                                chain_state.save_chain()
                                os.remove(f'balue/chain/{len(chain_state.chain) + 1}.json')
                    elif "type" in data:
                        thread_broadcast_chain = threading.Thread(target=self.broadcast_chain, args=(data["len"], addr[0], data["port"],))
                        thread_broadcast_chain.start()
                    elif "ip" in data:
                        self.add_peer(data["ip"], data["port"])
            self.add_peer(addr[0], self.port)
