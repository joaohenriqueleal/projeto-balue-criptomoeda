from blockchain.primitives.Block import *
import os


class ChainStorage:

    def __init__(self) -> None:
        self.chain_path: str = CHAIN_PATH
        self.blocks_path: str = BLOCKS_PATH

        os.makedirs(os.path.dirname(self.chain_path), exist_ok=True)
        os.makedirs(self.blocks_path, exist_ok=True)

        self.chain: list[dict] = []
        self.load_chain()
        self.sync_blocks()

    def load_chain(self) -> None:
        if os.path.exists(self.chain_path):
            with open(self.chain_path, 'r', encoding='utf-8') as cf:
                self.chain = json.load(cf)
        else:
            self.save_chain()

    def save_chain(self) -> None:
        with open(self.chain_path, 'w', encoding='utf-8') as cf:
            cf.write(json.dumps(self.chain, indent=4, ensure_ascii=False))

    def add_block(self, block: dict) -> None:
        block_path = os.path.join(self.blocks_path, f'{block["index"]}.json')
        with open(block_path, 'w', encoding='utf-8') as bf:
            bf.write(json.dumps(block, indent=4, ensure_ascii=False))
        self.chain.append({"path": block_path})
        self.sync_blocks()
        self.save_chain()

    def load_block(self, index: int) -> dict or None:
        try:
            block_path = os.path.join(self.blocks_path, f'{index}.json')
            with open(block_path, 'r', encoding='utf-8') as bf:
                return json.load(bf)
        except:
            return

    def sync_blocks(self) -> None:
        valid_chain = []

        existing_files = {
            int(fname.replace(".json", "")): os.path.join(self.blocks_path, fname)
            for fname in os.listdir(self.blocks_path)
            if fname.endswith(".json") and fname.replace(".json", "").isdigit()
        }

        for index in sorted(existing_files.keys()):
            path = existing_files[index]
            if os.path.isfile(path):
                valid_chain.append({"path": path})

        self.chain = valid_chain
        self.save_chain()
