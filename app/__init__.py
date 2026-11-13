"""Flask 应用工厂。"""
import os

from flask import Flask

from . import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    instance_dir = app.instance_path
    os.makedirs(instance_dir, exist_ok=True)

    app.config.from_mapping(
        DATABASE=os.environ.get("STUDYTASK_DB") or os.path.join(instance_dir, "tasks.db"),
        SECRET_KEY=os.environ.get("SECRET_KEY", "study-task-local-dev"),
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from . import routes
    app.register_blueprint(routes.bp)

    return app
