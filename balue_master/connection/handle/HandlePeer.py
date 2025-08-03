from connection.handle.HandleBlock import *


class HandlePeer:

    def __init__(self) -> None:
        self.peers_lock: 'threading' = threading.Lock()

    def handle(self, body: dict, broadcasts: 'Broadcasts') -> None:
        try:
            ip: str = body.get("ip", '')
            port: int = body.get("port", -1)
            with self.peers_lock:
                broadcasts.sni.rpb.rni.bc.bp.rc.blb.bpb.peers.add_peer(ip, port)
        except:
            return
