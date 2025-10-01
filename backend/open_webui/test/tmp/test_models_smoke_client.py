from types import SimpleNamespace
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_construct_models_app_and_client():
    import open_webui.routers.models as models_router
    app = FastAPI()
    app.include_router(models_router.router, prefix="/api/v1/models")
    app.state.config = SimpleNamespace(USER_PERMISSIONS={})
    client = TestClient(app)
    assert client is not None

