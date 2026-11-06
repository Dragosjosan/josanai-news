from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

STORY = {"title": "Gene therapy cuts bleeds by 90%", "url": "https://example.com/gene-therapy"}


def feed_ids(client: TestClient, query: str) -> list[int]:
    response = client.get(f"items?{query}")
    assert response.status_code == 200
    return [item["id"] for item in response.json()["items"]]


def test_an_anonymous_post_is_published(client: TestClient) -> None:
    response = client.post("items", json=STORY)

    assert response.status_code == 201
    item = response.json()
    assert response.headers["location"] == f"/api/v1/items/{item['id']}"
    assert item["title"] == STORY["title"]
    assert item["url"] == STORY["url"]
    assert item["domain"] == "example.com"
    assert item["username"] is None
    assert item["label"] is None
    assert item["score"] == 0
    assert item["comment_count"] == 0


def test_a_post_appears_on_the_front_page_new_past_and_its_item_page(
    client: TestClient,
) -> None:
    item_id = client.post("items", json=STORY).json()["id"]
    today = datetime.now(UTC).date().isoformat()

    assert feed_ids(client, "sort=top") == [item_id]
    assert feed_ids(client, "sort=new") == [item_id]
    assert feed_ids(client, f"sort=top&day={today}") == [item_id]
    page = client.get(f"items/{item_id}")
    assert page.status_code == 200
    assert page.json()["title"] == STORY["title"]


def test_the_same_url_twice_is_a_duplicate(client: TestClient) -> None:
    first = client.post("items", json=STORY).json()

    second = client.post("items", json={**STORY, "title": "Another title"})

    assert second.status_code == 409
    assert second.json() == {
        "error": {
            "code": "duplicate",
            "message": "This story is already on the site.",
            "details": {
                "item_id": first["id"],
                "title": STORY["title"],
                "url": STORY["url"],
                "reason": "same_url",
            },
        }
    }
    assert feed_ids(client, "sort=new") == [first["id"]]


@pytest.mark.parametrize(
    "url",
    [
        "javascript:alert(1)",
        "JavaScript:alert(document.cookie)",
        "data:text/html,<script>alert(1)</script>",
        "vbscript:msgbox(1)",
    ],
)
def test_a_link_that_could_run_code_is_refused(client: TestClient, url: str) -> None:
    response = client.post("items", json={**STORY, "url": url})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert [field["loc"] for field in error["details"]["fields"]] == [["body", "url"]]
    assert feed_ids(client, "sort=new") == []


def test_an_anonymous_post_cannot_set_a_label(client: TestClient) -> None:
    response = client.post("items", json={**STORY, "label": "my-bot"})

    assert response.status_code == 422
    assert response.json()["error"]["details"] == {
        "fields": [{"loc": ["body", "label"], "message": "only accounts can set a label"}]
    }
    assert feed_ids(client, "sort=new") == []


def test_an_agent_post_shows_its_name_and_label(client: TestClient) -> None:
    signup = client.post("auth/signup", json={"kind": "agent", "username": "Research-Bot"})
    assert signup.status_code == 201
    api_key = signup.json()["api_key"]

    response = client.post(
        "items", json={**STORY, "label": "nightly run"}, headers={"X-API-Key": api_key}
    )

    assert response.status_code == 201
    assert response.json()["username"] == "research-bot"
    assert response.json()["label"] == "nightly run"
