from blockchain.Adjusts import *
from wallet.Wallet import *


class TransactionValidations:

    def __init__(self) -> None:
        self.adjusts: 'Adjusts' = Adjusts()
        self.wallet_methods: 'WalletMethods' = WalletMethods()

    @staticmethod
    def compute_transaction_hash(tr: dict) -> str:
        tr_dict: dict = {
            "sender": tr["sender"],
            "receiver": tr["receiver"],
            "value": tr["value"],
            "fee": tr["fee"],
            "id": tr["id"],
            "timestamp": tr["timestamp"],
            "validation_timestamp": tr["validation_timestamp"],
            "public_key": tr["public_key"],
            "difficulty": tr["difficulty"],
            "nonce": tr["nonce"],
            "metadata": tr["metadata"]
        }
        return hashlib.sha256(json.dumps(
            tr_dict, sort_keys=True, ensure_ascii=False
        ).encode()).hexdigest()

    def get_balance(self, address: str) -> float:
        balance: int = 0
        for i in range(0, len(self.adjusts.storage.chain)):
            block: dict = self.adjusts.storage.load_block(i)
            if block["miner_address"] == address:
                balance += (block["reward"] + block["total_fees"])
            for tr in block["transactions"]:
                if tr["sender"] == address:
                    balance -= (tr["value"] + tr["fee"])
                if tr["receiver"] == address:
                    balance += tr["value"]
        return balance / DIVISIBLE

    def validate(self, tr: dict, block: dict) -> bool:
        try:
            if tr["value"] < MIN_REWARD or tr["fee"] < MIN_REWARD:
                return False
            if tr["value"] > MAX_SUPLY or tr["fee"] > MAX_SUPLY:
                return False
            if (tr["value"] + tr["fee"]) / DIVISIBLE > self.get_balance(tr["sender"]):
                return False
            if tr["value"] < 0 or tr["fee"] < 0:
                return False
            if tr["timestamp"] < block["timestamp"]:
                return False
            if tr["timestamp"] > time.time_ns() or tr["validation_timestamp"] > time.time_ns():
                return False
            if tr["validation_timestamp"] < tr["timestamp"]:
                return False
            if tr["difficulty"] != self.adjusts.adjust_transactions_difficulty(block["index"]):
                return False
            if len(tr["metadata"]) > MAX_METADATA_LENGTH:
                return False
            if not tr["hash"].startswith("0" * self.adjusts.adjust_transactions_difficulty(block["index"])):
                return False
            if tr["hash"] != self.compute_transaction_hash(tr):
                return False
            if not self.wallet_methods.verify_signature(
                self.wallet_methods.json_to_public_key(tr["public_key"]),
                tr["sender"],
                bytes.fromhex(tr["hash"]),
                self.wallet_methods.json_to_signature(tr["signature"])
            ):
                return False
        except:
            return False
        return True
