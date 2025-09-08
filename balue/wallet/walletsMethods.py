from cryptography.hazmat.primitives.asymmetric import ec
from wallet.wallet_storage.walletsStorage import *
from cryptography.hazmat.primitives import hashes
import hashlib
import base64


class WalletMethods:

    @staticmethod
    def private_key_to_json(private_key):
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return {"private_key": base64.b64encode(pem).decode()}

    @staticmethod
    def json_to_private_key(json_data):
        pem = base64.b64decode(json_data["private_key"].encode())
        return serialization.load_pem_private_key(pem, password=None, backend=default_backend())

    @staticmethod
    def public_key_to_json(public_key):
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return {"public_key": base64.b64encode(pem).decode()}

    @staticmethod
    def json_to_public_key(json_data):
        pem = base64.b64decode(json_data["public_key"].encode())
        return serialization.load_pem_public_key(pem, backend=default_backend())

    @staticmethod
    def signature_to_json(signature_bytes):
        return {"signature": base64.b64encode(signature_bytes).decode()}

    @staticmethod
    def json_to_signature(json_data):
        return base64.b64decode(json_data["signature"].encode())

    @staticmethod
    def sign_hash(private_key, message_hash) -> bytes:
        if isinstance(message_hash, str):
            try:
                message_hash: bytes = bytes.fromhex(message_hash)
            except ValueError:
                raise ValueError("A string fornecida não é um hash hexadecimal válido.")
        elif not isinstance(message_hash, bytes):
            raise TypeError(
                f"mensagem_hash deve ser do tipo bytes ou string hexadecimal,"
                f" recebido {type(message_hash).__name__}")

        return private_key.sign(
            message_hash,
            ec.ECDSA(hashes.SHA256())
        )

    @staticmethod
    def verify_signature(public_key, address: str,
                             message_hash: bytes, signature: bytes) -> bool:

        try:
            public_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            sha256 = hashlib.sha256(public_bytes).digest()
            ripemd160 = hashlib.new('ripemd160')
            ripemd160.update(sha256)
            endereco_calculado = ripemd160.hexdigest()

            if endereco_calculado != address:
                return False
            public_key.verify(
                signature,
                message_hash,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except:
            return False
