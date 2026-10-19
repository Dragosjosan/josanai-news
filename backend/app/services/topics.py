from sqlalchemy.orm import Session

from app.db.repositories import topics as topic_repo
from app.dto.topics import TopicResponse


class TopicService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_topics(self) -> list[TopicResponse]:
        return [
            TopicResponse(
                slug=topic.slug,
                name=topic.name,
                description=topic.description,
                tags=[tag.name for tag in topic.tags],
            )
            for topic in topic_repo.list_topics(self._session)
        ]
