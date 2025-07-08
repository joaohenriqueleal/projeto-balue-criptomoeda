from blockchain.storage import *
from blockchain.config import *


class Adjusts:

    def __init__(self) -> None:
        self.storage: Storage = Storage()

    def adjust_reward(self, index: int) -> float:
        if index < INTERVAL_HALVING:
            return INITIAL_REWARD
        total_coins: float = 0
        for i in range(len(self.storage.chain)):
            total_coins += self.storage.load_block(i)["reward"]
        if total_coins >= MAX_SUPLY:
            return 0
        halving_count: int = index // INTERVAL_HALVING
        reward: float = INITIAL_REWARD / (2 ** halving_count)
        return max(reward, MIN_REWARD)

    def adjust_difficulty(self, index: int) -> int:
        if index < INTERVAL_ADJUST:
            return INITIAL_DIFFICULTY
        sum_diferences: int = 0
        start = max(0, index - INTERVAL_ADJUST)
        for i in range(start, index):
            block: dict = self.storage.load_block(i)
            sum_diferences += block["validation_timestamp"] - block["timestamp"]
        median_time: float = sum_diferences / INTERVAL_ADJUST
        ultimate_difficulty: int = self.storage.load_block(index - 1)["difficulty"]
        if median_time >= AVERAGE_TIME:
            return ultimate_difficulty - ADJUST
        else:
            return ultimate_difficulty + ADJUST

    def adjust_transactions_difficulty(self, index: int) -> int:
        if index < INTERVAL_ADJUST:
            return INITIAL_TRANSACTIONS_DIFFICULTY
        sum_diferences: int = 0
        start = max(0, index - INTERVAL_ADJUST)
        for i in range(start, index):
            block: dict = self.storage.load_block(i)
            for tr in block["transactions"]:
                sum_diferences += tr["validation_timestamp"] - tr["timestamp"]
        median_time: float = sum_diferences / INTERVAL_ADJUST
        ultimate_difficulty: int = self.storage.load_block(index - 1)["transactions"][-1]["difficulty"]
        if median_time >= TRANSACTION_AVERAGE_TIME:
            return ultimate_difficulty - TRANSACIONS_ADJUST
        else:
            return ultimate_difficulty + TRANSACIONS_ADJUST

    def min_transactions(self, index: int) -> int:
        sum_transactions: int = 0
        start: int = max(0, index - INTERVAL_ADJUST)
        count: int = index - start
        for i in range(start, index):
            block: dict = self.storage.load_block(i)
            sum_transactions += block["total_transactions"]
        return sum_transactions // count if count > 0 else 0
