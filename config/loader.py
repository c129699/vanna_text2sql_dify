"""
配置加载模块
负责加载和管理配置文件
"""
import yaml
import os
from typing import Dict, Any, Optional


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self._config: Optional[Dict[str, Any]] = None
    
    def load(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML 解析错误
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if config is None:
            raise ValueError(f"配置文件为空: {self.config_path}")
        
        self._config = config
        return config
    
    @property
    def config(self) -> Dict[str, Any]:
        """获取配置（如果未加载则自动加载）"""
        if self._config is None:
            self.load()
        return self._config
    
    def get_llm_type(self) -> str:
        """获取 LLM 类型"""
        return self.config.get('llm_type', 'ollama').lower()
    
    def get_llm_config(self) -> Dict[str, Any]:
        """
        获取 LLM 配置
        
        Returns:
            LLM 配置字典
            
        Raises:
            ValueError: 不支持的 LLM 类型
        """
        llm_type = self.get_llm_type()
        
        if llm_type == 'ollama':
            return self.config.get('ollama', {})
        elif llm_type == 'openai':
            return self.config.get('openai', {})
        elif llm_type == 'vllm':
            return self.config.get('vllm', self.config.get('openai', {}))
        else:
            raise ValueError(
                f"不支持的 llm_type: {llm_type}，支持的类型: ollama, openai, vllm"
            )
    
    def get_database_config(self) -> Dict[str, str]:
        """获取数据库配置"""
        db_config = self.config.get('database', {})
        return {
            'host': db_config.get('host'),
            'port': db_config.get('port'),
            'dbname': db_config.get('dbname'),
            'user': db_config.get('user'),
            'password': db_config.get('password'),
        }
    
    def get_training_config(self) -> Dict[str, Any]:
        """获取训练配置"""
        return self.config.get('training', {})
    
    def get_flask_config(self) -> Dict[str, Any]:
        """获取 Flask 配置"""
        return self.config.get('flask', {})
    
    def get_chroma_db_path(self) -> Optional[str]:
        """
        获取 ChromaDB 持久化存储路径
        
        Returns:
            ChromaDB 路径，如果未配置则返回 None（使用默认路径）
        """
        return self.config.get('chroma_db_path')


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    便捷函数：加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    loader = ConfigLoader(config_path)
    return loader.load()

