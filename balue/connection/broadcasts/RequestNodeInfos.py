from connection.broadcasts.BroadcastChain import *


class RequestNodeInfos:

    def __init__(self) -> None:
        self.bc: 'BroadcastChain' = BroadcastChain()
        self.header: str = REQUEST_NODE_INFOS_HEADER

    def request_node_infos(self, ip: str, port: int) -> None:
        def rni() -> None:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    payload: dict = {
                        "header": self.header,
                        "body": {
                            "port": PORT
                        }
                    }
                    s.settimeout(TIMEOUT)
                    s.connect((ip, port))
                    s.sendall(json.dumps(payload).encode())
                except:
                    return
        thread_rni = threading.Thread(target=rni)
        thread_rni.start()
