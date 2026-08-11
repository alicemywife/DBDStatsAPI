
import asyncio
import json
import logging
from cloudscraper import CloudScraper

from core.utils.nl_utils import ArrayGraphDecoder


logger = logging.getLogger(__name__)

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
    for code in codes.get("routes/codes", {}).get("data", {}).get("codes", []):
        if code.get('expired') == "routes/codes":
            continue
        else:
            logger.info(f"{code.get('title')} | {code.get('code')} | {code.get('created_at')} | {code.get('expires_at')}")
        
if __name__ == "__main__":
    asyncio.run(main())