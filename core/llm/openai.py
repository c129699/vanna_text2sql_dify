"""
OpenAI 兼容 API LLM 后端实现
"""
from typing import Dict, Any, Optional, TYPE_CHECKING

# 尝试导入 OpenAI 相关依赖
try:
    from vanna.openai import OpenAI_Chat
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    OpenAI_Chat = None
    OpenAI = None
    HAS_OPENAI = False

if TYPE_CHECKING:
    from .base import BaseLLMBackend


if HAS_OPENAI:
    from .base import BaseLLMBackend
    
    class OpenAIBackend(BaseLLMBackend, OpenAI_Chat):
        """使用 OpenAI 兼容 API 的 LLM 后端"""
        
        def __init__(
            self,
            client: Optional[Any] = None,
            model: Optional[str] = None,
            config: Optional[Dict[str, Any]] = None
        ):
            """
            初始化 OpenAI 后端
            
            Args:
                client: OpenAI 客户端实例
                model: 模型名称
                config: 配置字典，包含：
                    - api_key: API 密钥
                    - api_base: API 基础地址
                    - allow_llm_to_see_data: 是否允许 LLM 查看数据
            """
            BaseLLMBackend.__init__(self, config=config)
            
            # OpenAI_Chat 需要 config 参数
            vanna_config = config or {}
            vanna_config['client'] = client
            if model:
                vanna_config['model'] = model
            
            OpenAI_Chat.__init__(self, config=vanna_config)
            
            # 确保 client 被设置为实例属性
            if client:
                self.client = client
            
            # 保存模型名称以便后续使用
            if model:
                self._model_name = model
        
        @classmethod
        def create(cls, config: Dict[str, Any]) -> 'OpenAIBackend':
            """
            创建 OpenAI LLM 后端实例
            
            Args:
                config: 模型配置字典，包含：
                    - api_key: API 密钥
                    - api_base: API 基础地址
                    - model: 模型名称
                    - allow_llm_to_see_data: 是否允许 LLM 查看数据
                    
            Returns:
                OpenAIBackend 实例
                
            Raises:
                ImportError: 缺少必要的依赖
            """
            # 获取配置
            api_key = config.get('api_key', 'EMPTY')
            api_base = config.get('api_base', 'http://localhost:8000/v1')
            model_name = config.get('model')
            
            # 创建 OpenAI 客户端
            openai_client = OpenAI(
                api_key=api_key,
                base_url=api_base
            )
            
            # 准备配置字典，保留 chroma_db_path 等配置
            vanna_config = {
                'allow_llm_to_see_data': config.get('allow_llm_to_see_data', True),
            }
            # 保留 chroma_db_path 配置（如果存在）
            if 'chroma_db_path' in config:
                vanna_config['chroma_db_path'] = config['chroma_db_path']
            
            # 创建实例
            instance = cls(
                client=openai_client,
                model=model_name,
                config=vanna_config
            )
            
            print(f"✓ 使用 OpenAI 兼容 API: {model_name} @ {api_base}")
            return instance
else:
    # 占位类
    class OpenAIBackend:
        """占位类，需要安装 vanna[openai]"""
        
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "需要安装 vanna[openai] 才能使用 OpenAI 兼容 API。"
                "运行: pip install vanna[openai]"
            )
        
        @classmethod
        def create(cls, config: Dict[str, Any]):
            raise ImportError(
                "需要安装 vanna[openai] 才能使用 OpenAI 兼容 API。"
                "运行: pip install vanna[openai]"
            )

