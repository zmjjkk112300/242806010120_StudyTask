#!/usr/bin/env bash
# StudyTask 一键部署脚本（Ubuntu 22.04 / 24.04）
# 作用：装依赖 -> 部署代码到 /opt/studytask -> 写入演示数据 -> 用 systemd 常驻 80 端口
set -e

APP_DIR=/opt/studytask
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -f "$SRC/app/__init__.py" ]; then
  echo "错误：找不到项目源码（$SRC/app/__init__.py 不存在）"
  exit 1
fi

echo "== 1/6 安装系统依赖 =="
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip curl

echo "== 2/6 复制代码到 $APP_DIR =="
mkdir -p "$APP_DIR"
cp -a "$SRC"/. "$APP_DIR"/
mkdir -p "$APP_DIR/instance"

echo "== 3/6 创建虚拟环境并安装 Python 依赖 =="
cd "$APP_DIR"
if [ ! -x "$APP_DIR/.venv/bin/python" ]; then
  python3 -m venv "$APP_DIR/.venv"
fi
"$APP_DIR/.venv/bin/pip" install -q --upgrade pip
"$APP_DIR/.venv/bin/pip" install -q -i https://mirrors.aliyun.com/pypi/simple/ -r "$APP_DIR/requirements.txt"

echo "== 4/6 写入演示数据 =="
export STUDYTASK_DB="$APP_DIR/instance/tasks.db"
"$APP_DIR/.venv/bin/python" "$APP_DIR/seed_demo.py" || true

echo "== 5/6 配置 systemd 常驻服务 =="
cat > /etc/systemd/system/studytask.service <<'EOF'
[Unit]
Description=StudyTask Flask App
After=network.target

[Service]
User=root
WorkingDirectory=/opt/studytask
Environment=STUDYTASK_DB=/opt/studytask/instance/tasks.db
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/studytask/.venv/bin/gunicorn -w 2 -b 0.0.0.0:80 "app:create_app()"
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable studystask >/dev/null 2>&1
systemctl restart studystask
sleep 3

echo "== 6/6 自检与地址 =="
systemctl is-active studytask || true
curl -s -m 5 -o /dev/null -w "本机自检 HTTP 状态码=%{http_code}\n" http://127.0.0.1/ || echo "本机自检失败，请查看：journalctl -u studytask -n 30"

IP=$(curl -s -m 6 http://100.100.100.200/latest/meta-data/eipv4 2>/dev/null || echo "")
if [ -z "$IP" ]; then
  IP=$(curl -s -m 6 https://ifconfig.me 2>/dev/null || echo "未取到")
fi

echo ""
echo "=================================================="
echo " 公网 IP  ： $IP"
echo " 访问地址 ： http://$IP/"
echo " 服务管理 ： systemctl status|restart|stop studytask"
echo " 运行日志 ： journalctl -u studytask -f"
echo "=================================================="
echo ""
echo "如果浏览器打不开，是这个端口没放通：到阿里云控制台 -> 服务器实例 ->"
echo "防火墙 / 安全组 -> 添加规则 -> 允许 TCP 80 端口（来源 0.0.0.0/0）。"
