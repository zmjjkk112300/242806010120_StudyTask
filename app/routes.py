"""HTTP 路由：任务增删改查、筛选、统计。"""
from flask import (Blueprint, flash, redirect, render_template, request, url_for)

from . import service
from .service import ValidationError

bp = Blueprint("tasks", __name__)


def _form_data():
    return {
        "name": request.form.get("name", ""),
        "course": request.form.get("course", ""),
        "description": request.form.get("description", ""),
        "due_at": request.form.get("due_at", ""),
        "priority": request.form.get("priority", "中"),
        "status": request.form.get("status", "待完成"),
    }


@bp.route("/")
def index():
    course = request.args.get("course", "").strip()
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()
    tasks = service.list_tasks(course or None, status or None, priority or None)
    stats = service.get_stats()
    return render_template(
        "index.html", tasks=tasks, stats=stats,
        filters={"course": course, "status": status, "priority": priority},
        priorities=service.PRIORITIES, statuses=service.STATUSES,
    )


@bp.route("/tasks/new", methods=["GET", "POST"])
def new_task():
    if request.method == "POST":
        data = _form_data()
        try:
            task_id = service.create_task(data)
            flash("任务创建成功。", "success")
            return redirect(url_for("tasks.detail", task_id=task_id))
        except ValidationError as exc:
            flash(str(exc), "error")
            return render_template("form.html", mode="new", values=data,
                                   priorities=service.PRIORITIES, statuses=service.STATUSES)
    return render_template("form.html", mode="new", values={},
                           priorities=service.PRIORITIES, statuses=service.STATUSES)


@bp.route("/tasks/<int:task_id>")
def detail(task_id):
    task = service.get_task(task_id)
    return render_template("detail.html", task=task)


@bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    task = service.get_task(task_id)
    if request.method == "POST":
        data = _form_data()
        try:
            service.update_task(task_id, data)
            flash("任务修改成功。", "success")
            return redirect(url_for("tasks.detail", task_id=task_id))
        except ValidationError as exc:
            flash(str(exc), "error")
            return render_template("form.html", mode="edit", values=data, task_id=task_id,
                                   priorities=service.PRIORITIES, statuses=service.STATUSES)
    return render_template("form.html", mode="edit", values=task, task_id=task_id,
                           priorities=service.PRIORITIES, statuses=service.STATUSES)


@bp.route("/tasks/<int:task_id>/delete", methods=["GET", "POST"])
def delete_task(task_id):
    task = service.get_task(task_id)
    if request.method == "POST":
        service.delete_task(task_id)
        flash("任务已删除。", "success")
        return redirect(url_for("tasks.index"))
    return render_template("delete.html", task=task)
