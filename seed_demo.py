"""可选：写入演示用样例任务（仅用于界面演示，不影响自动化测试）。

用法：python seed_demo.py
"""
from app import create_app
from app.db import get_db
from app.service import create_task

SAMPLES = [
    {"name": "链表实验报告", "course": "数据结构", "description": "完成单向链表增删查改与反转实验，附测试截图。",
     "due_at": "2026-11-14", "priority": "高", "status": "进行中"},
    {"name": "SQL 综合练习", "course": "数据库原理", "description": "完成多表连接、分组聚合与子查询练习。",
     "due_at": "2026-11-11", "priority": "高", "status": "待完成"},
    {"name": "用例建模作业", "course": "软件工程", "description": "绘制选课系统用例图并编写用例说明。",
     "due_at": "2026-11-13", "priority": "中", "status": "待完成"},
    {"name": "进程调度实验", "course": "操作系统", "description": "实现 FCFS 与时间片轮转调度模拟。",
     "due_at": "2026-11-20", "priority": "低", "status": "已完成"},
    {"name": "数据结构错题整理", "course": "数据结构", "description": "整理树与图章节错题，归纳解题思路。",
     "due_at": "2026-11-10", "priority": "中", "status": "待完成"},
    {"name": "英语单词背诵", "course": "大学英语", "description": "背诵六级词汇 List 3—4。",
     "due_at": "2026-11-16", "priority": "低", "status": "待完成"},
]

app = create_app()
with app.app_context():
    db = get_db()
    if db.execute("SELECT COUNT(*) n FROM tasks").fetchone()["n"] > 0:
        print("数据库已有任务，跳过写入。")
    else:
        for s in SAMPLES:
            create_task(s)
        print(f"已写入 {len(SAMPLES)} 条演示任务。")
