import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure settings can initialize without a real Postgres instance
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test_db")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")


class _ScalarResultStub:
    def __init__(self, values):
        self._values = values

    def all(self):
        return list(self._values)


class ResultStub:
    def __init__(self, values):
        self._values = list(values)

    def scalars(self):
        return _ScalarResultStub(self._values)

    def scalar_one_or_none(self):
        return self._values[0] if self._values else None


@pytest.fixture
def mock_session():
    """AsyncSession stand‑in with the methods our services touch."""
    session = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def result_stub():
    def _factory(values):
        return ResultStub(values)

    return _factory

