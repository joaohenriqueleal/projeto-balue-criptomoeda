from wallet.wallet_methods import *


class Wallet:

    def __init__(self, setup: bool) -> None:
        self.wallet_storage: 'WalletStorage' = WalletStorage()
        self.wallet_methods: 'WalletMethods' = WalletMethods()

        self.private_key = self.generate_private_key()
        self.public_key = self.generate_public_key()
        self.address = self.generate_address()
        if setup:
            self._setup_keys()

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
        endereco = ripemd160.hexdigest()
        return endereco
