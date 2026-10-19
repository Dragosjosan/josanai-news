from pydantic import BaseModel


class TopicResponse(BaseModel):
    slug: str
    name: str
    description: str
    tags: list[str]
