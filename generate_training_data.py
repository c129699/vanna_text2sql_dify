"""
生成训练数据脚本
用于将问题转换为SQL并添加到训练数据中
"""
import json
import os
import sys
from dependencies import DependencyContainer
from core.vanna.factory import VannaFactory
from core.vanna.trainer import VannaTrainer


def main():
    """主函数"""
    print("=" * 60)
    print("开始生成训练数据...")
    print("=" * 60)
    
    # 要处理的问题列表
    questions = [
        "实施主体是黄山市科学技术局的可用办事项有哪些？",
        "可以线上办理的办事项有哪些？",
        "按行政区划统计事项数量。",
        "按照实施主体统计办事项数量。",
        "查询省级通办的项目。",
        "查询蜀山区可以办理的项目",
        "查询区县级办理的事项",
        "查询办理时间包含周末的事项",
        "查询支持 PC 端办理的事项及其网址",
        "查询大型科学仪器设备入网事项的可办区域和相关联系人"
    ]
    
    # 读取配置文件
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    print(f"使用配置文件: {config_path}")
    
    # 创建依赖容器
    container = DependencyContainer(config_path)
    
    # 创建 Vanna 实例
    print("\n正在初始化 Vanna 实例...")
    factory = VannaFactory(container)
    vn = factory.create()
    
    # 进行训练（这样模型才能生成SQL）
    print("\n正在训练 Vanna 模型...")
    config = container.get_config()
    trainer = VannaTrainer(vn, config)
    trainer.train_all()
    
    # 读取现有的训练数据
    sql_examples_path = config.get('training', {}).get(
        'sql_examples_path', 
        'training_data/sql_examples.json'
    )
    
    print(f"\n读取现有训练数据: {sql_examples_path}")
    if os.path.exists(sql_examples_path):
        with open(sql_examples_path, 'r', encoding='utf-8') as f:
            existing_examples = json.load(f)
    else:
        existing_examples = []
        print("警告: 训练数据文件不存在，将创建新文件")
    
    # 检查已存在的问题（避免重复）
    existing_questions = {ex.get('question', '').strip() for ex in existing_examples}
    
    # 生成SQL并添加到训练数据
    print("\n" + "=" * 60)
    print("开始生成SQL...")
    print("=" * 60)
    
    new_examples = []
    for i, question in enumerate(questions, 1):
        question = question.strip()
        
        # 检查是否已存在
        if question in existing_questions:
            print(f"[{i}/{len(questions)}] 跳过已存在的问题: {question}")
            continue
        
        print(f"\n[{i}/{len(questions)}] 处理问题: {question}")
        try:
            # 生成SQL
            sql = vn.generate_sql(question=question)
            print(f"  生成的SQL: {sql}")
            
            # 添加到新示例列表
            new_examples.append({
                "question": question,
                "sql": sql
            })
            
        except Exception as e:
            print(f"  ✗ 生成SQL失败: {e}")
            continue
    
    # 合并新示例到现有数据
    if new_examples:
        print(f"\n添加 {len(new_examples)} 个新示例到训练数据...")
        all_examples = existing_examples + new_examples
        
        # 保存到文件
        with open(sql_examples_path, 'w', encoding='utf-8') as f:
            json.dump(all_examples, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 训练数据已更新: {sql_examples_path}")
        print(f"  总示例数: {len(all_examples)}")
        print(f"  新增示例数: {len(new_examples)}")
        
        # 显示新增的示例
        print("\n新增的训练示例:")
        for ex in new_examples:
            print(f"  问题: {ex['question']}")
            print(f"  SQL: {ex['sql']}")
            print()
    else:
        print("\n没有新示例需要添加")
    
    print("=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

