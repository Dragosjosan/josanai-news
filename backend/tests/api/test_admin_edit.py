import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

STORY = {
    "title": "Agent SDK 1.0 ships",
    "url": "https://example.com/agent-sdk",
    "summary": "Useful for wayCP and wayRTS integrations.",
}


def api_key(client: TestClient, username: str, *, admin: bool = False) -> str:
    signup = client.post("auth/signup", json={"kind": "agent", "username": username})
    assert signup.status_code == 201
    if admin:
        url = str(client.app.state.settings.database_url)  # type: ignore[attr-defined]
        with create_engine(url).begin() as connection:
            connection.execute(
                text("UPDATE accounts SET role = 'admin' WHERE username = :name"),
                {"name": username},
            )
    return str(signup.json()["api_key"])


@pytest.fixture
def admin_headers(client: TestClient) -> dict[str, str]:
    return {"X-API-Key": api_key(client, "site-admin", admin=True)}


def test_an_admin_edits_a_summary_and_the_post_is_marked_edited(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    item = client.post("items", json=STORY).json()
    assert item["edited_at"] is None

    response = client.patch(
        f"items/{item['id']}",
        json={"summary": "Useful for supply chain integrations."},
        headers=admin_headers,
    )

    assert response.status_code == 200
    edited = response.json()
    assert edited["summary"] == "Useful for supply chain integrations."
    assert edited["title"] == STORY["title"]
    assert edited["edited_at"] is not None
    page = client.get(f"items/{item['id']}").json()
    assert page["summary"] == "Useful for supply chain integrations."
    assert page["edited_at"] == edited["edited_at"]
    feed = client.get("items?sort=new").json()["items"]
    assert feed[0]["edited_at"] == edited["edited_at"]


def test_an_admin_can_change_the_title_or_remove_the_summary(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    item_id = client.post("items", json=STORY).json()["id"]

    response = client.patch(
        f"items/{item_id}",
        json={"title": "  Agent SDK  1.0 ", "summary": " "},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Agent SDK 1.0"
    assert response.json()["summary"] is None


def test_an_edit_that_changes_nothing_is_not_marked_edited(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    item_id = client.post("items", json=STORY).json()["id"]

    response = client.patch(
        f"items/{item_id}", json={"summary": STORY["summary"]}, headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["edited_at"] is None


def test_the_search_index_follows_an_edited_summary(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    item_id = client.post("items", json=STORY).json()["id"]
    client.patch(f"items/{item_id}", json={"summary": "Plain words."}, headers=admin_headers)

    url = str(client.app.state.settings.database_url)  # type: ignore[attr-defined]
    with create_engine(url).connect() as connection:
        old = connection.execute(text("SELECT rowid FROM items_fts WHERE items_fts MATCH 'wayCP'"))
        new = connection.execute(text("SELECT rowid FROM items_fts WHERE items_fts MATCH 'plain'"))
        assert old.all() == []
        assert [row[0] for row in new] == [item_id]


@pytest.mark.parametrize(
    "body",
    [{}, {"title": None}, {"title": ""}, {"url": "https://example.com/other"}],
)
def test_an_invalid_edit_is_refused(
    client: TestClient, admin_headers: dict[str, str], body: dict[str, object]
) -> None:
    item_id = client.post("items", json=STORY).json()["id"]

    response = client.patch(f"items/{item_id}", json=body, headers=admin_headers)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_only_an_admin_can_edit(client: TestClient) -> None:
    item_id = client.post("items", json=STORY).json()["id"]
    body = {"summary": "Changed."}

    anonymous = client.patch(f"items/{item_id}", json=body)
    agent = client.patch(
        f"items/{item_id}", json=body, headers={"X-API-Key": api_key(client, "plain-agent")}
    )

    assert anonymous.status_code == 401
    assert agent.status_code == 403
    assert client.get(f"items/{item_id}").json()["summary"] == STORY["summary"]


def test_a_deleted_or_missing_story_cannot_be_edited(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    item_id = client.post("items", json=STORY).json()["id"]
    client.delete(f"items/{item_id}", headers=admin_headers)

    for target in (item_id, 999):
        response = client.patch(f"items/{target}", json={"summary": "x"}, headers=admin_headers)
        assert response.status_code == 404
