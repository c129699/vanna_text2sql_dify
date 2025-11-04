"""
依赖注入容器
负责管理所有组件的生命周期和依赖关系
"""
from typing import Dict, Any, Optional, Type
from config.loader import ConfigLoader
from core.llm.base import BaseLLMBackend
from core.llm.ollama import OllamaBackend
from core.llm.openai import OpenAIBackend
from core.llm.vllm import VLLMBackend


class DependencyContainer:
    """依赖注入容器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化依赖容器
        
        Args:
            config_path: 配置文件路径
        """
        self._config_loader: Optional[ConfigLoader] = None
        self._config_path = config_path
        
        # LLM 后端注册表
        self._llm_backends: Dict[str, Type[BaseLLMBackend]] = {
            'ollama': OllamaBackend,
            'openai': OpenAIBackend,
            'vllm': VLLMBackend,
        }
    
    @property
    def config_loader(self) -> ConfigLoader:
        """获取配置加载器（单例）"""
        if self._config_loader is None:
            self._config_loader = ConfigLoader(self._config_path)
        return self._config_loader
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self.config_loader.config
    
    def get_llm_backend(self) -> BaseLLMBackend:
        """
        获取 LLM 后端实例（工厂方法）
        
        Returns:
            LLM 后端实例
            
        Raises:
            ValueError: 不支持的 LLM 类型
        """
        config = self.get_config()
        llm_type = self.config_loader.get_llm_type()
        llm_config = self.config_loader.get_llm_config()
        
        # 添加 ChromaDB 持久化路径（如果配置中有）
        chroma_db_path = self.config_loader.get_chroma_db_path()
        if chroma_db_path:
            llm_config['chroma_db_path'] = chroma_db_path
        
        # 获取对应的 LLM 后端类
        llm_class = self._llm_backends.get(llm_type)
        if llm_class is None:
            raise ValueError(
                f"不支持的 LLM 类型: {llm_type}。"
                f"支持的类型: {', '.join(self._llm_backends.keys())}"
            )
        
        # 创建 LLM 后端实例
        return llm_class.create(llm_config)
    
    def register_llm_backend(self, name: str, backend_class: Type[BaseLLMBackend]):
        """
        注册新的 LLM 后端
        
        Args:
            name: 后端名称
            backend_class: 后端类（必须继承 BaseLLMBackend）
        """
        self._llm_backends[name] = backend_class


# 全局依赖容器实例（可以通过函数获取，便于测试）
_global_container: Optional[DependencyContainer] = None


def get_container(config_path: str = "config.yaml") -> DependencyContainer:
    """
    获取全局依赖容器实例（单例模式）
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        依赖容器实例
    """
    global _global_container
    if _global_container is None:
        _global_container = DependencyContainer(config_path)
    return _global_container


def reset_container():
    """重置全局容器（主要用于测试）"""
    global _global_container
    _global_container = None

