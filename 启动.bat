@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo  StudyTask 个人学习任务管理系统 启动脚本
echo ========================================
echo.
echo [1/3] 检查并安装依赖...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo 依赖安装失败：请确认已安装 Python 3.11 以上，并已勾选 Add Python to PATH。
    pause
    exit /b 1
)
echo.
echo [2/3] 写入演示数据（数据库非空时自动跳过）...
python seed_demo.py
echo.
echo [3/3] 启动服务，稍后浏览器访问 http://127.0.0.1:5000
echo 关闭本窗口即可停止服务。
echo.
python run.py
pause
