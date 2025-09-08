# Balue – A Decentralized Peer-to-Peer Blockchain

Balue is an experimental peer-to-peer digital currency and blockchain system written in Python.  
It is designed as a lightweight, educational implementation of a cryptocurrency network, featuring block mining, transactions, wallet management, and peer synchronization.

---

## Blockchain Parameters

- **Block Reward:** Starts at 25 BALUE per block  
- **Halving:** The block reward is halved every 360,000 blocks  
- **Difficulty Adjustment:** The mining difficulty is adjusted every 2,016 blocks  

---

## How the Blockchain Works

### Blocks
Each block contains a set of transactions, a timestamp, the hash of the previous block, and a proof of work.  
Blocks are chained together cryptographically, forming the immutable blockchain ledger.

### Transactions
Users transfer value using cryptographic signatures based on elliptic curve cryptography (ECC).  
Each transaction is verified and included in a block by miners.

### Proof of Work (PoW)
Mining requires finding a valid hash below the network’s current difficulty target.  
This process secures the blockchain and prevents double-spending.

### Consensus
The longest valid chain (with the most accumulated proof of work) is considered the true blockchain.  
Peers automatically synchronize with the network to stay updated.

---

## Running a Balue Node

### Requirements
- Python 3.8 or higher  
- Dependencies listed in `requirements.txt`

### Installation

```bash
# Clone the repository
git clone https://github.com/joaohenriqueleal/projeto-balue-criptomoeda
cd projeto-balue-criptomoeda-main/balue

# Install dependencies
pip install -r requirements.txt

# Node initialization 
python3 InitCli.py
```

