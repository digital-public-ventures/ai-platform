def test_import_models_router():
    import open_webui.routers.models as models_router
    assert hasattr(models_router, 'router')

