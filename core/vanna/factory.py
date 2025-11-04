"""
Vanna 实例工厂
负责创建和初始化 Vanna 实例
"""
from typing import Dict, Any
from core.llm.base import BaseLLMBackend
from dependencies import DependencyContainer


class VannaFactory:
    """Vanna 实例工厂"""
    
    def __init__(self, container: DependencyContainer):
        """
        初始化工厂
        
        Args:
            container: 依赖注入容器
        """
        self.container = container
    
    def create(self) -> BaseLLMBackend:
        """
        创建并初始化 Vanna 实例
        
        Returns:
            初始化好的 Vanna 实例（已连接数据库）
            
        Raises:
            ValueError: 不支持的 LLM 类型
        """
        # 获取 LLM 配置并添加 ChromaDB 路径
        llm_config = self.container.config_loader.get_llm_config()
        
        # 添加 ChromaDB 持久化路径（如果配置中有）
        chroma_db_path = self.container.config_loader.get_chroma_db_path()
        if chroma_db_path:
            llm_config['chroma_db_path'] = chroma_db_path
        
        # 获取 LLM 后端实例（这里需要重新创建，因为需要传递更新后的配置）
        # 由于 get_llm_backend 已经创建了实例，我们需要确保配置正确传递
        # 实际上，BaseLLMBackend.__init__ 会自动处理 chroma_db_path
        vn = self.container.get_llm_backend()
        
        # 连接数据库
        db_config = self.container.config_loader.get_database_config()
        print(
            f"正在连接数据库: {db_config['host']}:"
            f"{db_config['port']}/{db_config['dbname']}"
        )
        vn.connect_to_mysql(**db_config)
        print("✓ 数据库连接成功")
        
        return vn

