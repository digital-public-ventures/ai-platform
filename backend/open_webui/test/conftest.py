"""
Pytest configuration for backend/open_webui tests.

Goals:
- Ensure legacy Peewee migrations are no-ops during tests (they conflict with SQLAlchemy models).
- Provide sane, fast defaults for env so tests don't require Docker or external services.

Note: This file only affects tests and does not modify application code.
"""

import os
import sys
from pathlib import Path


def pytest_configure(config):
    # Prefer a throwaway SQLite database under the test folder unless tests override.
    base_dir = Path(__file__).resolve().parent
    tmp_dir = base_dir / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("DATA_DIR", str(tmp_dir))
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{tmp_dir / 'webui.db'}")

    # Disable legacy Peewee migrations by monkeypatching peewee_migrate.Router.run to a no-op
    # before open_webui.internal.db gets imported by the app/models.
    try:
        import peewee_migrate  # type: ignore

        class _NoopRouter:
            def __init__(self, *args, **kwargs):
                pass

            def run(self, *args, **kwargs):
                return []

        peewee_migrate.Router = _NoopRouter  # type: ignore[attr-defined]
    except Exception:
        # If the package is missing, there's nothing to patch.
        pass

    # Neutralize Alembic migrations during tests by providing a dummy alembic module
    # so open_webui.config.run_migrations() becomes a no-op at import time.
    try:
        import types

        alembic_mod = types.ModuleType("alembic")
        command_mod = types.ModuleType("alembic.command")

        def _upgrade(_cfg, _rev):
            # no-op during tests
            return None

        command_mod.upgrade = _upgrade  # type: ignore[attr-defined]

        config_mod = types.ModuleType("alembic.config")

        class _DummyConfig:
            def __init__(self, *args, **kwargs):
                self._opts = {}

            def set_main_option(self, key: str, value: str):
                self._opts[key] = value

        config_mod.Config = _DummyConfig  # type: ignore[attr-defined]

        sys.modules.setdefault("alembic", alembic_mod)
        sys.modules.setdefault("alembic.command", command_mod)
        sys.modules.setdefault("alembic.config", config_mod)
    except Exception:
        pass

    # Ensure minimal DB readiness for modules that read config at import-time.
    # Specifically, create a lightweight `config` table and seed a default row
    # to satisfy open_webui.config.get_config() without running Alembic.
    try:
        from sqlalchemy import text
        from open_webui.internal.db import engine

        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS config (
                        id INTEGER PRIMARY KEY,
                        data JSON NOT NULL,
                        version INTEGER NOT NULL,
                        created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                        updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP)
                    )
                    """
                )
            )

            # Seed default config if empty
            count = conn.execute(text("SELECT COUNT(*) FROM config")).scalar() or 0
            if count == 0:
                import json as _json

                default = {"version": 0, "ui": {}}
                conn.execute(
                    text(
                        "INSERT INTO config (id, data, version) VALUES (1, :data, :version)"
                    ),
                    {"data": _json.dumps(default), "version": 0},
                )
    except Exception:
        # If DB isn't reachable yet, tests importing app modules will establish it later.
        pass
