from pydantic import BaseModel

class TradeCreate(BaseModel):
    topic: str