from connection.peers.PeersStorage import *
import threading
import socket


class BroadcastPendingBlock:

    def __init__(self) -> None:
        self.peers: 'PeersStorage' = PeersStorage()
        self.header: str = PENDING_BLOCK_HEADER

    def broadcast_pending_block(self) -> None:
        def bpb() -> None:
            pending_block: dict = blockchain.pending_blocks[0].to_dict()
            for peer in self.peers.peers:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        payload: dict = {
                            "header": self.header,
                            "body": {
                                "block": pending_block
                            }
                        }
                        s.settimeout(TIMEOUT)
                        s.connect((peer["ip"], peer["port"]))
                        s.sendall(json.dumps(payload).encode())
                    except:
                        continue
        thread_bpb = threading.Thread(target=bpb)
        thread_bpb.start()
