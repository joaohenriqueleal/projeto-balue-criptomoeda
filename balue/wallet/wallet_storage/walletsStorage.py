from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from wallet.wallet_storage.WalletsPointer import *
import json
import os


class WalletStorage:

    def __init__(self, name: str = None) -> None:
        self.wallets_pointer = WalletsPointer()
        if name is None:
            name = self.wallets_pointer.get_last_used_wallet_name()
        self.name = name
        self.base_path = f'{self.wallets_pointer.wallets_path}/{self.name}'
        self.private_key_path = f'{self.base_path}/private_key.pem'
        self.public_key_path = f'{self.base_path}/public_key.pem'
        self.address_path = f'{self.base_path}/address.json'

    def load_private_key(self):
        with open(self.private_key_path, "rb") as f:
            return serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )

    def load_public_key(self):
        with open(self.public_key_path, "rb") as f:
            return serialization.load_pem_public_key(
                f.read(), backend=default_backend()
            )

    def load_address(self) -> str:
        with open(self.address_path, "r") as f:
            data = json.load(f)
            return data["address"]

    def save_private_key(self, private_key) -> None:
        os.makedirs(os.path.dirname(self.private_key_path), exist_ok=True)
        with open(self.private_key_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )

    def save_public_key(self, public_key):
        os.makedirs(os.path.dirname(self.public_key_path), exist_ok=True)
        with open(self.public_key_path, "wb") as f:
            f.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )

    def save_address(self, address):
        os.makedirs(os.path.dirname(self.address_path), exist_ok=True)
        with open(self.address_path, "w") as f:
            f.write(json.dumps({"address": address}, indent=4, ensure_ascii=False))
