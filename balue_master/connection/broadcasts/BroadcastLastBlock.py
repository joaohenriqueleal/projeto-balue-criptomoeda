from connection.broadcasts.BroadcastPendingBlock import *


class BroadcastLastBlock:

    def __init__(self) -> None:
        self.bpb: 'BroadcastPendingBlock' = BroadcastPendingBlock()
        self.header: str = BLOCK_HEADER

    def broadcast_last_block(self) -> None:
        def blb() -> None:
            last_block: dict = blockchain.adjusts_path.storage.load_block(
                blockchain.get_index() - 1
            )
            for peer in self.bpb.peers.peers:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        payload: dict = {
                            "header": self.header,
                            "body": {
                                "this_block_height": last_block["index"],
                                "block": last_block
                            }
                        }
                        s.settimeout(TIMEOUT)
                        s.connect((peer["ip"], peer["port"]))
                        s.sendall(json.dumps(payload).encode())
                    except:
                        continue
        thread_blb = threading.Thread(target=blb)
        thread_blb.start()
