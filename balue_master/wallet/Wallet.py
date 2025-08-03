from wallet.walletsMethods import *


class Wallet:

    def __init__(self, setup: bool, name: str = None) -> None:
        self.wallet_storage = WalletStorage(name)
        self.wallet_methods = WalletMethods()

        self.private_key = self.generate_private_key()
        self.public_key = self.generate_public_key()
        self.address = self.generate_address()

        if setup:
            self._setup_keys()
            self.wallet_storage.wallets_pointer.set_last_used(self.wallet_storage.name)

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
