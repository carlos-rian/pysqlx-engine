import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


import pytest
from sqlx_engine import SQLXEngine


@pytest.fixture(scope="session")
def uri():
    return os.environ["DATABASE_URI"]


@pytest.fixture(scope="session")
async def db(uri):
    _db = SQLXEngine(provider="sqlite", uri=uri)
    await _db.connect()
    return _db
