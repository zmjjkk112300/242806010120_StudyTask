# StudyTask · AI 驱动的个人学习任务管理系统

《软件工程》实验一交付项目。单用户本地 Web 应用，用于记录课程作业、实验、考试准备等学习任务，支持任务增删改查、状态管理、组合筛选、逾期 / 即将到期提醒与基础统计。

## 一、技术栈

- 后端：Python 3.11+ / Flask 3
- 数据库：SQLite（本地文件，无需独立数据库服务）
- 前端：Jinja2 模板 + 原生 CSS（无前端框架）
- 测试：pytest + Flask 测试客户端

## 二、目录结构

```
StudyTask/
├── app/
│   ├── __init__.py        # Flask 应用工厂
│   ├── db.py             # SQLite 连接与建表
│   ├── service.py         # 校验与业务逻辑
│   ├── routes.py          # HTTP 路由
│   ├── templates/         # 页面模板
│   └── static/style.css  # 样式
├── tests/
│   ├── conftest.py        # 测试夹具（临时数据库）
│   └── test_tasks.py      # T1—T10 验收用例 + 校验边界测试
├── docs/
│   └── 验收表.md          # 需求验收记录（T1—T10）
├── instance/             # 运行时 SQLite 数据库（自动生成，已忽略）
├── run.py                # 启动入口
├── requirements.txt       # Python 依赖
├── pytest.ini
├── AI_DEV_LOG.md         # AI 协作过程记录
└── README.md
```

## 三、从零开始运行

### 1. 环境准备

- Python 3.11 或更高版本
- （建议）创建虚拟环境：

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. 安装依赖

```powershell
pip install -r requirements.txt
```

### 3. 启动应用

```powershell
python run.py
```

浏览器访问 <http://127.0.0.1:5000> 即可使用。数据库文件自动生成在 `instance/tasks.db`。

### 4. 运行自动化测试

```powershell
python -m pytest -q
```

预期输出：14 passed（覆盖验收用例 T1—T10 及输入校验边界）。

## 四、功能与需求对照

| 需求编号 | 功能 | 实现位置 |
| --- | --- | --- |
| FR-01 | 新建任务与必填 / 格式校验 | `service.validate`、`routes.new_task` |
| FR-02 | 列表展示名称、课程、截止日期、状态、优先级及详情页 | `templates/index.html`、`detail.html` |
| FR-03 | 修改任务字段，列表与详情一致 | `routes.edit_task`、`service.update_task` |
| FR-04 | 删除任务，二次确认后从数据库删除 | `routes.delete_task`、`templates/delete.html` |
| FR-05 | 状态在 待完成 / 进行中 / 已完成 间调整 | 编辑表单状态下拉框 |
| FR-06 | 按课程、状态、优先级组合筛选 | `routes.index`、`service.list_tasks` |
| FR-07 | 逾期、即将到期标记；已完成不提醒 | `service._decorate` |
| FR-08 | 总数、已完成数、完成率；空库完成率 0% | `service.get_stats`、`index.html` |
| FR-09 | 重启后数据保持不变 | SQLite 持久化，见 T10 测试 |
| FR-10 | 中文界面与错误提示，错误输入不崩溃 | 模板中文文案 + 校验异常处理 |

## 五、范围外（按 SRS 未实现）

用户注册、多用户权限、任务共享、邮件 / 短信推送、第三方日历同步、移动端 App、云登录。

## 六、部署说明

本项目为单用户本地应用，SRS（附录 A.4）不要求远程服务器。若课程要求提交公网 Web 地址，可任选一种方式部署，并在下方回填访问地址：

- 方式一：云服务器（如阿里云 / 腾讯云轻量服务器）安装 Python 与依赖，`gunicorn` 或 `python run.py` 启动，Nginx 反向代理 5000 端口。
- 方式二：PaaS 平台（Render / Railway / 国内云托管）导入仓库，启动命令 `python run.py`，指定端口由平台环境变量注入。

> 部署访问地址：**（提交前在此填写，例如 https://study-task.example.com）**
> 代码仓库地址：**（提交前在此填写 Gitee / GitHub / GitLab 链接）**

## 七、已知限制

- 单用户使用，无登录与会话隔离；
- 课程筛选为精确匹配，未做关键词模糊搜索；
- 统计仅包含总数、完成数与完成率，未提供图表。
