from pydantic import BaseModel


class TopicResponse(BaseModel):
    slug: str
    name: str
    tags: list[str]
