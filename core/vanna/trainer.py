"""
Vanna 训练模块
负责加载训练数据并进行 DDL、文档和 SQL 训练
"""
import json
import os
from typing import Dict, Any
from core.llm.base import BaseLLMBackend


class VannaTrainer:
    """Vanna 训练器，封装训练逻辑"""
    
    def __init__(self, vn: BaseLLMBackend, config: Dict[str, Any]):
        """
        初始化训练器
        
        Args:
            vn: Vanna 实例
            config: 配置字典，包含训练数据路径
        """
        self.vn = vn
        self.config = config
        self.training_config = config.get('training', {})
    
    def train_ddl(self) -> bool:
        """
        训练 DDL（数据定义语言）
        
        Returns:
            是否训练成功
        """
        ddl_path = self.training_config.get('ddl_path', 'training_data/ddl.sql')
        
        if not os.path.exists(ddl_path):
            print(f"警告: DDL文件不存在: {ddl_path}")
            return False
        
        print("正在训练 DDL...")
        try:
            with open(ddl_path, 'r', encoding='utf-8') as f:
                ddl_content = f.read()
            
            self.vn.train(ddl=ddl_content)
            print("✓ DDL训练完成")
            return True
        except Exception as e:
            print(f"✗ DDL训练失败: {e}")
            return False
    
    def train_documents(self) -> bool:
        """
        训练文档说明
        
        Returns:
            是否训练成功
        """
        docs_path = self.training_config.get(
            'documents_path', 
            'training_data/documents.md'
        )
        
        if not os.path.exists(docs_path):
            print(f"警告: 文档文件不存在: {docs_path}")
            return False
        
        print("正在训练文档...")
        try:
            with open(docs_path, 'r', encoding='utf-8') as f:
                docs_content = f.read()
            
            self.vn.train(documentation=docs_content)
            print("✓ 文档训练完成")
            return True
        except Exception as e:
            print(f"✗ 文档训练失败: {e}")
            return False
    
    def train_sql_examples(self) -> bool:
        """
        训练 SQL 示例（问题-SQL对）
        
        Returns:
            是否训练成功
        """
        sql_path = self.training_config.get(
            'sql_examples_path', 
            'training_data/sql_examples.json'
        )
        
        if not os.path.exists(sql_path):
            print(f"警告: SQL示例文件不存在: {sql_path}")
            return False
        
        print("正在训练 SQL 示例...")
        try:
            with open(sql_path, 'r', encoding='utf-8') as f:
                sql_examples = json.load(f)
            
            success_count = 0
            for example in sql_examples:
                question = example.get('question')
                sql = example.get('sql')
                if question and sql:
                    try:
                        self.vn.train(question=question, sql=sql)
                        success_count += 1
                    except Exception as e:
                        print(f"  警告: 训练示例失败 - {question[:30]}...: {e}")
            
            print(f"✓ SQL示例训练完成（成功 {success_count}/{len(sql_examples)} 个）")
            return success_count > 0
        except Exception as e:
            print(f"✗ SQL示例训练失败: {e}")
            return False
    
    def train_all(self) -> Dict[str, bool]:
        """
        执行所有训练
        
        Returns:
            训练结果字典，包含各项训练是否成功
        """
        print("=" * 50)
        print("开始训练 Vanna 模型...")
        print("=" * 50)
        
        results = {
            'ddl': self.train_ddl(),
            'documents': self.train_documents(),
            'sql_examples': self.train_sql_examples(),
        }
        
        print("=" * 50)
        if all(results.values()):
            print("所有训练完成！")
        else:
            print("训练完成（部分训练可能失败）")
        print("=" * 50)
        
        return results

