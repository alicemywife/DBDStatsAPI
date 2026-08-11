
from sqlalchemy import select, delete, update
from core.db.models import MatchPayload

from . import engine, asession, Base

class Database:
    @staticmethod
    async def create_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
class MatchPayloadDAO:
    @staticmethod
    async def add(payload: dict):
        async with asession() as session:
                    
            matchStartTime = payload.get("matchStat").get("matchStartTime")
            if await MatchPayloadDAO.get(matchStartTime=matchStartTime):
                if not payload.get("matchStat").get('isCustomMatch'):
                    await MatchPayloadDAO.update(matchStartTime=matchStartTime, payload=payload)
                    return False 
                return False
            info = MatchPayload(
                matchStartTime=matchStartTime,
                payload=payload
                )
            session.add(info)
            await session.commit()
            return True
    
    @staticmethod
    async def get(matchStartTime: int):
        async with asession() as session:
            query = await session.execute(select(MatchPayload).where(MatchPayload.matchStartTime == matchStartTime))
            return query.scalar_one_or_none()
        
    @staticmethod
    async def get_all(limit=10, offset=0, reverse=True):
        async with asession() as session:
            if reverse:
                query = await session.execute(select(MatchPayload).limit(limit).offset(offset).order_by(MatchPayload.matchStartTime.desc()))
            else:
                query = await session.execute(select(MatchPayload).limit(limit).offset(offset))
            return query.scalars().all()
        
    @staticmethod
    async def delete(matchStartTime: int):
        async with asession() as session:
            await session.execute(delete(MatchPayload).where(MatchPayload.matchStartTime == matchStartTime))
            await session.commit()
            
    @staticmethod
    async def update(matchStartTime: int, payload: dict):
        async with asession() as session:
            await session.execute(update(MatchPayload).where(MatchPayload.matchStartTime == matchStartTime).values(payload=payload))
            await session.commit()