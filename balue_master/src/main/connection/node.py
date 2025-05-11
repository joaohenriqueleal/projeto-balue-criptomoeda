from src.main.mine.miner import *
import socket
import requests
import threading


class Node:

    def __init__(self, port=8888):
        self.peers_path = 'peers.json'
        self.peers = []
        self.load_peers()
        self.local_ip = self.get_local_ip()
        self.public_ip = self.get_public_ip()
        self.port = port

    def save_peers(self):
        caminho = os.path.join('balue', self.peers_path)
        if os.path.exists(caminho):
            with open(caminho, 'w', encoding='utf-8') as chain_file:
                json.dump(self.peers, chain_file, ensure_ascii=False, indent=4)
        else:
            os.makedirs('balue', exist_ok=True)
            caminho = os.path.join('balue', self.peers_path)
            with open(caminho, 'w', encoding='utf-8') as chain_file:
                json.dump(self.peers, chain_file, ensure_ascii=False, indent=4)

    def load_peers(self):
        caminho = os.path.join('balue', self.peers_path)
        if os.path.exists(caminho):
            with open(caminho, 'r', encoding='utf-8') as chain_file:
                self.peers = json.load(chain_file)
        else:
            self.save_peers()

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            return f"Erro ao obter IP local: {e}"

    def get_public_ip(self):
        try:
            response = requests.get("https://api.ipify.org?format=text")
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            return f"Erro ao obter IP público: {e}"

    def peer_infos(self):
        print(f'Ip local: {self.local_ip}, para conexões locais na mesma wi-fi.')
        print(f'IP público: {self.public_ip} usado para conexões internacionais.')
        print(f'PORTA: {self.port}')

    def add_peer(self, ip, port):
        for peer in self.peers:
            if peer["ip"] == ip and peer["port"] == port:
                return
        peer = {"ip": ip, "port": port}
        self.peers.append(peer)
        self.save_peers()

    def start_node(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', self.port))
        s.listen(10)
        while True:
            conn, addr = s.accept()
            thread_handle = threading.Thread(target=self.handle, args=(conn, addr))
            thread_handle.start()

    def broadcast_pending(self):
        pending = b.pending_block[0]
        for peer in self.peers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((peer["ip"], peer["port"]))
                s.sendall(json.dumps(pending.block_to_dict()).encode())
            except:
                continue

    def broadcast_chain(self):
        block = b.chain[-1]
        for peer in self.peers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((peer["ip"], peer["port"]))
                s.sendall(json.dumps(block).encode())
            except:
                continue

    def request_chain(self):
        req = {"type": "r_c", "port": self.port, "len": len(b.chain)}
        for peer in self.peers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((peer["ip"], peer["port"]))
                s.sendall(json.dumps(req).encode())
                break
            except:
                continue

    def broadcast_total_chain(self, ip, port, len):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.sendall(json.dumps(b.chain[len:]).encode())
        except Exception as e:
            print(e)

    def broadcast_peers(self):
        all_peers = [{"ip": self.public_ip, "port": self.port}, {"ip": self.local_ip, "port": self.port}] + self.peers
        for peer in self.peers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((peer["ip"], peer["port"]))
                s.sendall(json.dumps(all_peers).encode())
                s.close()
            except:
                continue

    def handle(self, conn, addr):
        with conn:
            while True:
                try:
                    data = conn.recv(20048).decode()
                    if not data:
                        break
                    block = json.loads(data)
                    if isinstance(block, dict) and block.get("type") == "r_c":
                        thread_broadcast_total_chain = threading.Thread(
                            target=self.broadcast_total_chain,
                            args=(addr[0], block["port"], block.get("len"))
                        )
                        thread_broadcast_total_chain.start()
                    elif isinstance(block, list) and block and isinstance(block[0], dict) and block[0].get('ip'):
                        for peer in block:
                            self.add_peer(peer["ip"], peer["port"])
                        break
                    elif isinstance(block, list):
                        original_len = len(b.chain)
                        for blk in block:
                            b.chain.append(blk)
                        if b.chain_is_valid():
                            b.save_chain()
                            break
                        else:
                            b.chain = b.chain[:original_len]

                    elif isinstance(block, dict):
                        if block.get("nonce") == 0 and block.get("hash") == "0" and not block.get("miner_address"):
                            block_obj = Block.from_dict(block)
                            if b.is_valid_pending_block(block_obj):
                                if len(b.pending_block) > 0:
                                    if block_obj.index == b.pending_block[0].index:
                                        if len(block_obj.transactions) >= len(b.pending_block[0].transactions):
                                            b.pending_block = []
                                            b.add_block_to_pending(Block.from_dict(block))
                                        else:
                                            break
                                    else:
                                        break
                                else:
                                    b.pending_block = []
                                    b.add_block_to_pending(Block.from_dict(block))
                            else:
                                break
                        else:
                            b.chain.append(block)
                            if b.chain_is_valid():
                                if b.pending_block[0].index == block["index"]:
                                    b.pending_block = []
                                b.save_chain()
                                return
                            else:
                                b.chain.remove(block)
                                break
                    else:
                        break
                except Exception as e:
                    print(f"[ERRO] Falha no handle: {e}")
                    break
        self.add_peer(addr[0], self.port)
