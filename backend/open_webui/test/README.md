# Test Orchestration

This folder contains isolated test suites and helpers to run them reliably without loading unrelated pytest plugins or external services.

## Why plugin isolation?

Some global pytest plugins (asyncio, anyio, docker, langsmith, etc.) can alter event loop behavior or import timing and interfere with tests. We disable plugin autoload for this folder and opt in only to what each suite needs.

- Local config: `pytest.ini` in this folder sets `-p no:anyio -p no:asyncio -p no:docker -p no:langsmith` and filters noisy warnings.
- The runner also exports `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` for deterministic runs.

## Suites

- Unit: pure Python tests (util) + storage tests with pure in‑memory mocks. No external services.
- Integration: FastAPI router tests. Each builds a minimal app per module and uses in‑memory fakes; avoids DB migrations.

## Commands

Run from repo root (paths are relative):

- Unit: `backend/open_webui/test/run_tests.sh unit`
- Integration: `backend/open_webui/test/run_tests.sh integration`
- All: `backend/open_webui/test/run_tests.sh all`

These commands use this folder’s `pytest.ini` automatically (`-c backend/open_webui/test/pytest.ini`) and disable plugin autoload.

## Running subsets

- Util only: `pytest -c backend/open_webui/test/pytest.ini backend/open_webui/test/util -q`
- Storage (local + s3):
  `pytest -c backend/open_webui/test/pytest.ini -q \
backend/open_webui/test/apps/webui/storage/test_provider.py::TestLocalStorageProvider::test_upload_file \
backend/open_webui/test/apps/webui/storage/test_provider.py::TestLocalStorageProvider::test_get_file \
backend/open_webui/test/apps/webui/storage/test_provider.py::TestLocalStorageProvider::test_delete_file \
backend/open_webui/test/apps/webui/storage/test_provider.py::TestLocalStorageProvider::test_delete_all_files \
backend/open_webui/test/apps/webui/storage/test_provider.py::test_s3_upload_file \
backend/open_webui/test/apps/webui/storage/test_provider.py::test_s3_get_and_delete \
backend/open_webui/test/apps/webui/storage/test_provider.py::test_s3_delete_all`

- Storage (gcs + azure):
  `pytest -c backend/open_webui/test/pytest.ini -q \
backend/open_webui/test/apps/webui/storage/test_provider.py::test_gcs_upload_get_delete \
backend/open_webui/test/apps/webui/storage/test_provider.py::test_gcs_delete_all \
backend/open_webui/test/apps/webui/storage/test_provider.py::test_azure_flow`

## Notes

- Storage tests use pure mocks (no network/emulators). They monkeypatch provider clients and inject a minimal fake `open_webui.config` to avoid import‑time DB side effects.
- Router tests avoid importing the full app; they mount only the needed router with dependency overrides.
