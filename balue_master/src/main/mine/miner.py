from balue_master.src.main.blockchain.blockchain import *


class Miner:

    def __init__(self, miner_address, miner_public_key, miner_private_key):
        self.miner_address = miner_address
        self.miner_public_key = miner_public_key
        self.miner_private_key = miner_private_key

    def mine(self):
        pending = b.pending_block[0]
        pending.miner_address = self.miner_address
        pending.miner_public_key = chave_publica_para_json(self.miner_public_key)
        pending.mine_block()
        sign = assinar_hash(self.miner_private_key, pending.hash)
        pending.miner_signature = assinatura_para_json(sign)
        b.pending_block[0] = pending
        b.add_block_to_chain()

        if b.chain_is_valid():
            b.save_chain()
            return True
        else:
            print('inválido!')
            b.chain.remove(pending.block_to_dict())
            b.save_chain()
            return False
