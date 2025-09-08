from connection.handle.HandleRequestChain import *


class HandleRequestNodeInfos:

    @staticmethod
    def handle(body: dict, addr: tuple, broadcasts: 'Broadcasts') -> None:
        try:
            port: int = body.get("port", -1)
            broadcasts.sni.send_node_infos(
                addr[0], port
            )
        except:
            return
