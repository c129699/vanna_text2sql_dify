"""
统一应用
同时启动 Vanna Web UI 和 API 服务器，共享同一个端口
"""
from flask import Flask
from flask_cors import CORS
from dependencies import DependencyContainer
from core.vanna.factory import VannaFactory
from core.vanna.trainer import VannaTrainer
from vanna.flask import VannaFlaskApp


class UnifiedApp:
    """统一应用类，同时提供 Vanna Web UI 和 API 服务"""
    
    def __init__(self, container: DependencyContainer):
        """
        初始化应用
        
        Args:
            container: 依赖注入容器
        """
        self.container = container
        self.vn = None
    
    def initialize(self):
        """初始化 Vanna 实例并进行训练"""
        print("=" * 50)
        print("正在初始化统一应用...")
        print("=" * 50)
        
        # 创建 Vanna 实例
        factory = VannaFactory(self.container)
        self.vn = factory.create()
        
        # 进行训练
        config = self.container.get_config()
        trainer = VannaTrainer(self.vn, config)
        trainer.train_all()
        
        print("✓ 统一应用初始化完成")
        print("=" * 50)
    
    def create_unified_app(self):
        """
        创建统一的 Flask 应用，合并 Vanna Web UI 和 API 服务
        
        Returns:
            统一的 Flask 应用实例
        """
        # 创建 Vanna Flask 应用（用于 Web UI）
        vanna_app = VannaFlaskApp(self.vn)
        
        # 尝试获取内部的 Flask 应用实例
        # VannaFlaskApp 通常有一个 .app 属性包含实际的 Flask 应用
        flask_app = None
        if hasattr(vanna_app, 'app'):
            flask_app = vanna_app.app
        elif hasattr(vanna_app, 'flask_app'):
            flask_app = vanna_app.flask_app
        elif isinstance(vanna_app, Flask):
            flask_app = vanna_app
        
        # 如果找到了 Flask 应用，使用它；否则直接使用 vanna_app
        app = flask_app if flask_app is not None else vanna_app
        
        # 添加 CORS 支持（仅对 Flask 应用）
        if flask_app is not None and isinstance(flask_app, Flask):
            try:
                CORS(flask_app)  # 允许跨域请求
            except Exception as e:
                # 如果 CORS 初始化失败，继续执行
                print(f"警告: CORS 初始化失败，继续执行: {e}")
        
        # 创建 API 处理器
        from api.handlers import Text2SQLHandler
        handler = Text2SQLHandler(self.vn)
        
        # 创建 CORS 响应头函数（用于手动添加 CORS 头）
        def add_cors_headers(response):
            """手动添加 CORS 响应头"""
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        
        # 注册 API 路由到 Flask 应用
        # 使用唯一的 endpoint 名称，避免与 Vanna 路由冲突
        @app.route('/text2sql', methods=['POST', 'OPTIONS'])
        def text2sql():
            """将自然语言问题转换为 SQL 查询"""
            from flask import request, make_response
            if request.method == 'OPTIONS':
                response = make_response()
                return add_cors_headers(response)
            result = handler.text2sql()
            if isinstance(result, tuple) and len(result) == 2:
                response, status = result
                return add_cors_headers(response), status
            return add_cors_headers(result)
        
        @app.route('/query', methods=['POST', 'OPTIONS'])
        def query():
            """执行自然语言查询并返回结果"""
            from flask import request, make_response
            if request.method == 'OPTIONS':
                response = make_response()
                return add_cors_headers(response)
            result = handler.query()
            if isinstance(result, tuple) and len(result) == 2:
                response, status = result
                return add_cors_headers(response), status
            return add_cors_headers(result)
        
        @app.route('/health', methods=['GET'])
        def health():
            """健康检查接口"""
            from flask import jsonify
            response = jsonify({
                'status': 'healthy',
                'service': 'text2sql-api'
            })
            return add_cors_headers(response), 200
        
        @app.route('/openapi.yaml', methods=['GET'])
        def openapi_yaml():
            """返回 OpenAPI 规范文件（YAML格式）"""
            import os
            try:
                openapi_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    'openapi.yaml'
                )
                openapi_path = os.path.abspath(openapi_path)
                
                with open(openapi_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                from flask import make_response
                response = make_response(content)
                response.mimetype = 'text/yaml; charset=utf-8'
                return add_cors_headers(response), 200
            except FileNotFoundError:
                from flask import jsonify
                response = jsonify({
                    'error': 'OpenAPI 规范文件不存在',
                    'status': 'error'
                })
                return add_cors_headers(response), 404
        
        @app.route('/openapi.json', methods=['GET'])
        def openapi_json():
            """返回 OpenAPI 规范文件（JSON格式）"""
            import os
            import yaml
            from flask import jsonify
            try:
                openapi_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    'openapi.yaml'
                )
                openapi_path = os.path.abspath(openapi_path)
                
                with open(openapi_path, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                response = jsonify(content)
                return add_cors_headers(response), 200
            except FileNotFoundError:
                response = jsonify({
                    'error': 'OpenAPI 规范文件不存在',
                    'status': 'error'
                })
                return add_cors_headers(response), 404
        
        # 返回 VannaFlaskApp 实例（它应该会处理 run 方法）
        # 路由已经注册到内部的 Flask 应用
        return vanna_app
    
    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
        """
        运行统一的 Flask 应用
        
        Args:
            host: 主机地址
            port: 端口号
            debug: 是否开启调试模式
        """
        if self.vn is None:
            self.initialize()
        
        # 创建统一的 Flask 应用
        app = self.create_unified_app()
        
        print("=" * 50)
        print("统一应用启动中...")
        print(f"地址: http://{host}:{port}")
        print(f"Vanna Web UI: http://{host}:{port}/")
        print(f"API 接口: http://{host}:{port}/text2sql")
        print(f"API 文档: http://{host}:{port}/openapi.yaml")
        print("=" * 50)
        
        app.run(host=host, port=port, debug=debug)


def main(config_path: str = "config.yaml"):
    """
    主函数：启动统一应用
    
    Args:
        config_path: 配置文件路径
    """
    # 创建依赖容器
    container = DependencyContainer(config_path)
    
    # 创建并运行应用
    app = UnifiedApp(container)
    
    # 获取 Flask 配置
    flask_config = container.config_loader.get_flask_config()
    host = flask_config.get('host', '0.0.0.0')
    port = flask_config.get('port', 5000)
    debug = flask_config.get('debug', False)
    
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    import sys
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    main(config_path)

