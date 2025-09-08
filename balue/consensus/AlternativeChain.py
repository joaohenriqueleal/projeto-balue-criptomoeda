from connection.peers.PeersStorage import *


class AlternativeChain:

    def __init__(self, setup: bool) -> None:
        self.name: str = str(uuid.uuid4())

        self.blocks_path: str = f'{ALTERNATIVES_CHAINS_PATH}/{self.name}'
        self.blocks_pointer_path: str = f'{self.blocks_path}/blocks.json'

        self.blocks: list[dict] = []

        if setup:
            os.makedirs(self.blocks_path, exist_ok=True)
            self.synch_blocks()
        try:
            self.load_blocks()
        except:
            pass

    def synch_blocks(self) -> None:
        blocks_list: list[dict] = []
        if os.path.exists(self.blocks_path):
            for fname in sorted(os.listdir(self.blocks_path)):
                if fname.endswith(".json") and fname != "blocks.json":
                    try:
                        index = int(fname.replace(".json", ""))
                        blocks_list.append({
                            "index": index,
                            "path": os.path.join(self.blocks_path, fname)
                        })
                    except ValueError:
                        continue
        self.blocks = sorted(blocks_list, key=lambda b: b["index"])
        self.save_blocks()

    def load_blocks(self) -> None:
        if os.path.exists(self.blocks_pointer_path):
            with open(self.blocks_pointer_path, 'r', encoding='utf-8') as bf:
                self.blocks = json.load(bf)
        else:
            self.save_blocks()

    def save_blocks(self) -> None:
        with open(self.blocks_pointer_path, 'w', encoding='utf-8') as bf:
            bf.write(json.dumps(self.blocks, indent=4, ensure_ascii=False))

    def load_block(self, index: int) -> dict:
        with open(f'{self.blocks_path}/{index}.json', 'r', encoding='utf-8') as bf:
            return json.load(bf)

    def add_block(self, block: dict) -> None:
        new_path = f'{self.blocks_path}/{block["index"]}.json'
        with open(new_path, 'w', encoding='utf-8') as bf:
            bf.write(json.dumps(block, indent=4, ensure_ascii=False))
        self.synch_blocks()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "blocks_pointer_path": self.blocks_pointer_path
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AlternativeChain':
        alternative_chain: 'AlternativeChain' = AlternativeChain(False)

        alternative_chain.name = data["name"]
        alternative_chain.blocks_path = f'{ALTERNATIVES_CHAINS_PATH}/{alternative_chain.name}'
        alternative_chain.blocks_pointer_path = f'{alternative_chain.blocks_path}/blocks.json'

        os.makedirs(alternative_chain.blocks_path, exist_ok=True)
        alternative_chain.load_blocks()
        alternative_chain.synch_blocks()
        return alternative_chain
