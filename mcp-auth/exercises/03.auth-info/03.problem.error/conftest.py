"""Fixtures for this exercise. Same three lines in every exercise."""

import pytest
from starlette.testclient import TestClient

from app import app

#: Brings in `token`, `other_token`, `make_token`, and the in-process auth server.
pytest_plugins = ["epicme.testing"]


@pytest.fixture(scope="session")
def client():
    # Session-scoped because starting the app starts the MCP session manager,
    # and that can only happen once per process.
    with TestClient(app) as test_client:
        yield test_client
