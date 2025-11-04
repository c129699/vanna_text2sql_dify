"""
API 处理函数
"""
from typing import Optional, Any, Dict
from flask import request, jsonify
import traceback
import pandas as pd
from core.llm.base import BaseLLMBackend


class Text2SQLHandler:
    """Text2SQL API 处理器"""
    
    def __init__(self, vanna_instance: BaseLLMBackend):
        """
        初始化处理器
        
        Args:
            vanna_instance: Vanna 实例
        """
        self.vn = vanna_instance
    
    def text2sql(self) -> tuple:
        """
        将自然语言问题转换为 SQL 查询
        
        请求体:
        {
            "question": "查询所有事项名称"
        }
        
        响应:
        {
            "sql": "SELECT matter_name FROM info_fwsx_ssqd WHERE del_flag = '0'",
            "question": "查询所有事项名称",
            "status": "success"
        }
        """
        try:
            # 验证请求体
            if not request.is_json:
                return jsonify({
                    'error': '请求必须是 JSON 格式',
                    'status': 'error'
                }), 400
            
            data = request.get_json()
            
            # 验证必需参数
            if 'question' not in data:
                return jsonify({
                    'error': '缺少必需参数: question',
                    'status': 'error'
                }), 400
            
            question = data.get('question', '').strip()
            
            if not question:
                return jsonify({
                    'error': 'question 参数不能为空',
                    'status': 'error'
                }), 400
            
            # 使用 Vanna 生成 SQL
            if self.vn is None:
                return jsonify({
                    'error': 'Vanna 实例未初始化',
                    'status': 'error'
                }), 500
            
            # 生成 SQL
            sql = self.vn.generate_sql(question=question)
            
            # 返回结果
            return jsonify({
                'sql': sql,
                'question': question,
                'status': 'success'
            }), 200
            
        except Exception as e:
            # 记录错误详情
            error_msg = str(e)
            error_trace = traceback.format_exc()
            print(f"错误: {error_msg}")
            print(f"堆栈跟踪:\n{error_trace}")
            
            return jsonify({
                'error': error_msg,
                'status': 'error'
            }), 500
    
    def query(self) -> tuple:
        """
        执行自然语言查询并返回结果
        
        请求体:
        {
            "question": "查询所有事项名称"
        }
        
        响应:
        {
            "sql": "SELECT matter_name FROM info_fwsx_ssqd WHERE del_flag = '0'",
            "question": "查询所有事项名称",
            "data": [
                {"matter_name": "事项1"},
                {"matter_name": "事项2"}
            ],
            "row_count": 2,
            "status": "success"
        }
        """
        try:
            # 验证请求体
            if not request.is_json:
                return jsonify({
                    'error': '请求必须是 JSON 格式',
                    'status': 'error'
                }), 400
            
            data = request.get_json()
            
            # 验证必需参数
            if 'question' not in data:
                return jsonify({
                    'error': '缺少必需参数: question',
                    'status': 'error'
                }), 400
            
            question = data.get('question', '').strip()
            
            if not question:
                return jsonify({
                    'error': 'question 参数不能为空',
                    'status': 'error'
                }), 400
            
            # 使用 Vanna 生成 SQL
            if self.vn is None:
                return jsonify({
                    'error': 'Vanna 实例未初始化',
                    'status': 'error'
                }), 500
            
            # 生成 SQL
            sql = self.vn.generate_sql(question=question)
            
            # 执行 SQL 查询
            try:
                df = self.vn.run_sql(sql)
                
                # 将 DataFrame 转换为字典列表
                result_data = df.to_dict('records')
                
                # 确保所有 NaN 值都被转换为 None
                for record in result_data:
                    for key, value in record.items():
                        # 检查是否为 NaN 值
                        try:
                            if pd.isna(value):
                                record[key] = None
                        except (TypeError, ValueError):
                            # 如果无法判断，检查是否为 NaN（float('nan') 的特殊性）
                            if isinstance(value, float) and value != value:
                                record[key] = None
                
                # 返回结果
                return jsonify({
                    'sql': sql,
                    'question': question,
                    'data': result_data,
                    'row_count': len(result_data),
                    'columns': list(df.columns),
                    'status': 'success'
                }), 200
                
            except Exception as sql_error:
                # SQL 执行错误
                error_msg = str(sql_error)
                print(f"SQL 执行错误: {error_msg}")
                print(f"SQL: {sql}")
                
                return jsonify({
                    'sql': sql,
                    'question': question,
                    'error': f'SQL 执行失败: {error_msg}',
                    'status': 'sql_error'
                }), 500
            
        except Exception as e:
            # 记录错误详情
            error_msg = str(e)
            error_trace = traceback.format_exc()
            print(f"错误: {error_msg}")
            print(f"堆栈跟踪:\n{error_trace}")
            
            return jsonify({
                'error': error_msg,
                'status': 'error'
            }), 500

