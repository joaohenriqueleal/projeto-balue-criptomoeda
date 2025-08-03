from connection.handle.HandlePeer import *


class HandlePending:

    @staticmethod
    def handle(body: dict) -> None:
        if body["block"]["index"] == 0:
            if blockchain.validations.pending_validations.validate_pending_block(body["block"]):
                if len(blockchain.pending_blocks) > 0:
                    if len(body["block"]["transactions"]) > len(blockchain.pending_blocks[0].transactions):
                        blockchain.pending_blocks = []
                        blockchain.pending_blocks.append(Block.from_dict(body["block"]))
                        return
                else:
                    blockchain.pending_blocks = []
                    blockchain.pending_blocks.append(Block.from_dict(body["block"]))
        else:
            if blockchain.validations.pending_validations.validate_pending_block(
                    body["block"],
                    blockchain.adjusts_path.storage.load_block(body["block"]["index"] - 1)
            ):
                if len(blockchain.pending_blocks) > 0:
                    if len(body["block"]["transactions"]) > len(blockchain.pending_blocks[0].transactions):
                        blockchain.pending_blocks = []
                        blockchain.pending_blocks.append(Block.from_dict(body["block"]))
                        return
                else:
                    blockchain.pending_blocks = []
                    blockchain.pending_blocks.append(Block.from_dict(body["block"]))
