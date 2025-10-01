from types import SimpleNamespace
from fastapi import FastAPI
from fastapi.testclient import TestClient
from open_webui.test.util.mock_user import mock_user


def _app_with_models_router(monkeypatch):
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

    import open_webui.routers.models as models_router
    from open_webui.models import models as models_module

    # In-memory fake storage for models
    from types import SimpleNamespace
    store: dict[str, SimpleNamespace] = {}

    class FakeModels:
        def insert_new_model(self, form_data, user_id):
            data = SimpleNamespace(**{
                "id": form_data.id,
                "user_id": user_id,
                "base_model_id": form_data.base_model_id,
                "name": form_data.name,
                "params": form_data.params.model_dump() if hasattr(form_data.params, 'model_dump') else {},
                "meta": form_data.meta.model_dump() if hasattr(form_data.meta, 'model_dump') else {},
                "access_control": None,
                "is_active": True,
                "updated_at": 0,
                "created_at": 0,
            })
            store[data.id] = data
            return data

        def get_models_by_user_id(self, user_id: str, permission: str = "write"):
            return [{**vars(m), "user": None} for m in store.values() if m.user_id == user_id]

        def get_model_by_id(self, id: str):
            return store.get(id)

        def delete_model_by_id(self, id: str):
            return store.pop(id, None) is not None

    # Monkeypatch the Models table used by the router
    fake = FakeModels()
    monkeypatch.setattr(models_module, "Models", fake)
    monkeypatch.setattr(models_router, "Models", fake)

    app = FastAPI()
    app.include_router(models_router.router, prefix="/api/v1/models")
    # Minimal permissions config
    app.state.config = SimpleNamespace(USER_PERMISSIONS={})
    return app


def test_models_crud(monkeypatch):
    app = _app_with_models_router(monkeypatch)
    client = TestClient(app, headers={"Authorization": "Bearer test-token"})

    # Initially empty
    with mock_user(app, id="2"):
        r = client.get("/api/v1/models/")
    assert r.status_code == 200
    assert r.json() == []

    # Create (as admin to bypass permission checks)
    with mock_user(app, id="2", role="admin"):
        r = client.post(
            "/api/v1/models/create",
            json={
                "id": "my-model",
                "base_model_id": "base-model-id",
                "name": "Hello World",
                "meta": {"profile_image_url": "/static/favicon.png", "description": "description", "capabilities": None, "model_config": {}},
                "params": {},
            },
        )
    assert r.status_code == 200

    # List models for the user
    with mock_user(app, id="2"):
        r = client.get("/api/v1/models/")
    assert r.status_code == 200
    models = r.json()
    assert len(models) == 1 and models[0]["id"] == "my-model"

    # Get by id
    with mock_user(app, id="2"):
        r = client.get("/api/v1/models/model", params={"id": "my-model"})
    assert r.status_code == 200
    assert r.json()["id"] == "my-model"

    # Delete
    with mock_user(app, id="2"):
        r = client.delete("/api/v1/models/model/delete", params={"id": "my-model"})
    assert r.status_code == 200 and r.json() is True

    # Empty again
    with mock_user(app, id="2"):
        r = client.get("/api/v1/models/")
    assert r.status_code == 200 and r.json() == []
