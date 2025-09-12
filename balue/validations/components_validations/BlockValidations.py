from validations.components_validations.TransactionValidations import *


class BlockValidations:

    def __init__(self) -> None:
        self.transaction_validations: 'TransactionValidations' = TransactionValidations()
        self.wallet_methods: 'WalletMethods' = WalletMethods()
        self.hasher: 'Hasher' = Hasher()

    @staticmethod
    def validate_total_fees(block: dict) -> int:
        total_fees: int = 0
        for tr in block["transactions"]:
            total_fees += tr["fee"]
        return total_fees

    def validate_merkle_root(self, block: dict) -> str:
        if not block["transactions"]:
            return "0" * 64

        hashes_list = [tx["hash"] for tx in block["transactions"]]

        while len(hashes_list) > 1:
            if len(hashes_list) % 2 != 0:
                hashes_list.append(hashes_list[-1])
            new_hashes = []
            for i in range(0, len(hashes_list), 2):
                combined = hashes_list[i] + hashes_list[i + 1]
                new_hashes.append(self.hasher.hasher(combined))
            hashes_list = new_hashes

        return hashes_list[0]

    @staticmethod
    def tr_hash_unicity(block: dict) -> bool:
        hashes_list: list[str] = []
        for tr in block["transactions"]:
            if tr["hash"] in hashes_list:
                return False
            hashes_list.append(tr["hash"])
        return True

    @staticmethod
    def has_exact_fields(block: dict) -> bool:
        required_fields = {
            "index", "total_transactions", "total_fees",
            "transactions", "merkle_root", "reward",
            "miner_address", "previous_hash", "id", "signature",
            "timestamp", "validation_timestamp", "public_key",
            "difficulty", "nonce", "metadata", "hash", "version"
        }
        block_fields = set(block.keys())
        return block_fields == required_fields

    def compute_block_hash(self, block: dict) -> str:
        block_dict: dict = {
            "index": block["index"],
            "total_transactions": block["total_transactions"],
            "total_fees": block["total_fees"],
            "transactions": block["transactions"],
            "merkle_root": block["merkle_root"],
            "reward": block["reward"],
            "miner_address": block["miner_address"],
            "previous_hash": block["previous_hash"],
            "id": block["id"],
            "version": block["version"],
            "timestamp": block["timestamp"],
            "validation_timestamp": block["validation_timestamp"],
            "public_key": block["public_key"],
            "difficulty": block["difficulty"],
            "nonce": block["nonce"],
            "metadata": block["metadata"]
        }
        return self.hasher.hasher(
            block_dict
        )

    def validate(self, block: dict, previous_block: dict = None) -> bool:
        adjusts_path = blockchain.adjusts
        try:
            if not previous_block:
                if block["index"] != 0:
                    return False
                if block["previous_hash"] != "0" * 64:
                    return False
                if block["timestamp"] < INITIAL_TIMESTAMP:
                    return False
            else:
                if block["index"] != (previous_block["index"] + 1):
                    return False
                if block["previous_hash"] != previous_block["hash"]:
                    return False
                if block["timestamp"] < previous_block["timestamp"]:
                    return False
            if len(block["miner_address"]) > MAX_METADATA_LENGTH:
                return False
            if len(block["id"]) >= MAX_METADATA_LENGTH:
                return False
            if len(block["version"]) > MAX_METADATA_LENGTH:
                return False
            if not self.has_exact_fields(block):
                return False
            if len(block["transactions"]) > MAX_TRANSACTIONS_PER_BLOCK:
                return False
            if block["timestamp"] > time.time_ns() or block["validation_timestamp"] > time.time_ns():
                return False
            if block["validation_timestamp"] < block["timestamp"]:
                return False
            if block["total_transactions"] != len(block["transactions"]):
                return False
            if block["total_fees"] != self.validate_total_fees(block):
                return False
            if not self.tr_hash_unicity(block):
                return False
            if block["merkle_root"] != self.validate_merkle_root(block):
                return False
            if block["reward"] != adjusts_path.adjust_reward(block["index"]):
                return False
            if block["difficulty"] != adjusts_path.adjust_difficulty(block["index"]):
                return False
            if len(block["metadata"]) > MAX_METADATA_LENGTH:
                return False
            if not block["hash"].startswith("0" * adjusts_path.adjust_difficulty(block["index"])):
                return False
            if block["hash"] != self.compute_block_hash(block):
                return False
            if not self.wallet_methods.verify_signature(
                self.wallet_methods.json_to_public_key(block["public_key"]),
                block["miner_address"],
                bytes.fromhex(block["hash"]),
                self.wallet_methods.json_to_signature(block["signature"])
            ):
                return False
            return True
        except:
            return False
