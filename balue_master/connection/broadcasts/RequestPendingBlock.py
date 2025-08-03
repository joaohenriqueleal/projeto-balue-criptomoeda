from connection.broadcasts.RequestNodeInfos import *


class RequestPendingBlock:

    def __init__(self) -> None:
        self.rni: 'RequestNodeInfos' = RequestNodeInfos()
        self.header: str = REQUEST_PENDING_BLOCK_HEADER

    def request_pending_block(self) -> None:
        def rpb() -> None:
            for peer in self.rni.bc.bp.rc.blb.bpb.peers.peers:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        payload: dict = {
                            "header": self.header,
                            "body": {
                                "port": PORT
                            }
                        }
                        s.settimeout(TIMEOUT)
                        s.connect((peer["ip"], peer["port"]))
                        s.sendall(json.dumps(payload).encode())
                    except:
                        continue
        thread_rpb = threading.Thread(target=rpb)
        thread_rpb.start()
