from pydantic import TypeAdapter
from core.schemas.last_matches_schema import LastMatchesModel, ModelItem

class StatsParser:
    @staticmethod
    def parse_last_matches(data: list):
        adapter: TypeAdapter[LastMatchesModel] = TypeAdapter(LastMatchesModel)
        result = adapter.validate_python(data)
        return result
    
    @staticmethod
    def parse_match(data: dict):
        adapter: TypeAdapter[ModelItem] = TypeAdapter(ModelItem)
        result = adapter.validate_python(data)
        return result
    