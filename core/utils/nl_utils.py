

import json
from typing import Any


class ArrayGraphDecoder:
    def __init__(self, data: list):
        self.data = data
        self.cache = {}

    def decode(self, value: Any) -> Any:
        if isinstance(value, int):
            return self.resolve(value)

        if isinstance(value, list):
            return [self.decode(v) for v in value]

        if isinstance(value, dict):
            result = {}

            for key, val in value.items():
                if key.startswith("_") and key[1:].isdigit():
                    real_key = self.resolve(int(key[1:]))
                else:
                    real_key = key

                result[real_key] = self.decode(val)

            return result

        return value

    def resolve(self, index: int):
        if index in self.cache:
            return self.cache[index]

        value = self.data[index]

        self.cache[index] = None

        decoded = self.decode(value)

        self.cache[index] = decoded
        return decoded


def decode_array_graph(text: str):
    data = json.loads(text)

    decoder = ArrayGraphDecoder(data)

    return decoder.resolve(0)