from consensus.AlternativeChain import *


class AlternativesStorage:

    def __init__(self) -> None:
        self.alternatives_pointer_path: str = ALTERNATIVES_POINTER_PATH
        os.makedirs(os.path.dirname(self.alternatives_pointer_path), exist_ok=True)

        self.alternatives: list[dict] = []

        self.load_alternatives_pointer()

    def load_alternatives_pointer(self) -> None:
        if os.path.exists(self.alternatives_pointer_path):
            with open(self.alternatives_pointer_path ,'r', encoding='utf-8') as apf:
                self.alternatives = json.load(apf)
        else:
            self.save_alternatives_pointer()

    def save_alternatives_pointer(self) -> None:
        with open(self.alternatives_pointer_path, 'w', encoding='utf-8') as apf:
            apf.write(json.dumps(self.alternatives, indent=4, ensure_ascii=False))

    def add_alternative_chain(self, alternative: AlternativeChain) -> None:
        self.alternatives.append(alternative.to_dict())
        self.save_alternatives_pointer()

    def load_alternative_chain(self, name: str) -> 'AlternativeChain' or None:
        for ac in self.alternatives:
            if ac["name"] == name:
                return AlternativeChain.from_dict(ac)
        return None
