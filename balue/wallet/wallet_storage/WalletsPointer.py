from blockchain.Blockchain import *
from typing import Optional
import shutil
import json
import os


class WalletsPointer:

    def __init__(self) -> None:
        self.pointer_path: str = WALLETS_POINTER_PATH
        self.wallets_path: str = WALLETS_PATH
        self.wallets: list[dict] = []

        os.makedirs(os.path.dirname(self.pointer_path), exist_ok=True)
        self.load_pointer()

    def load_pointer(self) -> None:
        if os.path.exists(self.pointer_path):
            with open(self.pointer_path, 'r', encoding='utf-8') as pf:
                self.wallets = json.load(pf)
        else:
            self.save_pointer()

    def save_pointer(self) -> None:
        with open(self.pointer_path, 'w', encoding='utf-8') as pf:
            pf.write(json.dumps(self.wallets, ensure_ascii=False, indent=4))

    def add_new_wallet(self, name: str) -> None:
        new_wallet = {
            "name": name,
            "path": f'{self.wallets_path}/{name}',
            "last_used": True
        }

        for wallet in self.wallets:
            wallet["last_used"] = False

        self.wallets.append(new_wallet)
        self.save_pointer()

    def set_last_used(self, name: str) -> None:
        for wallet in self.wallets:
            wallet["last_used"] = (wallet["name"] == name)
        self.save_pointer()

    def get_last_used_wallet_name(self) -> Optional[str]:
        for wallet in self.wallets:
            if wallet.get("last_used", False):
                return wallet["name"]
        return None

    def list_wallet_names(self) -> list[str]:
        return [wallet["name"] for wallet in self.wallets]

    def wallet_exists(self, name: str) -> bool:
        return any(wallet["name"] == name for wallet in self.wallets)

    def delete_wallet(self, name: str) -> bool:

        carteira = next((w for w in self.wallets if w["name"] == name), None)
        if not carteira:
            return False

        self.wallets = [w for w in self.wallets if w["name"] != name]
        self.save_pointer()

        wallet_path = os.path.join(self.wallets_path, name)
        if os.path.exists(wallet_path):
            shutil.rmtree(wallet_path)
        return True
