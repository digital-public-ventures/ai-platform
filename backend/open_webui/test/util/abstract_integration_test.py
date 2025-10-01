import logging
import os
import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text


log = logging.getLogger(__name__)


def get_fast_api_client():
    from open_webui.main import app

    # Provide a default Authorization header so routes expecting a Bearer token don't
    # fall back to static index.html when tests omit it. The token value is a dummy;
    # dependency overrides in tests supply the user object. decode_token will return None,
    # which is tolerated by current route logic.
    return TestClient(app, headers={"Authorization": "Bearer test-token"})


class AbstractIntegrationTest:
    BASE_PATH = None

    def create_url(self, path="", query_params=None):
        if self.BASE_PATH is None:
            raise Exception("BASE_PATH is not set")
        parts = self.BASE_PATH.split("/")
        parts = [part.strip() for part in parts if part.strip() != ""]
        path_parts = path.split("/")
        path_parts = [part.strip() for part in path_parts if part.strip() != ""]
        query_parts = ""
        if query_params:
            query_parts = "&".join([f"{key}={value}" for key, value in query_params.items()])
            query_parts = f"?{query_parts}"
        url = "/".join(parts + path_parts)
        # Ensure trailing slash for base path root endpoints (FastAPI registers '/prefix/' when using '/')
        if not path_parts:
            url = url + "/"
        return url + query_parts

    @classmethod
    def setup_class(cls):
        pass

    def setup_method(self):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def teardown_method(self):
        pass


class AbstractPostgresTest(AbstractIntegrationTest):
    # Historically Postgres via Docker; for tests we default to fast local SQLite.

    @classmethod
    def _ensure_sqlite_db(cls) -> str:
        # Persist a test db under the test folder to avoid tmp cleanup races.
        from pathlib import Path

        base_dir = Path(__file__).resolve().parent.parent
        tmp_dir = base_dir / ".tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        db_path = tmp_dir / "webui.db"
        return f"sqlite:///{db_path}"

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # Use SQLite for tests by default
        try:
            database_url = os.environ.get("DATABASE_URL") or cls._ensure_sqlite_db()
            os.environ["DATABASE_URL"] = database_url

            # Import app/db and create SQLAlchemy tables for tests
            from open_webui.internal.db import Base, engine

            # Ensure models are imported so tables are registered with Base
            import open_webui.models.users  # noqa: F401
            import open_webui.models.chats  # noqa: F401
            import open_webui.models.prompts  # noqa: F401
            import open_webui.models.models  # noqa: F401
            import open_webui.models.auths  # noqa: F401

            Base.metadata.create_all(bind=engine)

            # FastAPI client after env is set
            cls.fast_api_client = get_fast_api_client()
        except Exception as ex:
            log.error(ex)
            cls.teardown_class()
            pytest.fail(f"Could not setup test environment: {ex}")

    def _check_db_connection(self):
        from open_webui.internal.db import Session

        retries = 10
        while retries > 0:
            try:
                Session.execute(text("SELECT 1"))
                Session.commit()
                break
            except Exception as e:
                Session.rollback()
                log.warning(e)
                time.sleep(3)
                retries -= 1

    def setup_method(self):
        super().setup_method()
        self._check_db_connection()

    @classmethod
    def teardown_class(cls) -> None:
        super().teardown_class()

    def teardown_method(self):
        from open_webui.internal.db import Session
        from sqlalchemy import inspect
        from sqlalchemy.engine import Connection
        from sqlalchemy.exc import SQLAlchemyError

        # rollback everything not yet committed
        Session.commit()

        # Dialect-aware cleanup of all application tables to ensure isolated tests.
        try:
            bind: Connection = Session.get_bind()  # type: ignore
            dialect_name = bind.dialect.name if bind else "unknown"
            inspector = inspect(bind)
            table_names = inspector.get_table_names()

            # Filter to only tables we own (heuristic: exclude alembic versioning if present later)
            # Keep explicit ordering for Postgres TRUNCATE CASCADE (order doesn't matter there) but
            # for DELETE we should delete child tables first if FK constraints exist; simplest is
            # to disable constraint checking for sqlite or rely on ON DELETE CASCADE; if issues arise
            # we can extend with foreign key introspection.

            if dialect_name == "postgresql":
                # Use single TRUNCATE with CASCADE for efficiency and to avoid FK ordering issues.
                if table_names:
                    tbl_list = ", ".join(f'"{t}"' if not t.startswith('"') else t for t in table_names)
                    Session.execute(text(f"TRUNCATE TABLE {tbl_list} CASCADE"))
            else:
                # Generic path (e.g., sqlite) – use DELETE FROM.
                for t in table_names:
                    Session.execute(text(f'DELETE FROM "{t}"'))
            Session.commit()
        except SQLAlchemyError as e:
            # Log and continue; failing to clean up should not hide the original test failure.
            log.warning(f"Test DB cleanup failed: {e}")
            Session.rollback()
