"""
Flask API 路由定义
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os
import yaml
from typing import Optional, Any
from api.handlers import Text2SQLHandler
from core.llm.base import BaseLLMBackend


def create_app(vanna_instance: Optional[BaseLLMBackend] = None) -> Flask:
    """
    创建 Flask 应用
    
    Args:
        vanna_instance: Vanna 实例（可选，如果为 None 则从全局变量获取）
        
    Returns:
        Flask 应用实例
    """
    app = Flask(__name__)
    CORS(app)  # 允许跨域请求
    
    # 创建处理器
    if vanna_instance is None:
        raise ValueError("vanna_instance 不能为 None")
    
    handler = Text2SQLHandler(vanna_instance)
    
    @app.route('/text2sql', methods=['POST'])
    def text2sql():
        """将自然语言问题转换为 SQL 查询"""
        return handler.text2sql()
    
    @app.route('/query', methods=['POST'])
    def query():
        """执行自然语言查询并返回结果"""
        return handler.query()
    
    @app.route('/health', methods=['GET'])
    def health():
        """
        健康检查接口
        
        响应:
        {
            "status": "healthy",
            "service": "text2sql-api"
        }
        """
        return jsonify({
            'status': 'healthy',
            'service': 'text2sql-api'
        }), 200
    
    @app.route('/openapi.yaml', methods=['GET'])
    def openapi_yaml():
        """返回 OpenAPI 规范文件（YAML格式）"""
        try:
            # 从项目根目录查找 openapi.yaml
            openapi_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                '..', 'openapi.yaml'
            )
            openapi_path = os.path.abspath(openapi_path)
            
            with open(openapi_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content, 200, {'Content-Type': 'text/yaml; charset=utf-8'}
        except FileNotFoundError:
            return jsonify({
                'error': 'OpenAPI 规范文件不存在',
                'status': 'error'
            }), 404
    
    @app.route('/openapi.json', methods=['GET'])
    def openapi_json():
        """返回 OpenAPI 规范文件（JSON格式）"""
        try:
            # 从项目根目录查找 openapi.yaml
            openapi_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                '..', 'openapi.yaml'
            )
            openapi_path = os.path.abspath(openapi_path)
            
            with open(openapi_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            return jsonify(content), 200
        except FileNotFoundError:
            return jsonify({
                'error': 'OpenAPI 规范文件不存在',
                'status': 'error'
            }), 404
    
    return app

