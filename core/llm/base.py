"""
LLM 后端基类
定义统一的接口
"""
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from vanna.chromadb import ChromaDB_VectorStore


class BaseLLMBackend(ChromaDB_VectorStore, ABC):
    """
    LLM 后端基类
    所有 LLM 后端实现都应该继承此类
    """
    
    @abstractmethod
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 LLM 后端
        
        Args:
            config: 配置字典，可以包含：
                - chroma_db_path: ChromaDB 持久化存储路径（可选）
        """
        # 确保 ChromaDB 使用持久化存储
        if config is None:
            config = {}
        
        # 如果没有指定 chroma_db_path，使用默认路径
        if 'chroma_db_path' not in config:
            # 使用项目根目录下的 data/chroma 目录作为默认存储路径
            # 从 core/llm/base.py 向上找到项目根目录
            current_file = os.path.abspath(__file__)
            # base.py -> llm -> core -> 项目根目录
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
            chroma_path = os.path.join(base_dir, 'data', 'chroma')
            # 确保目录存在
            os.makedirs(chroma_path, exist_ok=True)
            config['chroma_db_path'] = chroma_path
        
        ChromaDB_VectorStore.__init__(self, config=config)
    
    @classmethod
    @abstractmethod
    def create(cls, config: Dict[str, Any]) -> 'BaseLLMBackend':
        """
        创建 LLM 后端实例（工厂方法）
        
        Args:
            config: 配置字典
            
        Returns:
            LLM 后端实例
            
        Raises:
            NotImplementedError: 如果子类未实现此方法
        """
        raise NotImplementedError("子类必须实现 create 方法")

