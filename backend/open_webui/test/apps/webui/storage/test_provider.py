import io
import os
import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock
from open_webui.storage import provider


def mock_upload_dir(monkeypatch, tmp_path):
    """Fixture to monkey-patch the UPLOAD_DIR and create a temporary directory."""
    directory = tmp_path / "uploads"
    directory.mkdir()
    monkeypatch.setattr(provider, "UPLOAD_DIR", str(directory))
    return directory


def test_imports():
    assert provider.StorageProvider
    assert provider.LocalStorageProvider
    assert provider.S3StorageProvider
    assert provider.GCSStorageProvider
    assert provider.AzureStorageProvider
    assert provider.Storage


def test_get_storage_provider(monkeypatch):
    Storage = provider.get_storage_provider("local")
    assert isinstance(Storage, provider.LocalStorageProvider)
    Storage = provider.get_storage_provider("s3")
    assert isinstance(Storage, provider.S3StorageProvider)

    # Mock GCS and Azure for testing since they require credentials
    with monkeypatch.context() as m:
        # Mock GCS client to avoid credential requirements
        mock_gcs_client = MagicMock()
        m.setattr("google.cloud.storage.Client", lambda: mock_gcs_client)
        Storage = provider.get_storage_provider("gcs")
        assert isinstance(Storage, provider.GCSStorageProvider)

    with monkeypatch.context() as m:
        # Mock Azure client to avoid credential requirements
        mock_azure_client = MagicMock()
        m.setattr(provider, "BlobServiceClient", lambda *a, **k: mock_azure_client)
        Storage = provider.get_storage_provider("azure")
        assert isinstance(Storage, provider.AzureStorageProvider)

    with pytest.raises(RuntimeError):
        provider.get_storage_provider("invalid")


def test_class_instantiation(monkeypatch):
    with pytest.raises(TypeError):
        provider.StorageProvider()
    with pytest.raises(TypeError):

        class Test(provider.StorageProvider):
            pass

        Test()
    provider.LocalStorageProvider()
    provider.S3StorageProvider()

    # Mock GCS and Azure to avoid credential requirements
    with monkeypatch.context() as m:
        mock_gcs_client = MagicMock()
        m.setattr("google.cloud.storage.Client", lambda: mock_gcs_client)
        provider.GCSStorageProvider()

    with monkeypatch.context() as m:
        mock_azure_client = MagicMock()
        m.setattr(provider, "BlobServiceClient", lambda *a, **k: mock_azure_client)
        provider.AzureStorageProvider()


class TestLocalStorageProvider:
    file_content = b"test content"
    file_bytesio = io.BytesIO(file_content)
    filename = "test.txt"
    filename_extra = "test_exyta.txt"
    file_bytesio_empty = io.BytesIO()

    def test_upload_file(self, monkeypatch, tmp_path):
        from open_webui.storage import provider

        upload_dir = mock_upload_dir(monkeypatch, tmp_path)
        storage = provider.LocalStorageProvider()
        contents, file_path = storage.upload_file(self.file_bytesio, self.filename, {})
        assert (upload_dir / self.filename).exists()
        assert (upload_dir / self.filename).read_bytes() == self.file_content
        assert contents == self.file_content
        assert file_path == str(upload_dir / self.filename)
        with pytest.raises(ValueError):
            storage.upload_file(self.file_bytesio_empty, self.filename, {})

    def test_get_file(self, monkeypatch, tmp_path):
        from open_webui.storage import provider

        upload_dir = mock_upload_dir(monkeypatch, tmp_path)
        file_path = str(upload_dir / self.filename)
        storage = provider.LocalStorageProvider()
        file_path_return = storage.get_file(file_path)
        assert file_path == file_path_return

    def test_delete_file(self, monkeypatch, tmp_path):
        from open_webui.storage import provider

        upload_dir = mock_upload_dir(monkeypatch, tmp_path)
        (upload_dir / self.filename).write_bytes(self.file_content)
        assert (upload_dir / self.filename).exists()
        file_path = str(upload_dir / self.filename)
        storage = provider.LocalStorageProvider()
        storage.delete_file(file_path)
        assert not (upload_dir / self.filename).exists()

    def test_delete_all_files(self, monkeypatch, tmp_path):
        from open_webui.storage import provider

        upload_dir = mock_upload_dir(monkeypatch, tmp_path)
        (upload_dir / self.filename).write_bytes(self.file_content)
        (upload_dir / self.filename_extra).write_bytes(self.file_content)
        storage = provider.LocalStorageProvider()
        storage.delete_all_files()
        assert not (upload_dir / self.filename).exists()
        assert not (upload_dir / self.filename_extra).exists()


def _s3_storage_with_fake(monkeypatch):
    from open_webui.storage import provider

    storage = provider.S3StorageProvider()
    storage.bucket_name = "my-bucket"
    store = {}

    class FakeS3:
        def __init__(self, s):
            self.store = s

        def upload_file(self, file_path, bucket, key):
            with open(file_path, "rb") as f:
                self.store[(bucket, key)] = f.read()

        def put_object_tagging(self, Bucket, Key, Tagging):
            return None

        def download_file(self, bucket, key, dest):
            data = self.store[(bucket, key)]
            with open(dest, "wb") as f:
                f.write(data)

        def delete_object(self, Bucket, Key):
            self.store.pop((Bucket, Key), None)

        def list_objects_v2(self, Bucket):
            return {"Contents": [{"Key": k[1]} for k in self.store.keys() if k[0] == Bucket]}

    storage.s3_client = FakeS3(store)
    return storage, store


def test_s3_upload_file(monkeypatch, tmp_path):
    Storage, _store = _s3_storage_with_fake(monkeypatch)
    file_content = b"test content"
    filename = "test.txt"
    filename_extra = "test_exyta.txt"
    file_bytesio_empty = io.BytesIO()
    upload_dir = mock_upload_dir(monkeypatch, tmp_path)
    contents, s3_file_path = Storage.upload_file(io.BytesIO(file_content), filename, {"k": "v"})
    assert _store[(Storage.bucket_name, filename)] == file_content
    assert (upload_dir / filename).exists()
    assert (upload_dir / filename).read_bytes() == file_content
    assert contents == file_content
    assert s3_file_path == "s3://" + Storage.bucket_name + "/" + filename
    with pytest.raises(ValueError):
        Storage.upload_file(file_bytesio_empty, filename, {})


def test_s3_get_and_delete(monkeypatch, tmp_path):
    Storage, _store = _s3_storage_with_fake(monkeypatch)
    file_content = b"test content"
    filename = "test.txt"
    upload_dir = mock_upload_dir(monkeypatch, tmp_path)
    contents, s3_file_path = Storage.upload_file(io.BytesIO(file_content), filename, {})
    file_path = Storage.get_file(s3_file_path)
    assert file_path == str(upload_dir / filename)
    assert (upload_dir / filename).exists()
    Storage.delete_file(s3_file_path)
    assert not (upload_dir / filename).exists()
    assert (Storage.bucket_name, filename) not in _store


def test_s3_delete_all(monkeypatch, tmp_path):
    Storage, _store = _s3_storage_with_fake(monkeypatch)
    file_content = b"test content"
    filename = "test.txt"
    filename_extra = "test_exyta.txt"
    upload_dir = mock_upload_dir(monkeypatch, tmp_path)
    Storage.upload_file(io.BytesIO(file_content), filename, {})
    assert _store[(Storage.bucket_name, filename)] == file_content
    assert (upload_dir / filename).exists()
    Storage.upload_file(io.BytesIO(file_content), filename_extra, {})
    assert _store[(Storage.bucket_name, filename_extra)] == file_content
    assert (upload_dir / filename_extra).exists()
    Storage.delete_all_files()
    assert not (upload_dir / filename).exists()
    assert (Storage.bucket_name, filename) not in _store
    assert not (upload_dir / filename_extra).exists()
    assert (Storage.bucket_name, filename_extra) not in _store

    def test_init_without_credentials(self, monkeypatch):
        monkeypatch.setattr(provider, "S3_ACCESS_KEY_ID", None)
        monkeypatch.setattr(provider, "S3_SECRET_ACCESS_KEY", None)
        storage = provider.S3StorageProvider()
        assert storage.s3_client is not None
        assert storage.bucket_name == provider.S3_BUCKET_NAME


def _gcs_storage_with_fake(monkeypatch):
    import sys
    import types
    import importlib

    # Install a fake open_webui.config to avoid importing DB during provider import
    fake_cfg = types.ModuleType("open_webui.config")
    # Minimal config values consumed by provider
    fake_cfg.GCS_BUCKET_NAME = "my-bucket"
    fake_cfg.GOOGLE_APPLICATION_CREDENTIALS_JSON = None
    fake_cfg.S3_BUCKET_NAME = "my-bucket"
    fake_cfg.S3_ACCESS_KEY_ID = None
    fake_cfg.S3_SECRET_ACCESS_KEY = None
    fake_cfg.S3_REGION_NAME = "us-east-1"
    fake_cfg.S3_ENDPOINT_URL = None
    fake_cfg.S3_KEY_PREFIX = ""
    fake_cfg.S3_USE_ACCELERATE_ENDPOINT = False
    fake_cfg.S3_ADDRESSING_STYLE = "auto"
    fake_cfg.S3_ENABLE_TAGGING = False
    fake_cfg.AZURE_STORAGE_ENDPOINT = "https://example.blob.core.windows.net"
    fake_cfg.AZURE_STORAGE_CONTAINER_NAME = "container"
    fake_cfg.AZURE_STORAGE_KEY = "key"
    fake_cfg.STORAGE_PROVIDER = "local"
    fake_cfg.UPLOAD_DIR = "/tmp"
    sys.modules["open_webui.config"] = fake_cfg
    sys.modules.pop("open_webui.storage.provider", None)
    from open_webui.storage import provider

    store = {}

    class FakeBucket:

        def __init__(self, s):
            self.store = s

        def blob(self, filename):
            return SimpleNamespace(upload_from_filename=lambda path: self._upload(filename, path))

        def _upload(self, filename, path):
            with open(path, "rb") as f:
                self.store[filename] = f.read()

        def get_blob(self, filename):
            if filename in self.store:
                return SimpleNamespace(
                    download_as_bytes=lambda: self.store[filename],
                    name=filename,
                    download_to_filename=lambda p: open(p, "wb").write(self.store[filename]),
                    delete=lambda: self.store.pop(filename, None),
                )
            return None

        def list_blobs(self):
            return [SimpleNamespace(name=k, delete=lambda k=k: self.store.pop(k, None)) for k in list(self.store.keys())]

        def delete_blob(self, name):
            self.store.pop(name, None)

    class FakeClient:

        def __init__(self, *a, **k):
            pass

        def bucket(self, name):
            return FakeBucket(store)

    import types as _types

    provider.storage = _types.SimpleNamespace(Client=FakeClient)
    storage_obj = provider.GCSStorageProvider()
    # Ensure bucket_name is set correctly
    storage_obj.bucket_name = "my-bucket"
    return storage_obj, store


def test_gcs_upload_get_delete(monkeypatch, tmp_path):
    Storage, store = _gcs_storage_with_fake(monkeypatch)
    file_content = b"test content"
    filename = "test.txt"
    upload_dir = mock_upload_dir(monkeypatch, tmp_path)
    contents, gcs_file_path = Storage.upload_file(io.BytesIO(file_content), filename, {})
    obj = Storage.bucket.get_blob(filename)
    assert file_content == obj.download_as_bytes()
    assert (upload_dir / filename).exists()
    assert contents == file_content
    assert gcs_file_path == f"gs://{Storage.bucket_name}/{filename}"
    # get_file
    path = Storage.get_file(gcs_file_path)
    assert os.path.basename(path) == filename
    # delete
    Storage.delete_file(gcs_file_path)
    assert Storage.bucket.get_blob(filename) is None


def test_gcs_delete_all(monkeypatch, tmp_path):
    Storage, store = _gcs_storage_with_fake(monkeypatch)
    file_content = b"test content"
    filename = "test.txt"
    filename_extra = "test2.txt"
    upload_dir = mock_upload_dir(monkeypatch, tmp_path)
    Storage.upload_file(io.BytesIO(file_content), filename, {})
    Storage.upload_file(io.BytesIO(file_content), filename_extra, {})
    Storage.delete_all_files()
    assert Storage.bucket.get_blob(filename) is None
    assert Storage.bucket.get_blob(filename_extra) is None
    assert not (upload_dir / filename).exists()
    assert not (upload_dir / filename_extra).exists()


def test_azure_flow(monkeypatch, tmp_path):
    import sys
    import types

    # Install a fake open_webui.config to avoid importing DB during provider import
    fake_cfg = types.ModuleType("open_webui.config")
    fake_cfg.GCS_BUCKET_NAME = "my-bucket"
    fake_cfg.GOOGLE_APPLICATION_CREDENTIALS_JSON = None
    fake_cfg.S3_BUCKET_NAME = "my-bucket"
    fake_cfg.S3_ACCESS_KEY_ID = None
    fake_cfg.S3_SECRET_ACCESS_KEY = None
    fake_cfg.S3_REGION_NAME = "us-east-1"
    fake_cfg.S3_ENDPOINT_URL = None
    fake_cfg.S3_KEY_PREFIX = ""
    fake_cfg.S3_USE_ACCELERATE_ENDPOINT = False
    fake_cfg.S3_ADDRESSING_STYLE = "auto"
    fake_cfg.S3_ENABLE_TAGGING = False
    fake_cfg.AZURE_STORAGE_ENDPOINT = "https://myaccount.blob.core.windows.net"
    fake_cfg.AZURE_STORAGE_CONTAINER_NAME = "my-container"
    fake_cfg.AZURE_STORAGE_KEY = "fake-key"
    fake_cfg.STORAGE_PROVIDER = "local"
    fake_cfg.UPLOAD_DIR = "/tmp"
    sys.modules["open_webui.config"] = fake_cfg
    sys.modules.pop("open_webui.storage.provider", None)
    from open_webui.storage import provider

    mock_blob_service_client = MagicMock()
    mock_container_client = MagicMock()
    mock_blob_client = MagicMock()
    mock_blob_service_client.get_container_client.return_value = mock_container_client
    mock_container_client.get_blob_client.return_value = mock_blob_client

    monkeypatch.setattr(provider, "BlobServiceClient", lambda *a, **k: mock_blob_service_client)

    Storage = provider.AzureStorageProvider()
    Storage.endpoint = "https://myaccount.blob.core.windows.net"
    Storage.container_name = "my-container"
    Storage.blob_service_client = mock_blob_service_client
    Storage.container_client = mock_container_client

    file_content = b"test content"
    filename = "test.txt"
    upload_dir = mock_upload_dir(monkeypatch, tmp_path)

    Storage.container_client.get_blob_client.side_effect = Exception("no container")
    with pytest.raises(Exception):
        Storage.upload_file(io.BytesIO(file_content), filename, {})
    Storage.container_client.get_blob_client.side_effect = None
    contents, url = Storage.upload_file(io.BytesIO(file_content), filename, {})
    assert contents == file_content
    assert url == f"https://myaccount.blob.core.windows.net/{Storage.container_name}/{filename}"
    assert (upload_dir / filename).exists()

    Storage.container_client.get_blob_client().download_blob().readall.return_value = file_content
    path = Storage.get_file(url)
    assert os.path.basename(path) == filename

    Storage.container_client.get_blob_client().delete_blob.return_value = None
    Storage.delete_file(url)
    assert not (upload_dir / filename).exists()

    Storage.container_client.list_blobs.return_value = [SimpleNamespace(name=filename)]
    Storage.delete_all_files()
