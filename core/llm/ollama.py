"""
Ollama LLM 后端实现
"""
from typing import Dict, Any, Optional
from vanna.ollama import Ollama
from .base import BaseLLMBackend


class OllamaBackend(BaseLLMBackend, Ollama):
    """使用 Ollama 的 LLM 后端"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 Ollama 后端
        
        Args:
            config: 配置字典，包含：
                - model: 模型名称
                - ollama_host: Ollama 服务地址
                - allow_llm_to_see_data: 是否允许 LLM 查看数据
        """
        BaseLLMBackend.__init__(self, config=config)
        Ollama.__init__(self, config=config)
    
    @classmethod
    def create(cls, config: Dict[str, Any]) -> 'OllamaBackend':
        """
        创建 Ollama LLM 后端实例
        
        Args:
            config: 模型配置字典
            
        Returns:
            OllamaBackend 实例
        """
        instance = cls(config=config)
        model = config.get('model', 'unknown')
        host = config.get('ollama_host', 'unknown')
        print(f"✓ 使用 Ollama: {model} @ {host}")
        return instance

