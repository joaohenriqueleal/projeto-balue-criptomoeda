from blockchain.block import *
from wallet.wallet import *
import threading
import os


class Blockchain:

    def __init__(self):
        self.chain_lock = threading.Lock()

        # Constantes de config do protocolo.
        self.target_time = 600_000_000_000
        self.percent_fees = 0.5
        self.max_suply = 18_000_000
        self.interval_halving = 360_000
        self.initial_reward = 25
        self.initial_difficulty = 6
        self.interval_adjust = 2016
        self.adjust = 2
        self.max_transactions_per_block = 10_000

        self.chain_path = 'balue/chain/blockchain.json'
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

    def add_block(self, blk: dict) -> None:
        with open(f'balue/chain/{blk["index"]}.json', 'w', encoding='utf-8') as block_file:
            json.dump(blk, block_file, indent=4, ensure_ascii=False)
        new_path = {"path": f"balue/chain/{blk['index']}.json"}
        for path in self.chain:
            if path == new_path: return
        self.chain.append(new_path)
        self.save_chain()

    def load_block(self, index: int):
        try:
            with open(f'{self.chain[index]["path"]}', 'r', encoding='utf-8') as block:
                return json.load(block)
        except: pass

    def add_block_to_chain(self) -> None:
        if len(self.pending_block) > 0:
            p = self.pending_block[0]
            if p.miner_address and p.hash != 0 and p.miner_signature:
                self.add_block(p.block_to_dict())
                self.pending_block = []

    def sign_pending(self, signature: str) -> None:
        if len(self.pending_block) > 0:
            self.pending_block[0].sign_block(signature)

    def index(self) -> int: return len(self.chain)

    def previous_hash(self) -> str:
        if len(self.chain) == 0:
            return "0"
        return self.load_block(len(self.chain) - 1)["hash"]

    def calculate_total_fees(self, blk: dict) -> float:
        total_fees = 0
        for tr in blk["transactions"]:
            total_fees += tr["fees"]
        return total_fees

    def compute_merkle_root(self, blk) -> str:
        return hashlib.sha256(
            json.dumps(blk["transactions"], sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def validate_tr_hash_unicity(self, transactions: list[dict]) -> bool:
        saw_hashes: list[str] = []
        for tr in transactions:
            if tr["hash"] in saw_hashes:
                return False
            saw_hashes.append(tr["hash"])
        return True

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
        try:
            if blk["index"] == 0:
                if blk["previous_hash"] != "0":
                    return False
                if blk["reward"] != self.adjust_reward(blk["index"]):
                    return False
                if blk["difficulty"] != self.adjust_difficulty(blk["index"]):
                    return False
                if blk["total_fees"] != self.calculate_total_fees(blk):
                    return False
                if blk["timestamp"] > time.time_ns():
                    return False
                if blk["timestamp"] < 1749856600218119179:
                    return False
                if blk["mine_timestamp"]:
                    return False
                if len(blk["transactions"]) > self.max_transactions_per_block:
                    return False
                if not self.validate_tr_hash_unicity(blk["transactions"]):
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
                    if tr["timestamp"] < blk["timestamp"]:
                        return False
                    if tr["validation_timestamp"] < tr["timestamp"]:
                        return False
                    if tr["validation_timestamp"] > time.time_ns() or tr["timestamp"] > time.time_ns():
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
                if blk["index"] != (self.load_block(len(chain_state.chain) - 1)["index"] + 1):
                    return False
                if blk["previous_hash"] != self.previous_hash():
                    return False
                if blk["reward"] != self.adjust_reward(blk["index"]):
                    return False
                if blk["difficulty"] != self.adjust_difficulty(blk["index"]):
                    return False
                if blk["total_fees"] != self.calculate_total_fees(blk):
                    return False
                if blk["timestamp"] < self.load_block(len(chain_state.chain) - 1)["timestamp"]:
                    return False
                if blk["timestamp"] > time.time_ns():
                    return False
                if blk["mine_timestamp"]:
                    return False
                if len(blk["transactions"]) > self.max_transactions_per_block:
                    return False
                if not self.validate_tr_hash_unicity(blk["transactions"]):
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
                    if tr["timestamp"] < blk["timestamp"]:
                        return False
                    if tr["validation_timestamp"] < tr["timestamp"]:
                        return False
                    if tr["validation_timestamp"] > time.time_ns() or tr["timestamp"] > time.time_ns():
                        return False
                    if tr["metadata"] is None:
                        return False
                    if len(tr["metadata"]) > 80:
                        return False
                    sender_balance = self.get_balance(tr["sender"])
                    if sender_balance < (tr["value"] + tr["fees"]):
                        return False
            return True
        except: return False

    def validate_block(self, current_block, previous_block=None) -> bool:
        try:
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
                if current_block["timestamp"] < 1749856600218119179:
                    return False
                if current_block["timestamp"] > time.time_ns():
                    return False
                if current_block["mine_timestamp"]:
                    if current_block["mine_timestamp"] < current_block["timestamp"]:
                        return False
                    if current_block["mine_timestamp"] > time.time_ns():
                        return False
                if not verificar_assinatura(json_para_chave_publica(current_block["miner_public_key"]),
                                            current_block["miner_address"],
                                            bytes.fromhex(current_block["hash"]),
                                            json_para_assinatura(current_block["miner_signature"])):
                    return False
                if len(current_block["transactions"]) < self.min_transactions_block(current_block["index"]):
                    return False
                if len(current_block["transactions"]) > self.max_transactions_per_block:
                    return False
                if not self.validate_tr_hash_unicity(current_block["transactions"]):
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
                    if tr["timestamp"] < current_block["timestamp"]:
                        return False
                    if tr["validation_timestamp"] < tr["timestamp"]:
                        return False
                    if tr["validation_timestamp"] > time.time_ns() or tr["timestamp"] > time.time_ns():
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
                if current_block["timestamp"] > time.time_ns():
                    return False
                if current_block["mine_timestamp"]:
                    if current_block["mine_timestamp"] < current_block["timestamp"]:
                        return False
                    if current_block["mine_timestamp"] > time.time_ns():
                        return False
                if len(current_block["transactions"]) < self.min_transactions_block(current_block["index"]):
                    return False
                if len(current_block["transactions"]) > self.max_transactions_per_block:
                    return False
                if not verificar_assinatura(json_para_chave_publica(current_block["miner_public_key"]),
                                            current_block["miner_address"],
                                            bytes.fromhex(current_block["hash"]),
                                            json_para_assinatura(current_block["miner_signature"])):
                    return False
                if not self.validate_tr_hash_unicity(current_block["transactions"]):
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
                    if tr["timestamp"] < current_block["timestamp"]:
                        return False
                    if tr["validation_timestamp"] < tr["timestamp"]:
                        return False
                    if tr["validation_timestamp"] > time.time_ns() or tr["timestamp"] > time.time_ns():
                        return False
                    if tr["metadata"] is None:
                        return False
                    if len(tr["metadata"]) > 80:
                        return False
            return True
        except: return False

    def chain_is_valid(self) -> bool:
        for i in range(0, len(self.chain)):
            blk = self.load_block(i)
            if i == 0:
                current_block = blk
                if not self.validate_block(current_block):
                    return False
            else:
                current_block = blk
                prev_blk = self.load_block(i - 1)
                previous_block = prev_blk
                if not self.validate_block(current_block, previous_block):
                    return False
        return True

    def get_balance(self, address: str) -> float:
        balance = 0
        for blk in self.pending_block:
            for tr in blk.transactions:
                if tr["sender"] == address:
                    balance -= (tr["value"] + tr["fees"])
        for i in range(0, len(self.chain)):
            blk = self.load_block(i)
            if blk["miner_address"] == address:
                balance += (blk["reward"] + blk["total_fees"])
            for tr in blk["transactions"]:
                if tr["sender"] == address:
                    balance -= (tr["value"] + tr["fees"])
                if tr["receiver"] == address:
                    balance += tr["value"]
        return balance

    def adjust_difficulty(self, index: int) -> int:
        if index < self.interval_adjust + 1:
            return self.initial_difficulty

        total_time = 0
        for i in range(index - self.interval_adjust, index):
            prev_timestamp = self.load_block(i - 1)["mine_timestamp"]
            curr_timestamp = self.load_block(i)["mine_timestamp"]
            time_diff = curr_timestamp - prev_timestamp
            total_time += time_diff

        average_time = total_time / self.interval_adjust
        previous_difficulty = self.load_block(index - 1)["difficulty"]

        if average_time > self.target_time:
            return max(self.initial_difficulty, previous_difficulty - self.adjust)
        else:
            return previous_difficulty + self.adjust

    def min_transactions_block(self, index: int) -> int:
        start = max(0, index - self.interval_adjust)
        total_blocos = index - start
        if total_blocos == 0:
            return 0

        soma = 0
        for i in range(start, index):
            soma += len(self.load_block(i)["transactions"])

        return soma // total_blocos

    def adjust_reward(self, index: int) -> float:
        total_coins = 0
        rewards = []
        for i in range(0, len(self.chain)):
            rewards.append(self.load_block(i)["reward"])
        for r in rewards: total_coins += r
        if total_coins >= self.max_suply: return 0

        halving_count = index // self.interval_halving
        reward = self.initial_reward / (2 ** halving_count)
        reward = max(reward, 0.00000001)
        return round(reward, 8)

    def transactions_difficulty(self) -> int: return 4

    def calculate_fees(self, value: float) -> float:
        return round(value * (self.percent_fees / 100), 8)


chain_state = Blockchain()
