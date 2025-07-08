import requests
import socket

# Reward configs.
INITIAL_REWARD: float = 25
INTERVAL_HALVING: int = 360_000
MAX_SUPLY: int = 18_000_000
MIN_REWARD: float = 0.00000001

# Difficulty block configs.
INITIAL_DIFFICULTY: int = 6
INTERVAL_ADJUST: int = 2016
ADJUST: int = 2
AVERAGE_TIME: int = 600_000_000_000

# Difficulty transactions configs.
TRANSACIONS_ADJUST: int = 1
INITIAL_TRANSACTIONS_DIFFICULTY: int = 4
TRANSACTION_AVERAGE_TIME: int = 10_000_000_000

# General.
INITIAL_TIMESTAMP: int = 0 # Atualizar com o timestamp do bloco gênesis.
MAX_TRANSACTIONS_PER_BLOCK: int = 10_000

# Protocol configs.
TIMEOUT: int = 5
PORT: int = 8888

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        return response.text
    except Exception as e:
        print(f"Erro ao obter IP público: {e}")
        return get_local_ip()

def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Erro ao obter IP local: {e}")
        return "127.0.0.1"

LOCAL_IP: str = get_local_ip()
PUBLIC_IP: str = get_public_ip()
