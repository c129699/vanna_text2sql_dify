"""
V2 重构版本主入口
支持启动两种应用：
1. vanna_app: Vanna Web UI
2. api_app: API 服务器（供 Dify 调用）
"""
import sys
import os
import argparse

# 添加当前目录到 Python 路径，确保可以导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from apps.vanna_app import VannaApp
from apps.api_app import APIApp
from dependencies import DependencyContainer


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Vanna Text-to-SQL V2 重构版本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动 API 服务器（默认）
  python main.py
  
  # 启动 Vanna Web UI
  python main.py vanna
  
  # 启动 API 服务器（显式指定）
  python main.py api
  
  # 使用自定义配置文件
  python main.py --config custom_config.yaml
  python main.py vanna --config custom_config.yaml
        """
    )
    
    parser.add_argument(
        'app',
        nargs='?',
        choices=['vanna', 'api'],
        default='api',
        help='要启动的应用类型：vanna (Web UI) 或 api (API 服务器，默认)'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='配置文件路径（默认: config.yaml）'
    )
    
    parser.add_argument(
        '--host',
        help='服务器主机地址（覆盖配置文件中的设置）'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        help='服务器端口号（覆盖配置文件中的设置）'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='开启调试模式（覆盖配置文件中的设置）'
    )
    
    args = parser.parse_args()
    
    # 创建依赖容器
    container = DependencyContainer(args.config)
    
    # 获取 Flask 配置
    flask_config = container.config_loader.get_flask_config()
    
    # 应用命令行参数覆盖配置
    host = args.host or flask_config.get('host', '0.0.0.0')
    port = args.port or flask_config.get('port', 5000)
    debug = args.debug if args.debug else flask_config.get('debug', False)
    
    # 根据应用类型启动相应的应用
    if args.app == 'vanna':
        app = VannaApp(container)
        app.run(host=host, port=port, debug=debug)
    elif args.app == 'api':
        app = APIApp(container)
        app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()

