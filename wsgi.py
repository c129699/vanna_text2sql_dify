"""
WSGI 入口文件
用于 gunicorn 等生产级 WSGI 服务器启动应用

使用方法:
    # 启动统一应用（推荐，默认）
    gunicorn wsgi:app --bind 0.0.0.0:2523
    
    # 启动 API 应用
    APP_MODE=api gunicorn wsgi:app --bind 0.0.0.0:2523
    
    # 启动 Vanna Web UI
    APP_MODE=vanna gunicorn wsgi:app --bind 0.0.0.0:2523
"""
import os
import sys

# 修复 tokenizers 并行性警告（必须在导入其他库之前设置）
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')

# 添加当前目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from dependencies import DependencyContainer
from apps.unified_app import UnifiedApp
from apps.api_app import APIApp
from apps.vanna_app import VannaApp

# 从环境变量获取配置路径和应用模式
CONFIG_PATH = os.environ.get('CONFIG_PATH', 'config.yaml')
APP_MODE = os.environ.get('APP_MODE', 'unified').lower()  # unified, api, vanna

# 创建依赖容器
container = DependencyContainer(CONFIG_PATH)

# 根据模式创建并初始化应用
if APP_MODE == 'api':
    # API 应用模式
    app_instance = APIApp(container)
    app_instance.initialize()
    # APIApp 使用 api.routes.create_app 创建 Flask 应用
    from api.routes import create_app
    app = create_app(app_instance.vn)
    
elif APP_MODE == 'vanna':
    # Vanna Web UI 模式
    app_instance = VannaApp(container)
    app_instance.initialize()
    # 创建 Vanna Flask 应用
    from vanna.flask import VannaFlaskApp
    vanna_flask_app = VannaFlaskApp(app_instance.vn)
    # 尝试获取内部的 Flask 应用实例
    if hasattr(vanna_flask_app, 'app'):
        app = vanna_flask_app.app
    elif hasattr(vanna_flask_app, 'flask_app'):
        app = vanna_flask_app.flask_app
    else:
        # 如果 VannaFlaskApp 本身就是 Flask 应用
        from flask import Flask
        if isinstance(vanna_flask_app, Flask):
            app = vanna_flask_app
        else:
            app = vanna_flask_app
            
else:  # unified (默认)
    # 统一应用模式（同时提供 Web UI 和 API）
    app_instance = UnifiedApp(container)
    app_instance.initialize()
    unified_app = app_instance.create_unified_app()
    # 尝试获取内部的 Flask 应用实例
    if hasattr(unified_app, 'app'):
        app = unified_app.app
    elif hasattr(unified_app, 'flask_app'):
        app = unified_app.flask_app
    else:
        # 如果本身就是 Flask 应用
        from flask import Flask
        if isinstance(unified_app, Flask):
            app = unified_app
        else:
            app = unified_app

# 确保 app 已创建
if 'app' not in locals() or app is None:
    raise RuntimeError(f"无法创建 {APP_MODE} 应用实例，请检查应用初始化过程")

print(f"✓ WSGI 应用已初始化 ({APP_MODE} 模式)")
