from connection.broadcasts.RequestPendingBlock import *


class SendNodeInfos:

    def __init__(self) -> None:
        self.rpb: 'RequestPendingBlock' = RequestPendingBlock()
        self.header: str = NODE_INFOS_HEADER

    def send_node_infos(self, ip: str, port: int) -> None:
        def sni() -> None:
             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                 try:
                     payload: dict = {
                         "header": self.header,
                         "body": {
                             "port": PORT,
                             "chain_version": VERSION,
                             "chain_height": blockchain.get_index() - 1
                         }
                     }
                     s.settimeout(TIMEOUT)
                     s.connect((ip, port))
                     s.sendall(json.dumps(payload).encode())
                 except:
                     return
        thread_sni = threading.Thread(target=sni)
        thread_sni.start()
