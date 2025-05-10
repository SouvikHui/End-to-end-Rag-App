from pydantic import BaseModel
from typing import List

class URLRequest(BaseModel):
    urls: List[str]

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
