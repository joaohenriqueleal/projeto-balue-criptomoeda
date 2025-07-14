from network_protocol.broadcasts import *


class Handle:

    def __init__(self) -> None:
        self.public_ip: str = PUBLIC_IP
        self.local_ip: str = LOCAL_IP
        self.port: int = PORT

        self.broadcasts: 'Broadcasts' = Broadcasts()

        self.chain_lock: 'threading' = threading.Lock()
        self.peers_lock: 'threading' = threading.Lock()
        self.black_list_lock: 'threading' = threading.Lock()

        thread_start = threading.Thread(target=self.start_node)
        thread_start.start()

    def start_node(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', self.port))
        s.listen()
        while True:
            conn, addr = s.accept()
            thread_handle = threading.Thread(target=self.handle, args=(conn, addr,))
            thread_handle.start()

    def handle_pending(self, addr, pending: dict) -> None:
        if blockchain.validations.validate_pending_block(pending):
            if len(blockchain.pending_block) > 0:
                if blockchain.pending_block[0].total_transactions <= pending["total_transactions"]:
                    blockchain.pending_block = []
                    blockchain.pending_block.append(Block.from_dict(pending))
            else:
                blockchain.pending_block.append(Block.from_dict(pending))
        else:
            self.broadcasts.black_list.add_peer(addr[0], self.port)

    def handle_block(self, addr, block: dict) -> None:
        with self.chain_lock:
            if block["index"] == 0:
                if blockchain.validations.validate_block(block):
                    blockchain.validations.adjusts.storage.add_block(block)
                    if len(blockchain.pending_block) > 0:
                        if blockchain.pending_block[0].index == block["index"]:
                            blockchain.pending_block = []
                else:
                    self.broadcasts.black_list.add_peer(addr[0], PORT)
            else:
                previous_block: dict = blockchain.validations.adjusts.storage.load_block(block["index"] - 1)
                if blockchain.validations.validate_block(block, previous_block):
                    blockchain.validations.adjusts.storage.add_block(block)
                    if len(blockchain.pending_block) > 0:
                        if blockchain.pending_block[0].index == block["index"]:
                            blockchain.pending_block = []
                else:
                    self.broadcasts.black_list.add_peer(addr[0], PORT)

    def handle_peer(self, peer: dict) -> None:
        with self.peers_lock:
            self.broadcasts.peers.add_peer(peer["ip"], peer["port"])

    def handle_black_list_peer(self, peer: dict) -> None:
        with self.black_list_lock:
            self.broadcasts.black_list.add_peer(peer["ip"], peer["port"])

    def handle(self, conn, addr) -> None:
        with conn:
            while True:
                if {"ip": addr[0], "port": PORT} in self.broadcasts.black_list.peers:
                    return
                data = conn.recv(20000048).decode()
                if not data:
                    break
                try:
                    content: dict = json.loads(data)
                    if content["header"] == self.broadcasts.pending_header:
                        self.handle_pending(addr, content["data"])
                    elif content["header"] == self.broadcasts.block_header:
                        self.handle_block(addr, content["data"])
                    elif content["header"] == self.broadcasts.peers_header:
                        self.handle_peer(content["data"])
                    elif content["header"] == self.broadcasts.black_list_peers_header:
                        self.handle_black_list_peer(content["data"])
                    elif content["header"] == self.broadcasts.request_chain_header:
                        self.broadcasts.broadcast_total_chain(addr[0], content["data"]["port"],
                                                              content["data"]["chain_length"])
                except Exception as e:
                    print(e)
            self.broadcasts.peers.add_peer(addr[0], self.port)
