from validations.components_validations.PendingBlockValidations import *


class Validations:

    def __init__(self) -> None:
        self.pending_validations: 'PendingBlockValidations' = PendingBlockValidations()

    def validate_block(self, current_block: dict, previous_block: dict = None) -> bool:
        if not previous_block:
            if not self.pending_validations.block_validations.validate(current_block):
                return False
        else:
            if not self.pending_validations.block_validations.validate(current_block, previous_block):
                return False
        for tr in current_block["transactions"]:
            if not self.pending_validations.block_validations.transaction_validations.validate(tr, current_block):
                return False
        return True

    def chain_is_valid(self) -> bool:
        storage_path = blockchain.adjusts.storage
        for i in range(0, len(storage_path.chain)):
            if i == 0:
                current_block: dict = storage_path.load_block(i)
                if not self.validate_block(current_block):
                    return False
            else:
                current_block: dict = storage_path.load_block(i)
                previous_block: dict = storage_path.load_block(i - 1)
                if not self.validate_block(current_block, previous_block):
                    return False
        return True


validations: 'Validations' = Validations()
