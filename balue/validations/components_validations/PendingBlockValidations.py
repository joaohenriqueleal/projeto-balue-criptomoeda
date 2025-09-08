from validations.components_validations.BlockValidations import *


class PendingBlockValidations:

    def __init__(self) -> None:
        self.block_validations: 'BlockValidations' = BlockValidations()
        self.hasher: 'Hasher' = Hasher()

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

    @staticmethod
    def validate_total_fees(block: dict) -> int:
        total_fees: int = 0
        for tr in block["transactions"]:
            total_fees += tr["fee"]
        return total_fees

    @staticmethod
    def tr_hash_unicity(block: dict) -> bool:
        hashes_list: list[str] = []
        for tr in block["transactions"]:
            if tr["hash"] in hashes_list:
                return False
            hashes_list.append(tr["hash"])
        return True

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

    def validate_pending_block(self, current_block: dict, previous_block: dict = None) -> bool:
            adjusts_path = blockchain.adjusts
            try:
                if not previous_block:
                    if current_block["index"] != 0:
                        return False
                    if current_block["previous_hash"] != "0" * 64:
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
                if len(current_block["id"]) >= MAX_METADATA_LENGTH:
                    return False
                if len(current_block["version"]) > MAX_METADATA_LENGTH:
                    return False
                if not self.has_exact_fields(current_block):
                    return False
                if len(current_block["transactions"]) > MAX_TRANSACTIONS_PER_BLOCK:
                    return False
                if current_block["timestamp"] > time.time_ns() or current_block["validation_timestamp"] > time.time_ns():
                    return False
                if current_block["total_transactions"] != len(current_block["transactions"]):
                    return False
                if current_block["total_fees"] != self.validate_total_fees(current_block):
                    return False
                if not self.tr_hash_unicity(current_block):
                    return False
                if current_block["merkle_root"] != self.validate_merkle_root(current_block):
                    return False
                if current_block["reward"] != adjusts_path.adjust_reward(current_block["index"]):
                    return False
                if current_block["difficulty"] != adjusts_path.adjust_difficulty(current_block["index"]):
                    return False
                if len(current_block["metadata"]) > MAX_METADATA_LENGTH:
                    return False
                for tr in current_block["transactions"]:
                    if not self.block_validations.transaction_validations.validate(tr, current_block):
                        return False
                return True
            except:
                return False
