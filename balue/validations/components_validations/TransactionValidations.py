from wallet.Wallet import *


class TransactionValidations:

    def __init__(self) -> None:
        self.wallet_methods: 'WalletMethods' = WalletMethods()
        self.hasher: 'Hasher' = Hasher()

    def compute_transaction_hash(self, tr: dict) -> str:
        tr_dict: dict = {
            "sender": tr["sender"],
            "receiver": tr["receiver"],
            "value": tr["value"],
            "fee": tr["fee"],
            "id": tr["id"],
            "version": tr["version"],
            "timestamp": tr["timestamp"],
            "validation_timestamp": tr["validation_timestamp"],
            "public_key": tr["public_key"],
            "difficulty": tr["difficulty"],
            "nonce": tr["nonce"],
            "metadata": tr["metadata"]
        }
        return self.hasher.hasher(
            tr_dict
        )

    @staticmethod
    def get_balance(address: str, ignore_tx: dict) -> float:
        balance: int = 0
        for i in range(0, len(blockchain.adjusts.storage.chain)):
            block: dict = blockchain.adjusts.storage.load_block(i)
            if block["miner_address"] == address:
                balance += (block["reward"] + block["total_fees"])
            for tr in block["transactions"]:
                if tr["sender"] == address:
                    balance -= (tr["value"] + tr["fee"])
                if tr["receiver"] == address:
                    balance += tr["value"]
        for blk in blockchain.pending_blocks:
            for tr in blk.transactions:
                if tr != ignore_tx:
                    if tr["sender"] == address:
                        balance -= (tr["value"] + tr["fee"])
        return balance / DIVISIBLE

    @staticmethod
    def has_exact_fields(tr: dict) -> bool:
        required_fields = {
            'sender', 'receiver', 'value', 'fee', 'id', 'version',
            'timestamp', 'validation_timestamp', 'public_key',
            'signature', 'nonce', 'difficulty', 'metadata', 'hash'
        }
        tr_fields = set(tr.keys())
        return tr_fields == required_fields

    def validate(self, tr: dict, block: dict) -> bool:
        try:
            if len(tr["id"]) >= MAX_METADATA_LENGTH:
                return False
            if len(tr["version"]) > MAX_METADATA_LENGTH:
                return False
            if tr["value"] < MIN_REWARD or tr["fee"] < MIN_REWARD:
                return False
            if tr["value"] > MAX_SUPLY or tr["fee"] > MAX_SUPLY:
                return False
            if (tr["value"] + tr["fee"]) / DIVISIBLE > self.get_balance(tr["sender"], tr):
                print(self.get_balance(tr["sender"], tr))
                return False
            if tr["value"] < 0 or tr["fee"] < 0:
                return False
            if tr["timestamp"] < block["timestamp"]:
                return False
            if tr["timestamp"] > time.time_ns() or tr["validation_timestamp"] > time.time_ns():
                return False
            if tr["validation_timestamp"] < tr["timestamp"]:
                return False
            if tr["difficulty"] != blockchain.adjusts.adjust_transactions_difficulty(block["index"]):
                return False
            if len(tr["metadata"]) > MAX_METADATA_LENGTH:
                return False
            if not tr["hash"].startswith("0" * blockchain.adjusts.adjust_transactions_difficulty(block["index"])):
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
