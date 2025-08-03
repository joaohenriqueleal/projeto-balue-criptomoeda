from connection.broadcasts.Broadcasts import *


class HandleBlock:

    def __init__(self) -> None:
        self.chain_lock: 'threading' = threading.Lock()

    def handle(self, body: dict) -> None:
        try:
            with self.chain_lock:
                height: int = body["this_block_height"]
                if height != body["block"]["index"]:
                    return
                if height == 0:
                    if blockchain.validations.validate_block(body["block"]):
                        if len(blockchain.pending_blocks) > 0:
                            if height == blockchain.pending_blocks[0].index:
                                blockchain.pending_blocks = []
                        blockchain.adjusts_path.storage.add_block(body["block"])
                else:
                    if blockchain.validations.validate_block(body["block"], blockchain.adjusts_path.storage.load_block(height - 1)):
                        if len(blockchain.pending_blocks) > 0:
                            if height == blockchain.pending_blocks[0].index:
                                blockchain.pending_blocks = []
                        blockchain.adjusts_path.storage.add_block(body["block"])
        except:
            return
