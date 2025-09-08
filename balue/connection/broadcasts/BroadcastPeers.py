from connection.broadcasts.RequestChain import *


class BroadcastPeers:

    def __init__(self) -> None:
        self.rc: 'RequestChain' = RequestChain()
        self.header: str = PEER_HEADER
        self.threads: list[threading.Thread] = []
        self.awaiting_threads: list[threading.Thread] = []

    @staticmethod
    def send_to_peer(ip: str, port: int, payload: dict) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(TIMEOUT)
                s.connect((ip, port))
                s.sendall(json.dumps(payload).encode())
        except:
            return

    def broadcast_peers(self) -> None:
        def bp() -> None:
            peers = self.rc.blb.bpb.peers.peers
            for peer in peers:
                for peer_to_send in peers:
                    payload = {
                        "header": self.header,
                        "body": peer_to_send
                    }
                    thread_peer = threading.Thread(
                        target=self.send_to_peer,
                        args=(peer["ip"], peer["port"], payload)
                    )
                    if len(self.threads) < MAX_THREADS:
                        thread_peer.start()
                        self.threads.append(thread_peer)
                    else:
                        self.awaiting_threads.append(thread_peer)

                    for t in self.threads[:]:
                        if not t.is_alive():
                            self.threads.remove(t)
                            if self.awaiting_threads:
                                next_thread = self.awaiting_threads.pop(0)
                                next_thread.start()
                                self.threads.append(next_thread)
        thread_bp = threading.Thread(target=bp)
        thread_bp.start()
