
import json
from typing import Any, Literal
from pathlib import Path

from aiohttp import ClientSession
import logging

from yarl import URL

logger = logging.getLogger(__name__)

class DBDStats:
    
    headers = {}
    
    @classmethod
    def update_headers(cls, access_token: str):
        cls.headers = {
            "Authorization": f"Bearer {access_token}"
        }
    
    @classmethod
    async def get_access_token(cls):
        logger.info("Getting tokens...")
        async with ClientSession() as session:
            with open('core/session.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                refresh_token = data['refresh_token']
            data = {
                "client_id": "DBDStats",
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            async with session.post('https://account-backend.bhvr.com/sso/token', json=data) as res:
                if res.ok:
                    result = await res.json()
                    cls.update_headers(result['access_token'])
                    with open('core/session.json', 'w', encoding='utf-8') as f:
                        json.dump({"refresh_token": result['refresh_token']}, f, indent=2)
                    logger.info("Tokens updated")
                    return result
                else:
                    logger.error(f'Error: {res.status} {res.reason} {await res.text()}')
                    logger.error("Tokens not updated")
                    return {}
            
    
    @classmethod
    async def overview_stats(cls, lang: Literal['en', 'ru'] = 'en'):
        async with ClientSession() as session:
            endpoint = f'https://account-backend.bhvr.com/player-stats/games/dbd/providers/bhvr?lang={lang}'
            async with session.get(endpoint, headers=cls.headers) as res:
                if res.ok:
                    result = await res.json()
                    with open('core/schemas/overview.json', 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2)
                    return result
                elif res.status == 401:
                    await cls.get_access_token()
                    return await cls.overview_stats(lang=lang)
                else:
                    logger.error(f'Error: {res.status} {res.reason} {await res.text()}')
                    return {}
    @classmethod
    async def general_stats(cls, lang: Literal['en', 'ru'] = 'en'):
        async with ClientSession() as session:
            endpoint = f'https://account-backend.bhvr.com/player-stats/games/dbd/providers/bhvr?lang={lang}&matchCategory=Regular'
            async with session.get(endpoint, headers=cls.headers) as res:
                if res.ok:
                    result = await res.json()
                    with open('core/schemas/general.json', 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2)
                    return result
                elif res.status == 401:
                    await cls.get_access_token()
                    return await cls.general_stats(lang=lang)
                else:
                    logger.error(f'Error: {res.status} {res.reason} {await res.text()}')
                    return {}
            
    @classmethod
    async def last_matches(cls, lang: Literal['en', 'ru'] = 'en') -> dict[str, Any]:
        async with ClientSession() as session:
            endpoint = f'https://account-backend.bhvr.com/player-stats/match-history/games/dbd/providers/bhvr?lang={lang}&limit=30'
            async with session.get(endpoint, headers=cls.headers) as res:
                if res.ok:
                    result = await res.json()
                    # with open('core/schemas/last_matches.json', 'w', encoding='utf-8') as f:
                    #     json.dump(result, f, indent=2)
                    return result
                elif res.status == 401:
                    await cls.get_access_token()
                    return await cls.last_matches(lang=lang)
                else:
                    logger.error(f'Error: {res.status} {res.reason} {await res.text()}')
                    return {}
                
    @classmethod
    async def get_asset(cls, url_path: str, mode: Literal['local', 'dbdstat'] = 'local'):
        async with ClientSession() as session:
            endpoint = 'https://stats.deadbydaylight.com/_next/image'
            params = {
                "url": f"https://assets.live.bhvraccount.com/" + url_path,
                "w": "256",
                "q": "75"
            }
            if mode == "dbdstat":
                return URL(endpoint).with_query(params)
            async with session.get(endpoint, params=params) as res:        
                if res.ok:                    
                    path = Path("core/assets/" + url_path)
                    path.mkdir(parents=True, exist_ok=True)
                    with open(path, "wb") as f:
                        f.write(await res.read())
                else:
                    logger.error(f'Error: {res.status} {res.reason} {await res.text()}')
                    return {}