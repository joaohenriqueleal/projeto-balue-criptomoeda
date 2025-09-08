from typing import Union
import hashlib
import json


class Hasher:

    @staticmethod
    def hasher(data: Union[list[dict], str, dict]) -> str:
        return hashlib.sha256(json.dumps(
            data, sort_keys=True, ensure_ascii=False)
        .encode()).hexdigest()
