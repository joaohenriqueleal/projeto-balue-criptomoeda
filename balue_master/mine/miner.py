from blockchain.timechain import *


class Miner:

    def __init__(self, private_key, public_key, address) -> None:
        self.miner_private_key = private_key
        self.miner_public_key = public_key
        self.miner_address = address

    def unique_mine(self, metadata: str = "0") -> bool or int:
        wallet_sign: 'WalletMethods' = WalletMethods()

        while True:
            if len(blockchain.pending_block) > 0:
                blockchain.mine_pending(wallet_sign.public_key_to_json(self.miner_public_key), self.miner_address, metadata)
                sign = wallet_sign.sign_hash(self.miner_private_key, blockchain.pending_block[0].hash)
                blockchain.sign_pending(wallet_sign.signature_to_json(sign))
                blockchain.add_pending_block_to_chain()
                if blockchain.validations.chain_is_valid():
                    return True
                else:
                    os.remove(f'balue/chain/{len(blockchain.validations.adjusts.storage.chain) - 1}.json')
                    blockchain.validations.adjusts.storage.chain.pop()
                    return False
            else:
                blockchain.new_pending_block()
                continue

    def infinite_mine(self, metadata: str = "0") -> bool or int:
        wallet_sign: 'WalletMethods' = WalletMethods()

        while True:
            if len(blockchain.pending_block) > 0:
                blockchain.mine_pending(wallet_sign.public_key_to_json(self.miner_public_key), self.miner_address, metadata)
                sign = wallet_sign.sign_hash(self.miner_private_key, blockchain.pending_block[0].hash)
                blockchain.sign_pending(wallet_sign.signature_to_json(sign))
                blockchain.add_pending_block_to_chain()
                if blockchain.validations.chain_is_valid():
                    print(f'\033[;32mBlock #{len(blockchain.validations.adjusts.storage.chain) - 1} Mined!\033[m')
                    print('~' * 80)
                    pass
                else:
                    os.remove(f'balue/chain/{len(blockchain.validations.adjusts.storage.chain) - 1}.json')
                    blockchain.validations.adjusts.storage.chain.pop()
                    return False
            else:
                blockchain.new_pending_block()
            blockchain.new_pending_block()
