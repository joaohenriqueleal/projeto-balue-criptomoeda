# General configs.
VERSION: str = 'vAlpha'
DIVISIBLE: int = 100_000_000
MAX_METADATA_LENGTH: int = 80
INITIAL_TIMESTAMP: int = 1757180326489493038
MAX_TRANSACTIONS_PER_BLOCK: int = 10_000

# Chain storage configs.
CHAIN_PATH: str = 'balue/chain/blockchain.json'
BLOCKS_PATH: str = 'balue/chain'

# Reward configs.
INTERVAL_HALVING: int = 360_000
INITIAL_REWARD: int = 25 * DIVISIBLE
MIN_REWARD: int = 1
MAX_SUPLY: int = 18_000_000 * DIVISIBLE

# Block difficulty configs.
MIN_DIFFICULTY: int = 1
INTERVAL_ADJUST: int = 2016
INITIAL_DIFFICULTY: int = 6
AVERAGE_TIME: int = 600_000_000_000
ADJUST: int = 2

# Transaction difficulty configs.
INITIAL_TRANSACTIONS_DIFFICULTY: int = 4
TRANSACTION_AVERAGE_TIME: int = 10_000_000_000
TRANSACIONS_ADJUST: int = 1

# Wallets storage configs.
WALLETS_POINTER_PATH: str = 'balue/wallets/wallets.json'
WALLETS_PATH: str = 'balue/wallets'

# Protocols configs.
PEERS_PATH: str = 'balue/peers/peers.json'
SECOND_TIMEOUT: int = 3
MAX_THREADS: int = 40
TIMEOUT: int = 5
PORT: int = 8888

# Headers.
REQUEST_PENDING_BLOCK_HEADER: str = 'REQUEST_PENDING_BLOCK_CONTENT'
REQUEST_NODE_INFOS_HEADER: str = 'REQUEST_NODE_INFOS_CONTENT'
PENDING_BLOCK_HEADER: str = 'PENDING_BLOCK_CONTENT'
REQUEST_CHAIN_HEADER: str = 'REQUEST_CHAIN_CONTENT'
NODE_INFOS_HEADER: str = 'NODE_INFOS_CONTENT'
COUNT_HEADER: str = 'COUNT_CONTENT'
BLOCK_HEADER: str = 'BLOCK_CONTENT'
PEER_HEADER: str = 'PEER_CONTENT'

# Alternatives configs.
ALTERNATIVES_POINTER_PATH: str = 'balue/chain/alternatives/alternatives.json'
ALTERNATIVES_CHAINS_PATH: str = 'balue/chain/alternatives'
MAX_DIFFERENCE_BLOCKS: int = 8
