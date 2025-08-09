from connection.handle.HandleRequestNodeInfos import *


class HandleRequestPending:

    @staticmethod
    def handle(body: dict, addr: tuple) -> None:
        try:
            port: int = body.get("port", -1)
        except:
            return
        if len(blockchain.pending_blocks) > 0:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    payload: dict = {
                        "header": PENDING_BLOCK_HEADER,
                        "body": {
                            "block": blockchain.pending_blocks[0].to_dict()
                        }
                    }
                    s.settimeout(TIMEOUT)
                    s.connect((addr[0], port))
                    s.sendall(json.dumps(payload).encode())
                except:
                    return
