from network_protocol.black_list import *
import threading
import socket


class Broadcasts:

    def __init__(self) -> None:
        self.peers: 'PeersStorage' = PeersStorage()
        self.black_list: 'BlackListPeersStorage' = BlackListPeersStorage()

        # Headers.
        self.pending_header: str = 'pending_block'
        self.block_header: str = 'block'
        self.request_chain_header: str = 'request_chain'
        self.peers_header: str = 'peer'
        self.black_list_peers_header: str = 'black_list_peer'

    def broadcast_pending_block(self) -> None:
        if len(blockchain.pending_block) > 0:
            pending: dict = blockchain.pending_block[0].to_dict()
            def bpb() -> None:
                for peer in self.peers.peers:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        try:
                            payload: dict = {
                                "header": self.pending_header,
                                "data": pending
                            }
                            s.settimeout(TIMEOUT)
                            s.connect((peer["ip"], peer["port"]))
                            s.sendall(json.dumps(payload).encode())
                        except socket.timeout:
                            continue
                        except ConnectionRefusedError:
                            continue
            thread_bpb = threading.Thread(target=bpb)
            thread_bpb.start()

    def broadcast_last_block(self) -> None:
        def blb() -> None:
            last_block: dict = blockchain.validations.adjusts.storage.load_block(blockchain.index() - 1)
            for peer in self.peers.peers:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        payload: dict = {
                            "header": self.block_header,
                            "data": last_block
                        }
                        s.settimeout(TIMEOUT)
                        s.connect((peer["ip"], peer["port"]))
                        s.sendall(json.dumps(payload).encode())
                    except socket.timeout:
                        continue
                    except ConnectionRefusedError:
                        continue
        thread_blb = threading.Thread(target=blb)
        thread_blb.start()

    def request_chain(self) -> None:
        def rq() -> None:
            for peer in self.peers.peers:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        payload: dict = {
                            "header": self.request_chain_header,
                            "data": {
                                "chain_length": blockchain.index(),
                                "port": PORT
                            }
                        }
                        s.settimeout(TIMEOUT)
                        s.connect((peer["ip"], peer["port"]))
                        s.sendall(json.dumps(payload).encode())
                    except socket.timeout:
                        continue
                    except ConnectionRefusedError:
                        continue
        thread_rq = threading.Thread(target=rq)
        thread_rq.start()

    def broadcast_total_chain(self, ip: str, port: int,
                              chain_length: int) -> None:
        def btc() -> None:
            for i in range(chain_length, len(blockchain.validations.adjusts.storage.chain)):
                block: dict = blockchain.validations.adjusts.storage.load_block(i)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        payload: dict = {
                            "header": self.block_header,
                            "data": block
                        }
                        s.settimeout(TIMEOUT)
                        s.connect((ip, port))
                        s.sendall(json.dumps(payload).encode())
                    except socket.timeout:
                        continue
                    except ConnectionRefusedError:
                        continue
        thread_btc = threading.Thread(target=btc)
        thread_btc.start()

    def broadcast_peers(self) -> None:
        def bp() -> None:
            for peer in self.peers.peers:
                for peer_to_send in self.peers.peers:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        try:
                            payload: dict = {
                                "header": self.peers_header,
                                "data": peer_to_send
                            }
                            s.settimeout(TIMEOUT)
                            s.connect((peer["ip"], peer["port"]))
                            s.sendall(json.dumps(payload).encode())
                        except socket.timeout:
                            continue
                        except ConnectionRefusedError:
                            continue
        thread_bp = threading.Thread(target=bp)
        thread_bp.start()

    def broadcast_black_list(self) -> None:
        def bbl() -> None:
            for peer in self.peers.peers:
                for peer_to_send in self.black_list.peers:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        try:
                            payload: dict = {
                                "header": self.black_list_peers_header,
                                "data": peer_to_send
                            }
                            s.settimeout(TIMEOUT)
                            s.connect((peer["ip"], peer["port"]))
                            s.sendall(json.dumps(payload).encode())
                        except socket.timeout:
                            continue
                        except ConnectionRefusedError:
                            continue
        thread_bbl = threading.Thread(target=bbl)
        thread_bbl.start()
