
import asyncio
import datetime
import json
import logging
from typing import Any
from cloudscraper import CloudScraper


logger = logging.getLogger(__name__)

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

class NightLightApi:
    
    DATA_PATH = "data/"
    CODES_PATH = DATA_PATH + "codes.json"
    
    scraper = CloudScraper()    
    @classmethod
    async def get_redeem_codes(cls):
        res = cls.scraper.get("https://nightlight.gg/codes.data?_routes=routes%2Fcodes")
        if res.ok:
            data = res.json()
            root = ArrayGraphDecoder(data).resolve(0)
            with open(cls.CODES_PATH, "w", encoding="utf-8") as f:
                json.dump(root.get("routes/codes", {}).get("data", {}).get("codes", []), f, indent=2)
            return root     
            
async def main():
    codes = await NightLightApi.get_redeem_codes()
    with open(NightLightApi.CODES_PATH, "r", encoding="utf-8") as f:
        last_codes = json.load(f)
    for code in codes.get("routes/codes", {}).get("data", {}).get("codes", []):
        if code.get('expired') == "routes/codes":
            continue
        else:
            logger.info(f"{code.get('title')} | {code.get('code')} | {code.get('created_at')} | {code.get('expires_at')}")
        
if __name__ == "__main__":
    asyncio.run(main())