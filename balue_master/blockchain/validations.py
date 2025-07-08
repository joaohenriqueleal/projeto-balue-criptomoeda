from blockchain.adjusts import *
from wallet.wallet import *


class Validations:

    def __init__(self) -> None:
        self.adjusts: Adjusts = Adjusts()

    @staticmethod
    def compute_block_hash(blk: dict) -> str:
        block_dict: dict = {
            "index": blk["index"],
            "total_transactions": blk["total_transactions"],
            "miner_address": blk["miner_address"],
            "metadata": blk["metadata"],
            "reward": blk["reward"],
            "merkle_root": blk["merkle_root"],
            "transactions": blk["transactions"],
            "total_fees": blk["total_fees"],
            "previous_hash": blk["previous_hash"],
            "validation_timestamp": blk["validation_timestamp"],
            "public_key": blk["public_key"],
            "difficulty": blk["difficulty"],
            "timestamp": blk["timestamp"],
            "id": blk["id"],
            "nonce": blk["nonce"]
        }
        return hashlib.sha256(json.dumps(
            block_dict, sort_keys=True, ensure_ascii=False
        ).encode()).hexdigest()

    @staticmethod
    def compute_transaction_hash(trx: dict) -> str:
        trx_dict: dict = {
            "sender": trx["sender"],
            "receiver": trx["receiver"],
            "value": trx["value"],
            "fee": trx["fee"],
            "validation_timestamp": trx["validation_timestamp"],
            "public_key": trx["public_key"],
            "difficulty": trx["difficulty"],
            "timestamp": trx["timestamp"],
            "id": trx["id"],
            "metadata": trx["metadata"],
            "nonce": trx["nonce"]
        }
        return hashlib.sha256(json.dumps(
            trx_dict, sort_keys=True, ensure_ascii=False
        ).encode()).hexdigest()

    @staticmethod
    def compute_merkle_root(blk: dict) -> str:
        return hashlib.sha256(json.dumps(
            blk["transactions"]
        ).encode()).hexdigest()

    @staticmethod
    def validate_total_fees(blk: dict) -> float:
        total_fees: float = 0
        for tr in blk["transactions"]:
            total_fees += tr["fee"]
        return total_fees

    def validate_pending_block(self, current_block: dict) -> bool:
        try:
            if current_block["index"] == 0:
                if current_block["previous_hash"] != "0":
                    return False
                if current_block["timestamp"] < INITIAL_TIMESTAMP:
                    return False
            else:
                previous_block = self.adjusts.storage.load_block(current_block["index"] - 1)
                if current_block["index"] != (previous_block["index"] + 1):
                    return False
                if current_block["previous_hash"] != previous_block["hash"]:
                    return False
                if current_block["timestamp"] < previous_block["timestamp"]:
                    return False
            if current_block["total_transactions"] != len(current_block["transactions"]):
                return False
            if current_block["metadata"] is None:
                return False
            if len(current_block["metadata"]) > 80:
                return False
            if current_block["reward"] != self.adjusts.adjust_reward(current_block["index"]):
                return False
            if current_block["merkle_root"] != self.compute_merkle_root(current_block):
                return False
            if current_block["total_fees"] != self.validate_total_fees(current_block):
                return False
            if current_block["validation_timestamp"]:
                if current_block["validation_timestamp"] < current_block["timestamp"]:
                    return False
            if current_block["timestamp"] > time.time_ns() or current_block["validation_timestamp"] > time.time_ns():
                return False
            if current_block["difficulty"] != self.adjusts.adjust_difficulty(current_block["index"]):
                return False
            if current_block["total_transactions"] > MAX_TRANSACTIONS_PER_BLOCK:
                return False
            if current_block["total_transactions"] < self.adjusts.min_transactions(current_block["index"]):
                return False
            if current_block["hash"] != "0":
                return False
            for tr in current_block["transactions"]:
                sign_verifications: 'WalletMethods' = WalletMethods()
                if not sign_verifications.verify_signature(
                        sign_verifications.json_to_public_key(tr["public_key"]),
                        tr["sender"], bytes.fromhex(tr["hash"]),
                        sign_verifications.json_to_signature(tr["signature"])):
                    return False
                sender_balance: float = self.get_balance(tr["sender"])
                if (tr["value"] + tr["fee"]) > sender_balance:
                    return False
                if tr["timestamp"] < current_block["timestamp"]:
                    return False
                if tr["validation_timestamp"] < tr["timestamp"]:
                    return False
                if tr["fee"] < 0:
                    return False
                if tr["timestamp"] > time.time_ns() or tr["validation_timestamp"] > time.time_ns():
                    return False
                if tr["difficulty"] != self.adjusts.adjust_transactions_difficulty(current_block["index"]):
                    return False
                if tr["metadata"] is None:
                    return False
                if len(tr["metadata"]) > 80:
                    return False
                if tr["hash"] != self.compute_transaction_hash(tr):
                    return False
                if not tr["hash"].startswith("0" * self.adjusts.adjust_difficulty(current_block["index"])):
                    return False
            return True
        except Exception as e:
            print(e)
            return False

    def validate_block(self, current_block: dict, previous_block: dict = None) -> bool:
        try:
            sign_verifications: 'WalletMethods' = WalletMethods()
            if not previous_block:
                if current_block["index"] != 0:
                    return False
                if current_block["previous_hash"] != "0":
                    return False
                if current_block["timestamp"] < INITIAL_TIMESTAMP:
                    return False
            else:
                if current_block["index"] != (previous_block["index"] + 1):
                    return False
                if current_block["previous_hash"] != previous_block["hash"]:
                    return False
                if current_block["timestamp"] < previous_block["timestamp"]:
                    return False
            if not sign_verifications.verify_signature(sign_verifications.json_to_public_key(current_block["public_key"]),
                                                       current_block["miner_address"], bytes.fromhex(current_block["hash"]),
                                                       sign_verifications.json_to_signature(current_block["signature"])):
                return False
            if current_block["total_transactions"] != len(current_block["transactions"]):
                return False
            if current_block["metadata"] is None:
                return False
            if len(current_block["metadata"]) > 80:
                return False
            if current_block["reward"] != self.adjusts.adjust_reward(current_block["index"]):
                return False
            if current_block["merkle_root"] != self.compute_merkle_root(current_block):
                return False
            if current_block["total_fees"] != self.validate_total_fees(current_block):
                return False
            if current_block["validation_timestamp"] < current_block["timestamp"]:
                return False
            if current_block["timestamp"] > time.time_ns() or current_block["validation_timestamp"] > time.time_ns():
                return False
            if current_block["difficulty"] != self.adjusts.adjust_difficulty(current_block["index"]):
                return False
            if current_block["total_transactions"] > MAX_TRANSACTIONS_PER_BLOCK:
                return False
            if current_block["total_transactions"] < self.adjusts.min_transactions(current_block["index"]):
                return False
            if current_block["hash"] != self.compute_block_hash(current_block):
                return False
            if not current_block["hash"].startswith("0" * self.adjusts.adjust_difficulty(current_block["index"])):
                return False
            for tr in current_block["transactions"]:
                if not sign_verifications.verify_signature(
                        sign_verifications.json_to_public_key(tr["public_key"]),
                        tr["sender"], bytes.fromhex(tr["hash"]),
                        sign_verifications.json_to_signature(tr["signature"])):
                    return False
                sender_balance: float = self.get_balance(tr["sender"])
                if (tr["value"] + tr["fee"]) > sender_balance:
                    return False
                if tr["fee"] < 0:
                    return False
                if tr["timestamp"] < current_block["timestamp"]:
                    return False
                if tr["validation_timestamp"] < tr["timestamp"]:
                    return False
                if tr["timestamp"] > time.time_ns() or tr["validation_timestamp"] > time.time_ns():
                    return False
                if tr["difficulty"] != self.adjusts.adjust_transactions_difficulty(current_block["index"]):
                    return False
                if tr["metadata"] is None:
                    return False
                if len(tr["metadata"]) > 80:
                    return False
                if tr["hash"] != self.compute_transaction_hash(tr):
                    return False
                if not tr["hash"].startswith("0" * self.adjusts.adjust_difficulty(current_block["index"])):
                    return False
            return True
        except Exception as e:
            print(e)
            return False

    def get_balance(self, address: str) -> float:
        balance: float = 0
        for i in range(0, len(self.adjusts.storage.chain)):
            blk: dict = self.adjusts.storage.load_block(i)
            for tr in blk["transactions"]:
                if tr["sender"] == address:
                    balance -= (tr["value"] + tr["fee"])
                if tr["receiver"] == address:
                    balance += tr["value"]
            if blk["miner_address"] == address:
                balance += (blk["reward"] + blk["total_fees"])
        return balance

    def chain_is_valid(self) -> bool:
        for i in range(0, len(self.adjusts.storage.chain)):
            if i == 0:
                current_block: dict = self.adjusts.storage.load_block(i)
                if not self.validate_block(current_block):
                    return False
            else:
                current_block: dict = self.adjusts.storage.load_block(i)
                previous_block: dict = self.adjusts.storage.load_block(i - 1)
                if not self.validate_block(current_block, previous_block):
                    return False
        return True
