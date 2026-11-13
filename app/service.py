"""任务业务逻辑与输入校验（不依赖 Flask 路由，便于自动化测试）。"""
from datetime import date, datetime, timedelta

from flask import abort

from .db import get_db, now_str

PRIORITIES = ["高", "中", "低"]
STATUSES = ["待完成", "进行中", "已完成"]
DATE_FMT = "%Y-%m-%d"
UPCOMING_DAYS = 3  # 今日起未来 3 天内到期


class ValidationError(Exception):
    """输入校验失败，message 为面向用户的中文提示。"""


def _parse_date(value):
    return datetime.strptime(value.strip(), DATE_FMT).date()


def validate(name, course, description, due_at, priority, status):
    """校验全部字段，返回清洗后的字典；失败抛出 ValidationError。"""
    name = (name or "").strip()
    course = (course or "").strip()
    description = (description or "").strip()
    due_at = (due_at or "").strip()
    priority = (priority or "").strip()
    status = (status or "").strip()

    if not name:
        raise ValidationError("任务名称不能为空。")
    if len(name) > 100:
        raise ValidationError("任务名称不能超过 100 字。")
    if not course:
        raise ValidationError("所属课程不能为空。")
    if len(course) > 60:
        raise ValidationError("所属课程不能超过 60 字。")
    if len(description) > 1000:
        raise ValidationError("任务描述不能超过 1000 字。")
    if not due_at:
        raise ValidationError("截止日期不能为空。")
    try:
        _parse_date(due_at)
    except ValueError:
        raise ValidationError("截止日期格式不正确，应为 YYYY-MM-DD。")
    if priority not in PRIORITIES:
        raise ValidationError("优先级只能为 高 / 中 / 低。")
    if status not in STATUSES:
        raise ValidationError("状态只能为 待完成 / 进行中 / 已完成。")

    return {
        "name": name,
        "course": course,
        "description": description,
        "due_at": due_at,
        "priority": priority,
        "status": status,
    }


def _decorate(row):
    """为任务行补充逾期 / 即将到期标记。"""
    item = dict(row)
    today = date.today()
    due = _parse_date(item["due_at"])
    unfinished = item["status"] != "已完成"
    item["is_overdue"] = unfinished and due < today
    item["is_upcoming"] = unfinished and today <= due <= today + timedelta(days=UPCOMING_DAYS)
    return item


def list_tasks(course=None, status=None, priority=None):
    sql = "SELECT * FROM tasks WHERE 1=1"
    params = []
    if course:
        sql += " AND course = ?"
        params.append(course)
    if status:
        sql += " AND status = ?"
        params.append(status)
    if priority:
        sql += " AND priority = ?"
        params.append(priority)
    sql += " ORDER BY due_at ASC, id ASC"
    rows = get_db().execute(sql, params).fetchall()
    return [_decorate(r) for r in rows]


def get_task(task_id):
    row = get_db().execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        abort(404)
    return _decorate(row)


def create_task(data):
    clean = validate(**data)
    ts = now_str()
    db = get_db()
    cur = db.execute(
        """INSERT INTO tasks (name, course, description, due_at, priority, status, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (clean["name"], clean["course"], clean["description"], clean["due_at"],
         clean["priority"], clean["status"], ts, ts),
    )
    db.commit()
    return cur.lastrowid


def update_task(task_id, data):
    clean = validate(**data)
    ts = now_str()
    db = get_db()
    cur = db.execute(
        """UPDATE tasks SET name=?, course=?, description=?, due_at=?, priority=?,
           status=?, updated_at=? WHERE id=?""",
        (clean["name"], clean["course"], clean["description"], clean["due_at"],
         clean["priority"], clean["status"], ts, task_id),
    )
    db.commit()
    if cur.rowcount == 0:
        abort(404)
    return get_task(task_id)


def delete_task(task_id):
    db = get_db()
    cur = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    if cur.rowcount == 0:
        abort(404)


def get_stats():
    db = get_db()
    total = db.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()["n"]
    done = db.execute("SELECT COUNT(*) AS n FROM tasks WHERE status = '已完成'").fetchone()["n"]
    rate = round(done / total * 100) if total else 0
    return {"total": total, "done": done, "rate": rate}
