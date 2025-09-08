from blockchain.ChainStorage import *


class Adjusts:

    def __init__(self) -> None:
        self.storage: 'ChainStorage' = ChainStorage()

    def adjust_reward(self, index: int) -> int:
        if index < INTERVAL_HALVING:
            return INITIAL_REWARD
        total_coins: float = 0
        for i in range(len(self.storage.chain)):
            total_coins += self.storage.load_block(i)["reward"]
        if total_coins >= MAX_SUPLY:
            return 0
        halving_count: int = index // INTERVAL_HALVING
        reward: int = INITIAL_REWARD / (2 ** halving_count)
        return max(reward, MIN_REWARD)

    def adjust_difficulty(self, index: int) -> int:
        if index < INTERVAL_ADJUST:
            return INITIAL_DIFFICULTY
        if index % INTERVAL_ADJUST != 0:
            return self.storage.load_block(index - 1)["difficulty"]
        sum_diferences: int = 0
        start = index - INTERVAL_ADJUST
        for i in range(start, index):
            block: dict = self.storage.load_block(i)
            sum_diferences += block["validation_timestamp"] - block["timestamp"]
        median_time: float = sum_diferences / INTERVAL_ADJUST
        ultimate_difficulty: int = self.storage.load_block(index - 1)["difficulty"]
        if median_time >= AVERAGE_TIME:
            return max(ultimate_difficulty - ADJUST, MIN_DIFFICULTY)
        else:
            return max(ultimate_difficulty + ADJUST, MIN_DIFFICULTY)

    def adjust_transactions_difficulty(self, index: int) -> int:
        if index < INTERVAL_ADJUST:
            return INITIAL_TRANSACTIONS_DIFFICULTY
        if index % INTERVAL_ADJUST != 0:
            return self.storage.load_block(index - 1)["transactions"][-1]["difficulty"]
        sum_diferences: int = 0
        total_tx: int = 0
        start = index - INTERVAL_ADJUST
        for i in range(start, index):
            block: dict = self.storage.load_block(i)
            for tr in block["transactions"]:
                sum_diferences += tr["validation_timestamp"] - tr["timestamp"]
                total_tx += 1
        if total_tx == 0:
            return self.storage.load_block(index - 1)["transactions"][-1]["difficulty"]
        median_time: float = sum_diferences / total_tx
        ultimate_difficulty: int = self.storage.load_block(index - 1)["transactions"][-1]["difficulty"]
        if median_time >= TRANSACTION_AVERAGE_TIME:
            return max(ultimate_difficulty - TRANSACIONS_ADJUST, MIN_DIFFICULTY)
        else:
            return max(ultimate_difficulty + TRANSACIONS_ADJUST, MIN_DIFFICULTY)
