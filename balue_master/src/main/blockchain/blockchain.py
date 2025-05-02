from balue_master.src.main.blockchain.block import *
from balue_master.src.main.wallet.wallet import *
import os


class Blockchain:

    def __init__(self):
        self.chain_path = 'blockchain.json'
        self.chain = []
        self.pending_block = []
        self.load_chain()
        self.create_genesis_block()

    def create_genesis_block(self):
        if len(self.chain) == 0:
            genesis = Block(0, "0", self.adjust_difficulty(),None, None, None, self.adjust_reward())
            self.add_block_to_pending(genesis)

    def save_chain(self):
        with open(self.chain_path, 'w', encoding='utf-8') as chain_file:
            json.dump(self.chain, chain_file, ensure_ascii=False, indent=4)

    def load_chain(self):
        if os.path.exists(self.chain_path):
            with open(self.chain_path, 'r', encoding='utf-8') as chain_file:
                self.chain = json.load(chain_file)
        else:
            self.save_chain()

    def add_block_to_pending(self, block: Block):
        if not len(self.pending_block):
            self.pending_block.append(block)

    def add_block_to_chain(self):
        pending = self.pending_block[0]
        if pending.nonce == 0 and pending.hash == 0 and not pending.miner_address: return
        else:
            self.chain.append(pending.block_to_dict())
            self.save_chain()
            self.pending_block = []

    def add_transaction_to_pending(self, tr: Transaction):
        if len(self.pending_block) == 0:
            block = Block(self.index(), self.previous_hash(), self.adjust_difficulty(), None, None, None, self.adjust_reward())
            self.pending_block.append(block)
            self.pending_block[0].add_transaction(tr)
        else:
            self.pending_block[0].add_transaction(tr)

    def calculate_block_hash_after_mining(self, blk):
        block_dict = {
            "index": blk["index"],
            "timestamp": blk["timestamp"],
            "transactions": blk["transactions"],
            "block_identifier": blk["block_identifier"],
            "difficulty": blk["difficulty"],
            "reward": blk["reward"],
            "total_transactions_fees": blk["total_transactions_fees"],
            "nonce": blk["nonce"],
            "miner_address": blk["miner_address"],
            "miner_public_key": blk["miner_public_key"],
            "previous_hash": blk["previous_hash"]
        }
        block_json = json.dumps(block_dict, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(block_json.encode()).hexdigest()

    def calculate_transaction_hash_after_mining(self, trc):
        tr_dict = {
            "sender": trc["sender"],
            "receiver": trc["receiver"],
            "value": trc["value"],
            "fees": trc["fees"],
            "timestamp": trc["timestamp"],
            "public_key": trc["public_key"],
            "transaction_identifier": trc["transaction_identifier"],
            "metadata": trc["metadata"]
        }
        tr_json = json.dumps(tr_dict, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(tr_json.encode()).hexdigest()

    def is_valid_pending_block(self, block: Block) -> bool:
        if block.index != len(self.chain):
            return False
        if block.difficulty != self.verify_difficulty(block.index):
            return False
        if block.reward != self.verify_reward(block.index):
            return False
        if len(self.chain) == 0:
            if block.previous_hash != "0":
                return False
        else:
            if block.previous_hash != self.chain[-1]["hash"]:
                return False
        if block.hash != "0" or block.nonce != 0:
            return False
        if block.miner_address is not None or block.miner_signature is not None or block.miner_public_key is not None:
            return False
        for tr in block.transactions:
            saldo = self.get_balance(tr["sender"])
            if saldo - (tr["value"] + tr["fees"]) < 0:
                return False
            if tr["hash"] != self.calculate_transaction_hash_after_mining(tr):
                return False
            if not verificar_assinatura(
                    json_para_chave_publica(tr["public_key"]),
                    tr["sender"],
                    bytes.fromhex(tr["hash"]),
                    json_para_assinatura(tr["signature"])
            ):
                return False
            if tr["fees"] != self.adjust_mining_fees():
                return False
        return True

    def validate_block(self, current_block, previous_block=None) -> bool:
        if not previous_block:
            if current_block["index"] != 0:
                return False
            if current_block["difficulty"] != self.verify_difficulty(current_block["index"]):
                return False
            if current_block["reward"] != self.verify_reward(current_block["index"]):
                return False
            if current_block["previous_hash"] != "0":
                return False
            if not verificar_assinatura(json_para_chave_publica(current_block["miner_public_key"]), current_block["miner_address"], bytes.fromhex(current_block["hash"]), json_para_assinatura(current_block["miner_signature"])):
                return False
            if current_block["hash"] != self.calculate_block_hash_after_mining(current_block):
                return False
            for tr in current_block["transactions"]:
                sender_balance = self.get_balance(tr["sender"])
                if sender_balance - (tr["value"] + tr["fees"]) < 0:
                    return False
                if tr["hash"] != self.calculate_transaction_hash_after_mining(tr):
                    return False
                if not verificar_assinatura(json_para_chave_publica(tr["public_key"]), tr["sender"], bytes.fromhex(tr["hash"]), json_para_assinatura(tr["signature"])):
                    return False
                if tr["fees"] != self.adjust_mining_fees():
                    return False
        else:
            if current_block["index"] != (previous_block["index"] + 1):
                return False
            if current_block["difficulty"] != self.verify_difficulty(current_block["index"]):
                return False
            if current_block["reward"] != self.verify_reward(current_block["index"]):
                return False
            if current_block["previous_hash"] != previous_block["hash"]:
                return False
            if not verificar_assinatura(json_para_chave_publica(current_block["miner_public_key"]), current_block["miner_address"], bytes.fromhex(current_block["hash"]), json_para_assinatura(current_block["miner_signature"])):
                return False
            if current_block["hash"] != self.calculate_block_hash_after_mining(current_block):
                return False
            for tr in current_block["transactions"]:
                sender_balance = self.get_balance(tr["sender"])
                if sender_balance - (tr["value"] + tr["fees"]) < 0:
                    return False
                if tr["hash"] != self.calculate_transaction_hash_after_mining(tr):
                    return False
                if not verificar_assinatura(json_para_chave_publica(tr["public_key"]), tr["sender"], bytes.fromhex(tr["hash"]), json_para_assinatura(tr["signature"])):
                    return False
                if tr["fees"] != self.adjust_mining_fees():
                    return False
        return True

    def chain_is_valid(self) -> bool:
        for i in range(0, len(self.chain)):
            if not i:
                current_block = self.chain[i]
                if not self.validate_block(current_block):
                    return False
            else:
                current_block = self.chain[i]
                previous_block = self.chain[i - 1]
                if not self.validate_block(current_block, previous_block):
                    return False
        return True

    def get_balance(self, address):
        balance = 0
        for blk in self.chain:
            if blk["miner_address"] == address:
                balance += (blk["reward"] + blk["total_transactions_fees"])
            for tr in blk["transactions"]:
                if tr["sender"] == address:
                    balance -= (tr["value"] + tr["fees"])
                if tr["receiver"] == address:
                    balance += tr["value"]
        return balance

    def print_chain(self):
        for block in self.chain[-10:]:
            print(f'Block, {block["index"]}, Hash: {block["hash"][:15]}...')
            print(f'      with {len(block["transactions"])} transactions.')
            print('~' * 80)

    def index(self): return len(self.chain)
    def previous_hash(self): return self.chain[-1]["hash"]

    def adjust_difficulty(self):
        interval_adjust = 2016
        initial_difficulty = 4
        tempo_alvo = 600000000000 # 10 minutos em nanosegundos.

        if len(self.chain) < interval_adjust:
            return initial_difficulty

        timestamps = []
        soma = 0
        media = 0
        for block in self.chain[-interval_adjust:]:
            timestamps.append(block["timestamp"])
        for i in range(0, len(timestamps)):
            if i == 0:
                continue
            else:
                actual = timestamps[i]
                prev = timestamps[i - 1]
                if actual >= prev:
                    diference = actual - prev
                    soma += diference
                else:
                    diference = prev - actual
                    soma += diference
        if media >= tempo_alvo:
            return self.chain[-1]["difficulty"] - 1
        else:
            return self.chain[-1]["difficulty"] + 1

    def get_blocks_until_index(self, index, interval_adjust):
        start = max(0, index - interval_adjust)
        return self.chain[start:index]

    def verify_difficulty(self, index):
        interval_adjust = 2016
        initial_difficulty = 4
        tempo_alvo = 600000000000  # 10 minutos em nanosegundos.

        if index < interval_adjust:
            return initial_difficulty

        timestamps = []
        blocks = self.get_blocks_until_index(index, interval_adjust)

        for block in blocks:
            timestamps.append(block["timestamp"])

        soma = 0
        for i in range(1, len(timestamps)):
            actual = timestamps[i]
            prev = timestamps[i - 1]
            diference = abs(actual - prev)
            soma += diference

        media = soma // (len(timestamps) - 1)

        last_block_difficulty = self.chain[index - 1]["difficulty"]

        if media >= tempo_alvo:
            return last_block_difficulty - 1
        else:
            return last_block_difficulty + 1

    def adjust_reward(self):
        initial_reward = 3.125
        halving_interval = 300_000
        halvings = self.index() // halving_interval
        if initial_reward / (2 ** halvings) < 0.01:
            return 0.01
        return initial_reward / (2 ** halvings)
    def verify_reward(self, index):
        initial_reward = 3.125
        halving_interval = 300_000
        halvings = index // halving_interval
        if initial_reward / (2 ** halvings) < 0.01:
            return 0.01
        return initial_reward / (2 ** halvings)
    def adjust_mining_fees(self): return 0.00000010 # 10 balíns fixos.


b = Blockchain()
