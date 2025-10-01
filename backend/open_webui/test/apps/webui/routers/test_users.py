from types import SimpleNamespace
from fastapi import FastAPI
from fastapi.testclient import TestClient
from open_webui.test.util.mock_user import mock_user


def _app_with_users_router(monkeypatch):
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
    import open_webui.routers.users as users_router
    from open_webui.models import users as users_module
    from open_webui.models import auths as auths_module

    store = {}

    class FakeUsers:
        def insert_new_user(self, id, name, email, profile_image_url="/user.png", role="pending", oauth_sub=None):
            data = {
                "id": id,
                "name": name,
                "email": email,
                "role": role,
                "profile_image_url": profile_image_url,
                "last_active_at": 0,
                "updated_at": 0,
                "created_at": 0,
                "info": None,
                "settings": None,
            }
            store[id] = data
            return data

        def get_users(self, filter=None, skip=None, limit=None):
            return {"users": list(store.values()), "total": len(store)}

        def get_user_by_id(self, id):
            return SimpleNamespace(**store.get(id)) if id in store else None

        def get_user_by_email(self, email):
            for u in store.values():
                if u["email"].lower() == email.lower():
                    return SimpleNamespace(**u)
            return None

        def update_user_by_id(self, id, updated: dict):
            if id in store:
                store[id].update(updated)
                return SimpleNamespace(**store[id])
            return None

        def update_user_settings_by_id(self, id, updated: dict):
            if id in store:
                existing = store[id].get("settings") or {}
                existing.update(updated)
                store[id]["settings"] = existing
                return SimpleNamespace(**store[id])

        def delete_user_by_id(self, id):
            return store.pop(id, None) is not None

        def get_first_user(self):
            if store:
                first = next(iter(store.values()))
                return SimpleNamespace(**first)
            return None

    fake = FakeUsers()
    monkeypatch.setattr(users_module, "Users", fake)
    monkeypatch.setattr(users_router, "Users", fake)
    # Bridge delete via Auths -> Users to avoid DB usage in router
    monkeypatch.setattr(
        auths_module.Auths,
        "delete_auth_by_id",
        staticmethod(lambda user_id: fake.delete_user_by_id(user_id)),
    )

    app = FastAPI()
    app.include_router(users_router.router, prefix="/api/v1/users")
    app.state.config = SimpleNamespace(USER_PERMISSIONS={})
    return app


def _get_user_by_id(data, param):
    return next((item for item in data if item["id"] == param), None)


def _assert_user(data, id, **kwargs):
    user = _get_user_by_id(data, id)
    assert user is not None
    comparison_data = {
        "name": f"user {id}",
        "email": f"user{id}@openwebui.com",
        "profile_image_url": f"/user{id}.png",
        "role": "user",
        **kwargs,
    }
    for key, value in comparison_data.items():
        assert user[key] == value


def test_users_flow(monkeypatch):
    app = _app_with_users_router(monkeypatch)
    client = TestClient(app, headers={"Authorization": "Bearer test-token"})

    # Seed two users directly via fake table
    from open_webui.models import users as users_module
    users_module.Users.insert_new_user(id="1", name="user 1", email="user1@openwebui.com", profile_image_url="/user1.png", role="user")
    users_module.Users.insert_new_user(id="2", name="user 2", email="user2@openwebui.com", profile_image_url="/user2.png", role="user")

    # Admin lists users
    with mock_user(app, id="3", role="admin"):
        r = client.get("/api/v1/users/")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    _assert_user(body["users"], "1")
    _assert_user(body["users"], "2")

    # Update role via admin update endpoint
    with mock_user(app, id="3", role="admin"):
        r = client.post(
            "/api/v1/users/2/update",
            json={"role": "admin", "name": "user 2", "email": "user2@openwebui.com", "profile_image_url": "/user2.png"},
        )
    assert r.status_code == 200 and r.json()["role"] == "admin"

    # User settings
    with mock_user(app, id="2"):
        r = client.get("/api/v1/users/user/settings")
    assert r.status_code == 200 and r.json() is None

    with mock_user(app, id="2"):
        r = client.post(
            "/api/v1/users/user/settings/update",
            json={"ui": {"attr1": "value1", "attr2": "value2"}, "model_config": {"attr3": "value3", "attr4": "value4"}},
        )
    assert r.status_code == 200

    with mock_user(app, id="2"):
        r = client.get("/api/v1/users/user/settings")
    assert r.status_code == 200 and r.json() == {"ui": {"attr1": "value1", "attr2": "value2"}, "model_config": {"attr3": "value3", "attr4": "value4"}}

    # User info
    with mock_user(app, id="1"):
        r = client.get("/api/v1/users/user/info")
    assert r.status_code == 200 and r.json() is None

    with mock_user(app, id="1"):
        r = client.post("/api/v1/users/user/info/update", json={"attr1": "value1", "attr2": "value2"})
    assert r.status_code == 200

    with mock_user(app, id="1"):
        r = client.get("/api/v1/users/user/info")
    assert r.status_code == 200 and r.json() == {"attr1": "value1", "attr2": "value2"}

    # Get user by id
    with mock_user(app, id="1"):
        r = client.get("/api/v1/users/2")
    assert r.status_code == 200 and r.json()["name"] == "user 2"

    # Delete user by id (admin)
    with mock_user(app, id="3", role="admin"):
        r = client.delete("/api/v1/users/2")
    assert r.status_code == 200

    with mock_user(app, id="3", role="admin"):
        r = client.get("/api/v1/users/")
    assert r.status_code == 200 and r.json()["total"] == 1
