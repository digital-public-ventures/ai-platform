from types import SimpleNamespace
from fastapi import FastAPI
from fastapi.testclient import TestClient
from open_webui.test.util.mock_user import mock_user


def _app_with_prompts_router(monkeypatch):
    # Hard-disable peewee migrations before importing the router
    try:
        import peewee_migrate

        class _NoopRouter:
            def __init__(self, *a, **k):
                pass

            def run(self, *a, **k):
                return []

        monkeypatch.setattr(peewee_migrate, "Router", _NoopRouter)
    except Exception:
        pass
    import open_webui.routers.prompts as prompts_router
    from open_webui.models import prompts as prompts_module

    from types import SimpleNamespace
    store: dict[str, SimpleNamespace] = {}

    class FakePrompts:
        def insert_new_prompt(self, user_id, form_data):
            data = SimpleNamespace(**{
                "command": form_data.command,
                "user_id": user_id,
                "title": form_data.title,
                "content": form_data.content,
                "timestamp": 0,
                "access_control": None,
            })
            store[data.command] = data
            return data

        def get_prompts_by_user_id(self, user_id: str, permission: str = "read"):
            return list(store.values())

        def get_prompts(self):
            return list(store.values())

        def get_prompt_by_command(self, command: str):
            return store.get(command)

        def update_prompt_by_command(self, command: str, form_data):
            if command in store:
                ns = store[command]
                ns.title = form_data.title
                ns.content = form_data.content
                return ns
            return None

        def delete_prompt_by_command(self, command: str):
            return store.pop(command, None) is not None

    fake = FakePrompts()
    monkeypatch.setattr(prompts_module, "Prompts", fake)
    # Also patch the reference used inside the router module
    monkeypatch.setattr(prompts_router, "Prompts", fake)

    app = FastAPI()
    app.include_router(prompts_router.router, prefix="/api/v1/prompts")
    app.state.config = SimpleNamespace(USER_PERMISSIONS={})
    return app


def test_prompts_crud(monkeypatch):
    app = _app_with_prompts_router(monkeypatch)
    client = TestClient(app, headers={"Authorization": "Bearer test-token"})

    with mock_user(app, id="2"):
        r = client.get("/api/v1/prompts/")
    assert r.status_code == 200 and r.json() == []

    with mock_user(app, id="2", role="admin"):
        r = client.post(
            "/api/v1/prompts/create",
            json={"command": "/my-command", "title": "Hello World", "content": "description"},
        )
    assert r.status_code == 200

    with mock_user(app, id="3", role="admin"):
        r = client.post(
            "/api/v1/prompts/create",
            json={"command": "/my-command2", "title": "Hello World 2", "content": "description 2"},
        )
    assert r.status_code == 200

    with mock_user(app, id="2"):
        r = client.get("/api/v1/prompts/")
    assert r.status_code == 200 and len(r.json()) == 2

    with mock_user(app, id="2"):
        r = client.get("/api/v1/prompts/command/my-command")
    assert r.status_code == 200 and r.json()["command"] == "/my-command"

    with mock_user(app, id="3"):
        r = client.post(
            "/api/v1/prompts/command/my-command2/update",
            json={"command": "ignored", "title": "Hello World Updated", "content": "description Updated"},
        )
    assert r.status_code == 200 and r.json()["title"] == "Hello World Updated"

    with mock_user(app, id="2"):
        r = client.get("/api/v1/prompts/command/my-command2")
    assert r.status_code == 200 and r.json()["title"] == "Hello World Updated"

    with mock_user(app, id="2"):
        r = client.delete("/api/v1/prompts/command/my-command/delete")
    assert r.status_code == 200

    with mock_user(app, id="2"):
        r = client.get("/api/v1/prompts/")
    assert r.status_code == 200 and len(r.json()) == 1
