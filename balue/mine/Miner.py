from validations.Validations import *


class Miner:

    def __init__(self, miner_private_key, miner_public_key,
                 miner_address) -> None:

        self.miner_private_key = miner_private_key
        self.miner_public_key = miner_public_key
        self.miner_address = miner_address
        self.wallet_methods: 'WalletMethods' = WalletMethods()

    def mine(self, metadata: str = "0") -> None:
        if len(blockchain.pending_blocks) > 0:
            blockchain.validate_pending(
                self.wallet_methods.public_key_to_json(self.miner_public_key),
                self.miner_address,
                metadata
            )
            signature = self.wallet_methods.signature_to_json(
                self.wallet_methods.sign_hash(self.miner_private_key,
                        blockchain.pending_blocks[0].hash
                )
            )
            blockchain.sign_pending(signature)
            if blockchain.pending_blocks[0].index != 0:
                previous_block: dict = blockchain.adjusts.storage.load_block(blockchain.get_index() - 1)
                if validations.validate_block(blockchain.pending_blocks[0].to_dict(), previous_block):
                    blockchain.add_mined_block_to_chain()
                    blockchain.pending_blocks = []
                else:
                    print('INVÁLIDO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            else:
                if validations.validate_block(blockchain.pending_blocks[0].to_dict()):
                    blockchain.add_mined_block_to_chain()
                    blockchain.pending_blocks = []
        else:
            print('\033[;31m there is no pending block!\033[m')
