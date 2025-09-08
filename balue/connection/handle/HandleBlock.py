from connection.broadcasts.Broadcasts import *


class HandleBlock:

    def __init__(self) -> None:
        self.chain_lock: 'threading' = threading.Lock()
        self.rules: 'Rules' = Rules()

    def handle(self, body: dict) -> None:
        try:
            with self.chain_lock:
                self.rules.apply(body["block"])
                if blockchain.adjusts.storage.load_block(len(blockchain.adjusts.storage.chain) - 1)["index"] == blockchain.pending_blocks[0].index:
                    blockchain.pending_blocks = []
        except:
            return
