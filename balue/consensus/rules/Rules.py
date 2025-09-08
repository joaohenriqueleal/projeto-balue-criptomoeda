from consensus.AlternativesStorage import *
from typing import List
import threading
import socket


class Rules:

    def __init__(self) -> None:
        self.alternatives_storage: 'AlternativesStorage' = AlternativesStorage()
        self.chain_lock: threading.Lock = threading.Lock()
        self.peers_lock: threading.Lock = threading.Lock()

    @staticmethod
    def send_to_peer(ip: str, port: int, payload: dict) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(TIMEOUT)
                s.connect((ip, port))
                s.sendall(json.dumps(payload).encode())
        except Exception:
            return

    def broadcast_block(self, block: dict) -> None:
        def blb() -> None:
            with self.peers_lock:
                threads: List[threading.Thread] = []
                awaiting_threads: List[threading.Thread] = []
                header: str = BLOCK_HEADER
                if os.path.exists(PEERS_PATH):
                    with open(PEERS_PATH, 'r', encoding='utf-8') as pf:
                        peers = json.load(pf)
                else:
                    peers = []
                for peer in peers:
                    try:
                        payload: dict = {
                            "header": header,
                            "body": {
                                "this_block_height": block["index"],
                                "block": block
                            }
                        }
                        thread_peer = threading.Thread(target=self.send_to_peer,
                                                       args=(peer["ip"], peer["port"], payload))
                        if len(threads) < MAX_THREADS:
                            thread_peer.start()
                            threads.append(thread_peer)
                        else:
                            awaiting_threads.append(thread_peer)

                        for t in threads[:]:
                            if not t.is_alive():
                                threads.remove(t)
                                if awaiting_threads:
                                    thread_to_append = awaiting_threads.pop(0)
                                    thread_to_append.start()
                                    threads.append(thread_to_append)
                    except Exception:
                        continue

        thread_blb = threading.Thread(target=blb)
        thread_blb.start()

    @staticmethod
    def get_total_work(alternative: 'AlternativeChain') -> list[int]:
        forked_index: int = alternative.load_block(alternative.blocks[0]["index"])["index"]
        total_main_chain_work: int = 0
        total_alternative_work: int = 0
        for i in range(forked_index, len(alternative.blocks)):
            total_alternative_work += alternative.load_block(i)["nonce"]
        for i in range(forked_index, len(blockchain.adjusts.storage.chain)):
            total_main_chain_work += blockchain.adjusts.storage.load_block(i)["nonce"]
        return [total_alternative_work, total_main_chain_work]

    def reorg(self, alternative: 'AlternativeChain') -> None:
        forked_index: int = alternative.load_block(alternative.blocks[0]["index"])["index"]
        new_alternative: 'AlternativeChain' = AlternativeChain(True)
        for i in range(forked_index, len(alternative.blocks)):
            block: dict = blockchain.adjusts.storage.load_block(i)
            with open(f'{BLOCKS_PATH}/{i}.json', 'w', encoding='utf-8') as bf:
                bf.write(json.dumps(alternative.load_block(i), indent=4, ensure_ascii=False))
            new_alternative.add_block(block)
        shutil.rmtree(alternative.blocks_path)
        self.alternatives_storage.add_alternative_chain(new_alternative)
        self.alternatives_storage.alternatives.remove(alternative.to_dict())
        self.alternatives_storage.save_alternatives_pointer()

    def apply(self, block: dict) -> None:
        with self.chain_lock:
            try:
                if len(self.alternatives_storage.alternatives) == 0:
                    previous_block: Optional[dict] = None
                    if block["index"] > 0:
                        previous_block = blockchain.adjusts.storage.load_block(block["index"] - 1)
                        if validations.pending_validations.block_validations.validate(block, previous_block):
                            if len(blockchain.adjusts.storage.chain) - 1 == block["index"]:
                                if block == blockchain.adjusts.storage.load_block(block["index"]):
                                    return
                            blockchain.adjusts.storage.add_block(block)
                            if block == blockchain.adjusts.storage.load_block(block["index"]):
                                return
                            self.broadcast_block(block)
                    else:
                        if validations.pending_validations.block_validations.validate(block, previous_block):
                            if len(blockchain.adjusts.storage.chain) > 0:
                                if block == blockchain.adjusts.storage.load_block(block["index"]):
                                    return
                                alternative: 'AlternativeChain' = AlternativeChain(True)
                                alternative.add_block(block)
                                self.alternatives_storage.add_alternative_chain(alternative)
                                self.broadcast_block(block)
                                if len(alternative.blocks) == len(blockchain.adjusts.storage.chain):
                                    total_works: list[int] = self.get_total_work(alternative)
                                    if total_works[0] > total_works[1]:
                                        self.reorg(alternative)
                            else:
                                blockchain.adjusts.storage.add_block(block)
                                self.broadcast_block(block)
                else:
                    if block["index"] == 0:
                        if validations.pending_validations.block_validations.validate(block, None):
                            if block == blockchain.adjusts.storage.load_block(block["index"]):
                                return
                            for alt in self.alternatives_storage.alternatives:
                                alternative: 'AlternativeChain' = AlternativeChain.from_dict(alt)
                                if block == alternative.load_block(block["index"]):
                                    return
                            alternative: 'AlternativeChain' = AlternativeChain(True)
                            alternative.add_block(block)
                            self.alternatives_storage.add_alternative_chain(alternative)
                            self.broadcast_block(block)
                            if len(alternative.blocks) == len(blockchain.adjusts.storage.chain):
                                total_works: list[int] = self.get_total_work(alternative)
                                if total_works[0] > total_works[1]:
                                    self.reorg(alternative)
                    else:
                        previous_block: dict = blockchain.adjusts.storage.load_block(block["index"] - 1)
                        if validations.pending_validations.block_validations.validate(block, previous_block):
                            blockchain.adjusts.storage.add_block(block)
                            for alt in self.alternatives_storage.alternatives:
                                alternative: 'AlternativeChain' = AlternativeChain.from_dict(alt)
                                forked_index: int = alternative.load_block(alternative.blocks[0]["index"])["index"]
                                if len(blockchain.adjusts.storage.chain[forked_index:]) - len(alternative.blocks) >= MAX_DIFFERENCE_BLOCKS:
                                    self.alternatives_storage.alternatives.remove(alternative.to_dict())
                                    self.alternatives_storage.save_alternatives_pointer()
                                    shutil.rmtree(alternative.blocks_path)
                            if block == blockchain.adjusts.storage.load_block(block["index"]):
                                return
                            self.broadcast_block(block)
                        else:
                            for alt in self.alternatives_storage.alternatives:
                                alternative: 'AlternativeChain' = AlternativeChain.from_dict(alt)
                                previous_block: dict = alternative.load_block(block["index"] - 1)
                                if validations.pending_validations.block_validations.validate(block, previous_block):
                                    alternative.add_block(block)
                                    forked_index: int = alternative.load_block(alternative.blocks[0]["index"])["index"]
                                    if len(blockchain.adjusts.storage.chain[forked_index:]) - len(
                                            alternative.blocks) >= MAX_DIFFERENCE_BLOCKS:
                                        self.alternatives_storage.alternatives.remove(alternative.to_dict())
                                        self.alternatives_storage.save_alternatives_pointer()
                                        shutil.rmtree(alternative.blocks_path)
                                    else:
                                        if len(alternative.blocks) > len(blockchain.adjusts.storage.chain[forked_index:]):
                                            alternative.add_block(block)
                                            self.reorg(alternative)
                                        elif len(alternative.blocks) == len(blockchain.adjusts.storage.chain[forked_index:]):
                                            total_works: list[int] = self.get_total_work(alternative)
                                            if total_works[0] > total_works[1]:
                                                self.reorg(alternative)
                                    return
            except:
                return
