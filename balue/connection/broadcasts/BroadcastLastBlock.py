from connection.broadcasts.BroadcastPendingBlock import *


class BroadcastLastBlock:

    def __init__(self) -> None:
        self.bpb: 'BroadcastPendingBlock' = BroadcastPendingBlock()
        self.threads: list[threading.Thread] = []
        self.awaiting_threads: list[threading.Thread] = []
        self.header: str = BLOCK_HEADER

    @staticmethod
    def send_to_peer(ip: str, port: int, payload: dict) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(TIMEOUT)
                s.connect((ip, port))
                s.sendall(json.dumps(payload).encode())
            except:
                return

    def broadcast_last_block(self) -> None:
        def blb() -> None:
            if len(blockchain.adjusts.storage.chain) == 0:
                last_block: dict = blockchain.adjusts.storage.load_block(
                blockchain.get_index()
            )
            else:
                last_block: dict = blockchain.adjusts.storage.load_block(
                    blockchain.get_index() - 1
                )
            for peer in self.bpb.peers.peers:
                try:
                    payload: dict = {
                        "header": self.header,
                        "body": {
                            "this_block_height": last_block["index"],
                            "block": last_block
                        }
                    }
                    thread_peer = threading.Thread(target=self.send_to_peer, args=(peer["ip"], peer["port"], payload))
                    if not len(self.threads) > MAX_THREADS:
                        thread_peer.start()
                        self.threads.append(thread_peer)
                    else:
                        self.awaiting_threads.append(thread_peer)
                    for t in self.threads[:]:
                        if not t.is_alive():
                            self.threads.remove(t)
                            if len(self.awaiting_threads) > 0:
                                thread_to_append: threading.Thread = self.awaiting_threads[0]
                                self.awaiting_threads.remove(thread_to_append)
                                thread_to_append.start()
                                self.threads.append(thread_to_append)
                except:
                    continue
        thread_blb = threading.Thread(target=blb)
        thread_blb.start()
