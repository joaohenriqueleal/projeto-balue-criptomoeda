from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import os
import hashlib
import base64
import json

def gerar_chave_privada():
    return ec.generate_private_key(ec.SECP256K1(), default_backend())

def gerar_chave_publica(chave_privada):
    return chave_privada.public_key()

def gerar_endereco(chave_publica):
    public_bytes = chave_publica.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    sha256 = hashlib.sha256(public_bytes).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256)
    endereco = ripemd160.hexdigest()
    return endereco

def salvar_chave_privada(chave_privada, caminho):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "wb") as f:
        f.write(
            chave_privada.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

def salvar_chave_publica(chave_publica, caminho):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "wb") as f:
        f.write(
            chave_publica.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

def salvar_endereco(endereco, caminho):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w") as f:
        json.dump({"address": endereco}, f)

def carregar_chave_privada(caminho):
    with open(caminho, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )

def carregar_chave_publica(caminho):
    with open(caminho, "rb") as f:
        return serialization.load_pem_public_key(
            f.read(), backend=default_backend()
        )

def carregar_endereco(caminho):
    with open(caminho, "r") as f:
        data = json.load(f)
        return data["address"]

def chave_privada_para_json(chave_privada):
    pem = chave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    return {"private_key": base64.b64encode(pem).decode()}

def json_para_chave_privada(json_data):
    pem = base64.b64decode(json_data["private_key"].encode())
    return serialization.load_pem_private_key(pem, password=None, backend=default_backend())

def chave_publica_para_json(chave_publica):
    pem = chave_publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return {"public_key": base64.b64encode(pem).decode()}

def json_para_chave_publica(json_data):
    pem = base64.b64decode(json_data["public_key"].encode())
    return serialization.load_pem_public_key(pem, backend=default_backend())

def assinatura_para_json(assinatura_bytes):
    return {"signature": base64.b64encode(assinatura_bytes).decode()}

def json_para_assinatura(json_data):
    return base64.b64decode(json_data["signature"].encode())

def assinar_hash(chave_privada, mensagem_hash) -> bytes:
    if isinstance(mensagem_hash, str):
        try:
            mensagem_hash = bytes.fromhex(mensagem_hash)
        except ValueError:
            raise ValueError("A string fornecida não é um hash hexadecimal válido.")
    elif not isinstance(mensagem_hash, bytes):
        raise TypeError(
            f"mensagem_hash deve ser do tipo bytes ou string hexadecimal, recebido {type(mensagem_hash).__name__}")

    return chave_privada.sign(
        mensagem_hash,
        ec.ECDSA(hashes.SHA256())
    )

def verificar_assinatura(chave_publica, endereco: str, mensagem_hash: bytes, assinatura: bytes) -> bool:
    try:
        public_bytes = chave_publica.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        sha256 = hashlib.sha256(public_bytes).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256)
        endereco_calculado = ripemd160.hexdigest()

        if endereco_calculado != endereco:
            return False
        chave_publica.verify(
            assinatura,
            mensagem_hash,
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except Exception:
        return False
