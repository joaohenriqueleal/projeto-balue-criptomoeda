from connection.broadcasts.BroadcastPeers import *


class BroadcastChain:

    def __init__(self) -> None:
        self.bp: 'BroadcastPeers' = BroadcastPeers()
        self.header: str = BLOCK_HEADER

    def broadcast_chain(self, ip: str, port: int, chain_height: int) -> None:
        def bc() -> None:
            for i in range(chain_height, len(blockchain.adjusts_path.storage.chain)):
                block: dict = blockchain.adjusts_path.storage.load_block(i)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        payload: dict = {
                            "header": self.header,
                            "body": {
                                "this_block_height": block["index"],
                                "block": block
                            }
                        }
                        s.settimeout(TIMEOUT)
                        s.connect((ip, port))
                        s.sendall(json.dumps(payload).encode())
                    except:
                        return
        thread_bc = threading.Thread(target=bc)
        thread_bc.start()
