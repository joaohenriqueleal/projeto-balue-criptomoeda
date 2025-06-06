from main.wallet.wallet_keys import *
import os


class Wallet:

    def __init__(self, setup: bool):
        self.private_key_path = "balue/private_key.pem"
        self.public_key_path = "balue/public_key.pem"
        self.address_path = "balue/address.json"

        self.private_key = gerar_chave_privada()
        self.public_key = gerar_chave_publica(self.private_key)
        self.address = gerar_endereco(self.public_key)
        if setup:
            self._setup_keys()

    def _setup_keys(self):
        if os.path.exists(self.private_key_path) and os.path.exists(self.public_key_path) and os.path.exists(self.address_path):
            self.private_key = carregar_chave_privada(self.private_key_path)
            self.public_key = carregar_chave_publica(self.public_key_path)
            self.address = carregar_endereco(self.address_path)
        else:
            salvar_chave_privada(self.private_key, self.private_key_path)
            salvar_chave_publica(self.public_key, self.public_key_path)
            salvar_endereco(self.address, self.address_path)
