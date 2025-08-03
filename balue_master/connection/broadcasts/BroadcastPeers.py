from connection.broadcasts.RequestChain import *


class BroadcastPeers:

    def __init__(self) -> None:
        self.rc: 'RequestChain' = RequestChain()
        self.header: str = PEER_HEADER

    def broadcast_peers(self) -> None:
        def bp() -> None:
            for peer in self.rc.blb.bpb.peers.peers:
                for peer_to_send in self.rc.blb.bpb.peers.peers:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        try:
                            payload: dict = {
                                "header": self.header,
                                "body": peer_to_send
                            }
                            s.settimeout(TIMEOUT)
                            s.connect((peer["ip"], peer["port"]))
                            s.sendall(json.dumps(payload).encode())
                        except:
                            continue
        thread_bp = threading.Thread(target=bp())
        thread_bp.start()
