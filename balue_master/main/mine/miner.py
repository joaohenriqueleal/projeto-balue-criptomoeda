from blockchain.blockchain import *

class Miner:

    def __init__(self, miner_private_key: str,
                 miner_public_key: str, miner_address: str) -> None:

        self.miner_private_key = miner_private_key
        self.miner_public_key = miner_public_key
        self.miner_address = miner_address

    def mine(self) -> bool or int:
        if len(chain_state.pending_block) > 0:
            chain_state.mine_pending(self.miner_address, chave_publica_para_json(self.miner_public_key))

            sign = assinar_hash(self.miner_private_key, chain_state.pending_block[0].hash)
            chain_state.sign_pending(assinatura_para_json(sign))
            chain_state.add_block_to_chain()

            if chain_state.chain_is_valid():
                return True
            else:
                chain_state.chain.pop()
                chain_state.save_chain()
                return False
        else:
            return 13
