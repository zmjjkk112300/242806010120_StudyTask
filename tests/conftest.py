"""pytest 公共夹具：每个用例使用独立临时 SQLite 文件。"""
import os

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    os.environ["STUDYTASK_DB"] = str(tmp_path / "test.db")
    app = create_app()
    app.config["TESTING"] = True
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
