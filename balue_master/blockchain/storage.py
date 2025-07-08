from blockchain.block import *
import os


class Storage:

    def __init__(self) -> None:
        self.chain: list[dict] = []

        self.chain_path: str = 'balue/chain/blockchain.json'
        self.blocks_path: str = 'balue/chain'
        os.makedirs(os.path.dirname(self.chain_path), exist_ok=True)

        self.load_chain()

    def load_chain(self) -> None:
        if os.path.exists(self.chain_path):
            with open(self.chain_path, 'r', encoding='utf-8') as chain_file:
                self.chain = json.load(chain_file)
        else: self.save_chain()

    def save_chain(self) -> None:
        with open(self.chain_path, 'w', encoding='utf-8') as chain_file:
            chain_file.write(json.dumps(self.chain, indent=4, ensure_ascii=False))

    def load_block(self, index: int) -> dict:
        with open(f'{self.blocks_path}/{index}.json', 'r', encoding='utf-8') as blk:
            return json.load(blk)

    def add_block(self, block: dict) -> None:
        with open(f'{self.blocks_path}/{block["index"]}.json', 'w', encoding='utf-8') as blk:
            blk.write(json.dumps(block, indent=4, ensure_ascii=False))
        new_path: dict = {"path": f"{self.blocks_path}/{block['index']}.json"}
        self.chain.append(new_path)
        self.save_chain()
