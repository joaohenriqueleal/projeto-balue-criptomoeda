from connection.broadcasts.BroadcastLastBlock import *


class RequestChain:

    def __init__(self) -> None:
        self.blb: 'BroadcastLastBlock' = BroadcastLastBlock()
        self.header: str = REQUEST_CHAIN_HEADER

    def request_chain(self) -> None:
        def rc() -> None:
            for peer in self.blb.bpb.peers.peers:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        payload: dict = {
                            "header": self.header,
                            "body": {
                                "port": PORT,
                                "chain_height": blockchain.get_index()
                            }
                        }
                        s.settimeout(TIMEOUT)
                        s.connect((peer["ip"], peer["port"]))
                        s.sendall(json.dumps(payload).encode())
                    except:
                        continue
        thread_rc = threading.Thread(target=rc)
        thread_rc.start()
