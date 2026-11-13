"""SQLite 数据库连接与初始化。"""
import sqlite3
from datetime import datetime

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    course      TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT '',
    due_at      TEXT    NOT NULL,
    priority    TEXT    NOT NULL DEFAULT '中',
    status      TEXT    NOT NULL DEFAULT '待完成',
    created_at  TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL
);
"""


def get_db():
    """返回当前请求复用的数据库连接。"""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """创建数据表（若不存在）。"""
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
