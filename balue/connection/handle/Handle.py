from connection.handle.HandleRequestPending import *
from json import JSONDecodeError


class Handle:

    def __init__(self) -> None:
        self.broadcasts: 'Broadcasts' = Broadcasts()
        self.port: int = PORT

        self.handle_block: 'HandleBlock' = HandleBlock()
        self.handle_peer: 'HandlePeer' = HandlePeer()
        self.handle_pending: 'HandlePending' = HandlePending()
        self.handle_request_chain: 'HandleRequestChain' = HandleRequestChain()
        self.handle_request_node_infos: 'HandleRequestNodeInfos' = HandleRequestNodeInfos()
        self.handle_request_pending: 'HandleRequestPending' = HandleRequestPending()

        thread_start_node = threading.Thread(target=self.start_node)
        thread_start_node.start()

    def start_node(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', self.port))
        s.listen()
        while True:
            conn, addr = s.accept()
            thread_handle = threading.Thread(target=self.handle, args=(conn, addr,))
            thread_handle.start()

    def handle(self, conn, addr) -> None:
        with conn:
            while True:
                self.broadcasts.sni.rpb.rni.bc.bp.rc.blb.bpb.peers.add_peer(addr[0], PORT)
                try:
                    data = conn.recv(20000048).decode()
                    data = json.loads(data)
                except JSONDecodeError:
                    return
                if not data:
                    break
                if data.get("header", {}) == BLOCK_HEADER:
                    self.handle_block.handle(data.get("body", {}))
                elif data.get("header", {}) == PEER_HEADER:
                    self.handle_peer.handle(data.get("body", {}), self.broadcasts)
                elif data.get("header", {}) == PENDING_BLOCK_HEADER:
                    self.handle_pending.handle(data.get("body", {}))
                elif data.get("header", {}) == REQUEST_CHAIN_HEADER:
                    self.handle_request_chain.handle(data.get("body", {}),
                            addr, self.broadcasts)
                elif data.get("header", {}) == REQUEST_NODE_INFOS_HEADER:
                    self.handle_request_node_infos.handle(data.get("body", {}),
                            addr, self.broadcasts)
                elif data.get("header", {}) == REQUEST_PENDING_BLOCK_HEADER:
                    self.handle_request_pending.handle(data.get("body", {}),
                            addr)
                elif data.get("header", {}) == COUNT_HEADER:
                    pass
