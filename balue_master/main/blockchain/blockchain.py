from blockchain.block import *
from wallet.wallet import *
import os


class Blockchain:

    def __init__(self):
        self.chain_path = 'balue/blockchain.json'
        self.chain = []
        os.makedirs(os.path.dirname(self.chain_path), exist_ok=True)
        self.load_chain()
        self.pending_block = []
        self.create_genesis()

    def load_chain(self):
        if os.path.exists(self.chain_path):
            with open(self.chain_path, 'r', encoding='utf-8') as chain_file:
                self.chain = json.load(chain_file)
        else: self.save_chain()

    def save_chain(self):
        with open(self.chain_path, 'w', encoding='utf-8') as chain_file:
            json.dump(self.chain, chain_file, ensure_ascii=False, indent=4)

    def create_genesis(self):
        if len(self.chain) == 0:
            self.new_pending_block()

    def new_pending_block(self) -> bool:
        if len(self.pending_block) == 0:
            new_block = Block(self.index(), self.adjust_difficulty(self.index()),
                              self.adjust_reward(self.index()), self.previous_hash())
            self.pending_block = []
            self.pending_block.append(new_block)
            return True
        return False

    def add_transaction_to_pending(self, transaction: Transaction) -> None:
        if len(self.pending_block) > 0:
            self.pending_block[0].add_transaction(transaction)
        else:
            self.new_pending_block()
            self.pending_block[0].add_transaction(transaction)

    def mine_pending(self, miner_address: str, miner_public_key: str) -> None:
        if len(self.pending_block) > 0:
            self.pending_block[0].mine_block(miner_address, miner_public_key)

    def add_block_to_chain(self) -> None:
        if len(self.pending_block) > 0:
            p = self.pending_block[0]
            if p.miner_address and p.hash != 0 and p.miner_signature:
                self.chain.append(p.block_to_dict())
                self.save_chain()
                self.pending_block = []

    def sign_pending(self, signature: str) -> None:
        if len(self.pending_block) > 0:
            self.pending_block[0].sign_block(signature)

    def index(self) -> int: return len(self.chain)

    def previous_hash(self) -> str:
        if len(self.chain) == 0:
            return "0"
        return self.chain[-1]["hash"]

    def calculate_total_fees(self, blk: dict) -> float:
        total_fees = 0
        for tr in blk["transactions"]:
            total_fees += tr["fees"]
        return total_fees

    def compute_merkle_root(self, blk) -> str:
        return hashlib.sha256(
            json.dumps(blk["transactions"], sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def calculate_block_hash_after_mining(self, blk: dict) -> str:
        block_dict = {
            "index": blk["index"],
            "timestamp": blk["timestamp"],
            "mine_timestamp": blk["mine_timestamp"],
            "id": blk["id"],
            "difficulty": blk["difficulty"],
            "nonce": blk["nonce"],
            "reward": blk["reward"],
            "total_fees": blk["total_fees"],
            "transactions": blk["transactions"],
            "merkle_root": blk["merkle_root"],
            "miner_address": blk["miner_address"],
            "miner_public_key": blk["miner_public_key"],
            "previous_hash": blk["previous_hash"]
        }
        return hashlib.sha256(
            json.dumps(block_dict, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def calculate_transaction_hash_after_mining(self, trx: dict) -> str:
        trx_dict = {
            "sender": trx["sender"],
            "receiver": trx["receiver"],
            "value": trx["value"],
            "fees": trx["fees"],
            "timestamp": trx["timestamp"],
            "validation_timestamp": trx["validation_timestamp"],
            "id": trx["id"],
            "metadata": trx["metadata"],
            "public_key": trx["public_key"],
            "nonce": trx["nonce"],
            "difficulty": trx["difficulty"]
        }
        return hashlib.sha256(
            json.dumps(trx_dict, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def validate_pending_block(self, blk: dict) -> bool:
        if blk["index"] == 0:
            if blk["previous_hash"] != "0":
                return False
            if blk["reward"] != self.adjust_reward(blk["index"]):
                return False
            if blk["difficulty"] != self.adjust_difficulty(blk["index"]):
                return False
            if blk["total_fees"] != self.calculate_total_fees(blk):
                return False
            if blk["timestamp"] < 1749209387667023055:
                return False
            for tr in blk["transactions"]:
                if tr["fees"] != self.calculate_fees(tr["value"]):
                    return False
                if tr["hash"] != self.calculate_transaction_hash_after_mining(tr):
                    return False
                if tr["difficulty"] != self.transactions_difficulty():
                    return False
                if not tr["hash"].startswith("0" * self.transactions_difficulty()):
                    return False
                if not verificar_assinatura(json_para_chave_publica(tr["public_key"]),
                                            tr["sender"], bytes.fromhex(tr["hash"]),
                                            json_para_assinatura(tr["signature"])):
                    return False
                if tr["metadata"] is None:
                    return False
                if len(tr["metadata"]) > 80:
                    return False
                if tr["value"] == 0:
                    return False
                sender_balance = self.get_balance(tr["sender"])
                if sender_balance < (tr["value"] + tr["fees"]):
                    return False
        else:
            if blk["index"] != (self.chain[-1]["index"] + 1):
                return False
            if blk["previous_hash"] != self.previous_hash():
                return False
            if blk["reward"] != self.adjust_reward(blk["index"]):
                return False
            if blk["difficulty"] != self.adjust_difficulty(blk["index"]):
                return False
            if blk["total_fees"] != self.calculate_total_fees(blk):
                return False
            if blk["timestamp"] < self.chain[-1]["timestamp"]:
                return False
            if blk["mine_timestamp"]:
                return False
            for tr in blk["transactions"]:
                if tr["fees"] != self.calculate_fees(tr["value"]):
                    return False
                if tr["hash"] != self.calculate_transaction_hash_after_mining(tr):
                    return False
                if tr["value"] == 0:
                    return False
                sender_balance = self.get_balance(tr["sender"])
                if sender_balance < (tr["value"] + tr["fees"]):
                    return False
                if tr["difficulty"] != self.transactions_difficulty():
                    return False
                if not tr["hash"].startswith("0" * self.transactions_difficulty()):
                    return False
                if not verificar_assinatura(json_para_chave_publica(tr["public_key"]),
                                            tr["sender"], bytes.fromhex(tr["hash"]),
                                            json_para_assinatura(tr["signature"])):
                    return False
                if tr["metadata"] is None:
                    return False
                if len(tr["metadata"]) > 80:
                    return False
                sender_balance = self.get_balance(tr["sender"])
                if sender_balance < (tr["value"] + tr["fees"]):
                    return False
        return True

    def validate_block(self, current_block, previous_block=None) -> bool:
        if not previous_block:
            if current_block["index"] != 0:
                return False
            if current_block["previous_hash"] != "0":
                return False
            if current_block["merkle_root"] != self.compute_merkle_root(current_block):
                return False
            if current_block["hash"] != self.calculate_block_hash_after_mining(current_block):
                return False
            if current_block["reward"] != self.adjust_reward(current_block["index"]):
                return False
            if current_block["difficulty"] != self.adjust_difficulty(current_block["index"]):
                return False
            if not current_block["hash"].startswith("0" * self.adjust_difficulty(current_block["index"])):
                return False
            if current_block["total_fees"] != self.calculate_total_fees(current_block):
                return False
            if current_block["timestamp"] < 1749209387667023055:
                return False
            if current_block["mine_timestamp"]:
                if current_block["mine_timestamp"] < current_block["timestamp"]:
                    return False
            if not verificar_assinatura(json_para_chave_publica(current_block["miner_public_key"]),
                                        current_block["miner_address"],
                                        bytes.fromhex(current_block["hash"]),
                                        json_para_assinatura(current_block["miner_signature"])):
                return False
            for tr in current_block["transactions"]:
                if tr["fees"] != self.calculate_fees(tr["value"]):
                    return False
                if tr["hash"] != self.calculate_transaction_hash_after_mining(tr):
                    return False
                if tr["value"] == 0:
                    return False
                sender_balance = self.get_balance(tr["sender"])
                if sender_balance < (tr["value"] + tr["fees"]):
                    return False
                if tr["difficulty"] != self.transactions_difficulty():
                    return False
                if not tr["hash"].startswith("0" * self.transactions_difficulty()):
                    return False
                if not verificar_assinatura(json_para_chave_publica(tr["public_key"]),
                                        tr["sender"], bytes.fromhex(tr["hash"]),
                                        json_para_assinatura(tr["signature"])):
                    return False
                if tr["metadata"] is None:
                    return False
                if len(tr["metadata"]) > 80:
                    return False
        else:
            if current_block["index"] != (previous_block["index"] + 1):
                return False
            if current_block["previous_hash"] != previous_block["hash"]:
                return False
            if current_block["merkle_root"] != self.compute_merkle_root(current_block):
                return False
            if current_block["hash"] != self.calculate_block_hash_after_mining(current_block):
                return False
            if current_block["reward"] != self.adjust_reward(current_block["index"]):
                return False
            if current_block["difficulty"] != self.adjust_difficulty(current_block["index"]):
                return False
            if not current_block["hash"].startswith("0" * self.adjust_difficulty(current_block["index"])):
                return False
            if current_block["total_fees"] != self.calculate_total_fees(current_block):
                return False
            if current_block["timestamp"] < previous_block["timestamp"]:
                return False
            if current_block["mine_timestamp"]:
                if current_block["mine_timestamp"] < current_block["timestamp"]:
                    return False
            if not verificar_assinatura(json_para_chave_publica(current_block["miner_public_key"]),
                                        current_block["miner_address"],
                                        bytes.fromhex(current_block["hash"]),
                                        json_para_assinatura(current_block["miner_signature"])):
                return False
            for tr in current_block["transactions"]:
                if tr["fees"] != self.calculate_fees(tr["value"]):
                    return False
                if tr["hash"] != self.calculate_transaction_hash_after_mining(tr):
                    return False
                if tr["value"] == 0:
                    return False
                sender_balance = self.get_balance(tr["sender"])
                if sender_balance < (tr["value"] + tr["fees"]):
                    return False
                if tr["difficulty"] != self.transactions_difficulty():
                    return False
                if not tr["hash"].startswith("0" * self.transactions_difficulty()):
                    return False
                if not verificar_assinatura(json_para_chave_publica(tr["public_key"]),
                                        tr["sender"], bytes.fromhex(tr["hash"]),
                                        json_para_assinatura(tr["signature"])):
                    return False
                if tr["metadata"] is None:
                    return False
                if len(tr["metadata"]) > 80:
                    return False
        return True

    def chain_is_valid(self) -> bool:
        for i in range(0, len(self.chain)):
            if i == 0:
                current_block = self.chain[i]
                if not self.validate_block(current_block):
                    return False
            else:
                current_block = self.chain[i]
                previous_block = self.chain[i -1]
                if not self.validate_block(current_block, previous_block):
                    return False
        return True

    def get_balance(self, address: str) -> float:
        balance = 0
        for blk in self.pending_block:
            for tr in blk.transactions:
                if tr["sender"] == address:
                    balance -= (tr["value"] + tr["fees"])
        for blk in self.chain:
            if blk["miner_address"] == address:
                balance += (blk["reward"] + blk["total_fees"])
            for tr in blk["transactions"]:
                if tr["sender"] == address:
                    balance -= (tr["value"] + tr["fees"])
                if tr["receiver"] == address:
                    balance += tr["value"]
        return balance

    def adjust_difficulty(self, index: int) -> int:
        target_time = 600_000_000_000
        initial_difficulty = 6
        interval_adjust = 2016
        adjust = 2

        if index < interval_adjust + 1:
            return initial_difficulty

        total_time = 0
        for i in range(index - interval_adjust, index):
            prev_timestamp = self.chain[i - 1]["mine_timestamp"]
            curr_timestamp = self.chain[i]["mine_timestamp"]
            time_diff = curr_timestamp - prev_timestamp
            total_time += time_diff

        average_time = total_time / interval_adjust
        previous_difficulty = self.chain[index - 1]["difficulty"]

        if average_time > target_time:
            return max(initial_difficulty, previous_difficulty - adjust)
        else:
            return previous_difficulty + adjust

    def adjust_reward(self, index: int) -> float:
        max_suply = 18_000_000
        interval_halving = 250_000
        initial_reward = 12.5

        total_coins = 0
        rewards = [blk["reward"] for blk in self.chain]
        for r in rewards: total_coins += r
        if total_coins >= max_suply: return 0

        halving_count = index // interval_halving
        reward = initial_reward / (2 ** halving_count)
        reward = max(reward, 0.00000001)
        return round(reward, 8)

    def transactions_difficulty(self) -> int: return 4

    def calculate_fees(self, value: float) -> float:
        percent_fees = 0.5
        return round(value * (percent_fees / 100), 8)


chain_state = Blockchain()
