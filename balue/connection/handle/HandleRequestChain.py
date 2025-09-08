from connection.handle.HandlePending import *


class HandleRequestChain:

    @staticmethod
    def handle(body: dict, addr: tuple, broadcasts: 'Broadcasts') -> None:
        try:
            port: int = body.get("port", -1)
            broadcasts.sni.rpb.rni.bc.broadcast_chain(
                addr[0], port
            )
        except:
            return
