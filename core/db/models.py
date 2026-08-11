
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import JSON

from . import Base

class MatchPayload(Base):
    __tablename__ = 'basic_payloads'

    matchStartTime: Mapped[int] = mapped_column(unique=True)
    payload: Mapped[dict] = mapped_column(JSON)
    
class Asset(Base):
    __tablename__ = "assets"
    
    uri: Mapped[str]
    name: Mapped[str]