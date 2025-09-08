from wallet.walletsMethods import *


class Wallet:

    def __init__(self, setup: bool, name: str = None) -> None:
        self.wallet_storage = WalletStorage(name)
        self.wallet_methods = WalletMethods()

        self.private_key = self.generate_private_key()
        self.public_key = self.generate_public_key()
        self.address = self.generate_address()
        self.balance: float = 0

        if setup:
            self._setup_keys()
            self.wallet_storage.wallets_pointer.set_last_used(self.wallet_storage.name)
        self.define_balance()

    def _setup_keys(self):
        if (os.path.exists(self.wallet_storage.private_key_path) and
            os.path.exists(self.wallet_storage.public_key_path) and
            os.path.exists(self.wallet_storage.address_path)):

            self.private_key = self.wallet_storage.load_private_key()
            self.public_key = self.wallet_storage.load_public_key()
            self.address = self.wallet_storage.load_address()
        else:
            self.wallet_storage.save_private_key(self.private_key)
            self.wallet_storage.save_public_key(self.public_key)
            self.wallet_storage.save_address(self.address)
            self.wallet_storage.wallets_pointer.add_new_wallet(self.wallet_storage.name)

    def get_pending_balance(self) -> float:
        balance: int = 0
        for block in blockchain.pending_blocks:
            for tr in block.transactions:
                if tr["sender"] == self.address:
                    balance -= (tr["value"] + tr["fee"])
        return balance / DIVISIBLE

    def get_balance_range(self, start_index: int, end_index: int) -> float:
        balance: int = 0
        address: str = self.address
        for i in range(start_index, end_index):
            block: dict = blockchain.adjusts.storage.load_block(i)
            if block["miner_address"] == address:
                balance += (block["reward"] + block["total_fees"])
            for tr in block["transactions"]:
                if tr["sender"] == address:
                    balance -= (tr["value"] + tr["fee"])
                if tr["receiver"] == address:
                    balance += tr["value"]
        return balance / DIVISIBLE

    def define_balance(self) -> None:
        chain_index = blockchain.get_index()
        recent_start = max(0, chain_index - MAX_DIFFERENCE_BLOCKS)
        balance: float = 0

        for w in self.wallet_storage.wallets_pointer.wallets:
            if w["name"] == self.wallet_storage.name:
                if w.get("balance") is None:
                    w["balance"] = self.get_balance_range(0, recent_start)
                    w["last_block_height"] = recent_start
                    self.wallet_storage.wallets_pointer.save_pointer()
                else:
                    new_blocks_balance = self.get_balance_range(w["last_block_height"], recent_start)
                    w["balance"] += new_blocks_balance
                    w["last_block_height"] = recent_start
                    self.wallet_storage.wallets_pointer.save_pointer()
                balance = w["balance"]

        recent_blocks_balance = self.get_balance_range(recent_start, chain_index)
        self.balance = balance + recent_blocks_balance + self.get_pending_balance()

    @staticmethod
    def generate_private_key():
        return ec.generate_private_key(ec.SECP256K1(), default_backend())

    def generate_public_key(self):
        return self.private_key.public_key()

    def generate_address(self):
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        sha256 = hashlib.sha256(public_bytes).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256)
        return ripemd160.hexdigest()
