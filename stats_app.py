
import asyncio

from core.db.h_database import MatchPayloadDAO
from core.parser import StatsParser

from core.services.services import send_match_info_into_tg

async def main():
    matches = await MatchPayloadDAO.get_all(limit=4)
    matches.reverse()
    for match in matches:
        match = StatsParser.parse_match(match.payload)
  
        await send_match_info_into_tg(match)
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
