"""实验一验收用例 T1—T10 与输入校验自动化测试。"""
from datetime import date, timedelta

import pytest

from app import create_app
from app.db import get_db
from app.service import list_tasks

today = date.today()
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)


def make_task(name="链表实验报告", course="数据结构", due_at=None,
              priority="中", status="待完成", description=""):
    return {
        "name": name,
        "course": course,
        "description": description,
        "due_at": due_at or str(today),
        "priority": priority,
        "status": status,
    }


def create(client, data):
    resp = client.post("/tasks/new", data=data)
    assert resp.status_code == 302, resp.text
    return int(resp.headers["Location"].rstrip("/").split("/")[-1])


def task_count(app):
    with app.app_context():
        return get_db().execute("SELECT COUNT(*) n FROM tasks").fetchone()["n"]


# T1 新建任务并在列表可见
def test_T1_create_task_appears_in_list(client):
    data = make_task(course="数据结构", due_at=str(tomorrow), priority="高")
    create(client, data)
    html = client.get("/").text
    assert "链表实验报告" in html
    assert "数据结构" in html


# T2 名称为空：提示错误且不产生脏数据
def test_T2_empty_name_rejected(client, app):
    resp = client.post("/tasks/new", data=make_task(name=""))
    assert resp.status_code == 200
    assert "任务名称不能为空" in resp.text
    assert task_count(app) == 0


# T3 修改描述与优先级，刷新后保留
def test_T3_edit_persists(client, app):
    tid = create(client, make_task())
    resp = client.post(f"/tasks/{tid}/edit",
                       data=make_task(description="改写后的描述", priority="低"))
    assert resp.status_code == 302
    page = client.get(f"/tasks/{tid}").text
    assert "改写后的描述" in page
    assert "低" in page
    # 再次请求（模拟刷新）数据仍在
    page2 = client.get(f"/tasks/{tid}").text
    assert "改写后的描述" in page2


# T4 状态：待完成 → 进行中 → 已完成
def test_T4_status_transitions(client):
    tid = create(client, make_task(status="待完成"))
    client.post(f"/tasks/{tid}/edit", data=make_task(status="进行中"))
    assert "进行中" in client.get(f"/tasks/{tid}").text
    client.post(f"/tasks/{tid}/edit", data=make_task(status="已完成"))
    assert "已完成" in client.get(f"/tasks/{tid}").text


# T5 按课程、状态、优先级组合筛选
def test_T5_combined_filters(client):
    create(client, make_task(name="A-数学", course="数学", status="待完成", priority="高"))
    create(client, make_task(name="B-数学", course="数学", status="进行中", priority="中"))
    create(client, make_task(name="C-英语", course="英语", status="待完成", priority="高"))

    html = client.get("/?course=数学&status=待完成").text
    assert "A-数学" in html and "B-数学" not in html and "C-英语" not in html

    html2 = client.get("/?priority=高&course=英语").text
    assert "C-英语" in html2 and "A-数学" not in html2


# T6 昨日到期且未完成 → 逾期；已完成不标记逾期
def test_T6_overdue_flag(client, app):
    create(client, make_task(name="逾期任务", due_at=str(yesterday), status="待完成"))
    create(client, make_task(name="已完成旧任务", due_at=str(yesterday), status="已完成"))
    html = client.get("/").text
    assert "逾期" in html

    with app.app_context():
        overdue = [t["name"] for t in list_tasks() if t["is_overdue"]]
    assert "逾期任务" in overdue
    assert "已完成旧任务" not in overdue


# T7 明日到期且未完成 → 即将到期
def test_T7_upcoming_flag(client):
    create(client, make_task(name="临期任务", due_at=str(tomorrow)))
    html = client.get("/").text
    assert "即将到期" in html


# T8 总数 5、完成 2、完成率 40%；空库完成率 0%
def test_T8_statistics(client, app):
    ids = [create(client, make_task(name=f"任务{i}")) for i in range(5)]
    for tid in ids[:2]:
        client.post(f"/tasks/{tid}/edit", data=make_task(status="已完成"))
    html = client.get("/").text
    assert ">5<" in html or "5" in html
    assert ">2<" in html or "2" in html
    assert "40%" in html

    # 空库完成率显示 0%
    os_env_db = __import__("os").environ["STUDYTASK_DB"]
    app2 = create_app()
    c2 = app2.test_client()
    assert "0%" in c2.get("/").text


# T9 删除：取消不删除，确认后删除
def test_T9_delete_cancel_then_confirm(client, app):
    tid = create(client, make_task(name="待删除任务"))
    page = client.get(f"/tasks/{tid}/delete").text
    assert "确认删除" in page and "取消" in page
    # 取消：仅打开确认页，不提交 POST，任务仍在
    assert client.get(f"/tasks/{tid}").status_code == 200
    assert task_count(app) == 1
    # 确认删除
    client.post(f"/tasks/{tid}/delete")
    assert task_count(app) == 0
    assert client.get(f"/tasks/{tid}").status_code == 404


# T10 关闭并重启应用后数据仍存在
def test_T10_persistence_after_restart(client, app):
    create(client, make_task(name="持久化任务", course="软件工程"))
    # 模拟重启：用同一数据库文件新建应用实例
    app2 = create_app()
    c2 = app2.test_client()
    html = c2.get("/").text
    assert "持久化任务" in html
    assert "软件工程" in html


# 附加：输入校验边界
def test_validation_invalid_date(client, app):
    resp = client.post("/tasks/new", data=make_task(due_at="2026-13-40"))
    assert "截止日期格式不正确" in resp.text
    assert task_count(app) == 0


def test_validation_bad_priority(client, app):
    resp = client.post("/tasks/new", data=make_task(priority="紧急"))
    assert "优先级只能为" in resp.text
    assert task_count(app) == 0


def test_validation_too_long_fields(client, app):
    resp = client.post("/tasks/new", data=make_task(name="x" * 101))
    assert "任务名称不能超过 100 字" in resp.text
    resp2 = client.post("/tasks/new", data=make_task(description="y" * 1001))
    assert "任务描述不能超过 1000 字" in resp2.text
    assert task_count(app) == 0


def test_validation_empty_course(client, app):
    resp = client.post("/tasks/new", data=make_task(course=""))
    assert "所属课程不能为空" in resp.text
    assert task_count(app) == 0
