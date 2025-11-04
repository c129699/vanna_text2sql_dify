"""
Vanna 应用
启动 Vanna 的 Web UI（使用 vanna.flask.VannaFlaskApp）
"""
from dependencies import DependencyContainer
from core.vanna.factory import VannaFactory
from core.vanna.trainer import VannaTrainer
from vanna.flask import VannaFlaskApp


class VannaApp:
    """Vanna 应用类"""
    
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
        print("正在初始化 Vanna 应用...")
        print("=" * 50)
        
        # 创建 Vanna 实例
        factory = VannaFactory(self.container)
        self.vn = factory.create()
        
        # 进行训练
        config = self.container.get_config()
        trainer = VannaTrainer(self.vn, config)
        trainer.train_all()
        
        print("✓ Vanna 应用初始化完成")
        print("=" * 50)
    
    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
        """
        运行 Vanna Flask 应用
        
        Args:
            host: 主机地址
            port: 端口号
            debug: 是否开启调试模式
        """
        if self.vn is None:
            self.initialize()
        
        # 创建 Vanna Flask 应用
        app = VannaFlaskApp(self.vn)
        
        print("=" * 50)
        print("Vanna Web UI 启动中...")
        print(f"地址: http://{host}:{port}")
        print("=" * 50)
        
        app.run(host=host, port=port, debug=debug)


def main(config_path: str = "config.yaml"):
    """
    主函数：启动 Vanna 应用
    
    Args:
        config_path: 配置文件路径
    """
    # 创建依赖容器
    container = DependencyContainer(config_path)
    
    # 创建并运行应用
    app = VannaApp(container)
    
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

