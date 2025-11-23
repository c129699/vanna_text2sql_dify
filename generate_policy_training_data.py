"""
从DDL和CSV数据生成训练数据脚本
用于生成documents.md和sql_examples.json
"""
import csv
import json
import os
import re
from collections import Counter
from datetime import datetime


def read_ddl(ddl_path):
    """读取DDL文件"""
    with open(ddl_path, 'r', encoding='utf-8') as f:
        return f.read()


def analyze_csv(csv_path, sample_size=1000):
    """分析CSV文件，获取数据特征"""
    data = {
        'total_rows': 0,
        'fields': {},
        'sample_values': {},
        'unique_values': {},
        'null_counts': {}
    }
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        # 初始化统计
        for field in fieldnames:
            data['fields'][field] = {
                'has_data': False,
                'sample_values': [],
                'unique_values': set(),
                'null_count': 0
            }
        
        # 读取数据
        for i, row in enumerate(reader):
            data['total_rows'] += 1
            
            for field in fieldnames:
                value = row.get(field, '').strip()
                field_data = data['fields'][field]
                
                if value and value != '':
                    field_data['has_data'] = True
                    if len(field_data['sample_values']) < 10:
                        field_data['sample_values'].append(value[:100])  # 限制长度
                    field_data['unique_values'].add(value)
                else:
                    field_data['null_count'] += 1
            
            # 只分析前sample_size行
            if i >= sample_size:
                break
    
    # 转换为可序列化的格式
    for field in fieldnames:
        field_data = data['fields'][field]
        data['unique_values'][field] = len(field_data['unique_values'])
        data['null_counts'][field] = field_data['null_count']
        data['sample_values'][field] = field_data['sample_values'][:5]  # 只保留5个样本
    
    return data


def extract_field_info_from_ddl(ddl_content):
    """从DDL中提取字段信息"""
    fields = []
    
    # 匹配字段定义
    pattern = r'`(\w+)`\s+(\w+(?:\([^)]+\))?)\s+(?:DEFAULT\s+[^,\s]+)?\s*(?:COMMENT\s+[\'"]([^\'"]+)[\'"])?'
    
    lines = ddl_content.split('\n')
    in_table = False
    
    for line in lines:
        line = line.strip()
        
        # 检查是否在CREATE TABLE中
        if 'CREATE TABLE' in line.upper():
            in_table = True
            continue
        
        if in_table and line.startswith('`'):
            # 提取字段名、类型和注释
            match = re.search(r'`(\w+)`\s+(\w+(?:\([^)]+\))?)', line)
            if match:
                field_name = match.group(1)
                field_type = match.group(2)
                
                # 提取注释
                comment_match = re.search(r"COMMENT\s+['\"]([^'\"]+)['\"]", line)
                comment = comment_match.group(1) if comment_match else ''
                
                fields.append({
                    'name': field_name,
                    'type': field_type,
                    'comment': comment
                })
        
        # 检查是否结束
        if in_table and line.startswith(')') and 'COMMENT' in line:
            break
    
    return fields


def generate_documents(ddl_content, csv_analysis):
    """生成documents.md"""
    fields = extract_field_info_from_ddl(ddl_content)
    
    # 提取表名和表注释
    table_match = re.search(r"CREATE TABLE\s+[`']?(\w+)[`']?", ddl_content, re.IGNORECASE)
    table_name = table_match.group(1) if table_match else 'info_policy_service'
    
    table_comment_match = re.search(r"COMMENT\s*=\s*['\"]([^'\"]+)['\"]", ddl_content)
    table_comment = table_comment_match.group(1) if table_comment_match else '政策服务表'
    
    doc = f"""# 政策服务数据库文档

## 表结构说明

### {table_name} 表

{table_comment}，存储各类政策服务信息，包括服务名称、所属区域、部门分类、申报条件、兑现标准等详细信息。

#### 主要字段说明

"""
    
    # 添加字段说明
    for field in fields:
        field_name = field['name']
        field_type = field['type']
        field_comment = field['comment']
        
        # 获取数据特征
        csv_field_data = csv_analysis['fields'].get(field_name, {})
        sample_values = csv_field_data.get('sample_values', [])
        unique_count = csv_analysis['unique_values'].get(field_name, 0)
        
        doc += f"- **{field_name}**: {field_comment or '无注释'}\n"
        doc += f"  - 数据类型: {field_type}\n"
        
        if sample_values:
            doc += f"  - 示例值: {', '.join(sample_values[:3])}\n"
        
        if unique_count > 0:
            doc += f"  - 唯一值数量: {unique_count}\n"
        
        doc += "\n"
    
    # 添加核心查询任务说明
    doc += """#### 核心查询任务（重要）

**所有查询都必须返回完整的一行数据（SELECT * 或列出所有字段）**

1. **根据服务事项名称+区域信息锁定具体服务事项的所有信息**（核心场景）
   - 查询字段：`service_name`（服务事项名称）和 `belong_area`（区域信息）
   - 查询方式：**必须使用模糊查询（LIKE）**
     - `service_name LIKE '%服务事项关键词%'`
     - `belong_area LIKE '%区域关键词%' OR belong_area LIKE '%安徽省%'`（**重要：查询区域时总是要包含"安徽省"**）
   - 返回：完整的一行数据（所有字段）
   - SQL模式：`SELECT * FROM info_policy_service WHERE service_name LIKE '%服务事项%' AND (belong_area LIKE '%区域%' OR belong_area LIKE '%安徽省%')`
   - 示例：查询"高新技术企业"相关的办事项在"合肥市"的详细信息

2. **按照实施主体查询**
   - 查询字段：`create_dept_name`（创建部门名称，实施主体）或 `org_name`（部门分类）
   - 查询方式：使用模糊查询（LIKE）
     - `create_dept_name LIKE '%实施主体关键词%'` 或
     - `org_name LIKE '%部门关键词%'`
   - 返回：完整的一行数据（所有字段）
   - SQL模式：`SELECT * FROM info_policy_service WHERE create_dept_name LIKE '%实施主体%'`
   - 示例：查询"科学技术局"实施的政策服务详细信息

3. **按照通办层级查询**
   - 查询字段：`service_level`（服务级别，通办层级）
   - 查询方式：可以使用精确匹配或模糊查询
     - `service_level = '省级'` 或
     - `service_level LIKE '%省级%'`
   - 可能的值：国家、省级、市级、区县级
   - 返回：完整的一行数据（所有字段）
   - SQL模式：`SELECT * FROM info_policy_service WHERE service_level = '省级'`
   - 示例：查询"省级"通办的政策服务详细信息

#### 查询规则

1. **主要查询字段**：
   - `service_name`（服务事项名称）和 `belong_area`（区域信息）是核心查询字段
   - 这两个字段**必须使用模糊查询（LIKE）**，不要使用精确匹配（=）
   - **重要：查询 `belong_area` 时，总是要使用 `OR belong_area LIKE '%安徽省%'` 条件**，即：`(belong_area LIKE '%区域关键词%' OR belong_area LIKE '%安徽省%')`

2. **其他字段的作用**：
   - 其他字段（如联系方式、地址、部门、申报条件、兑现标准等）**不作为查询条件**
   - 这些字段主要用于作为返回结果，展示完整的办事详情

3. **返回数据规则**：
   - **每次查询都必须返回完整的一行数据**
   - 使用 `SELECT *` 或列出所有字段
   - 确保返回所有字段信息，包括：id, service_name, belong_area, org_name, apply_condition, service_level, contact_telephone, apply_materials, apply_start_time, apply_end_time, address, cash_standard, cash_way, policy_term, service_procedure, create_dept_name

4. **空数据处理**：
   - 数据库里面很多空数据，查询时**不需要判断非空**
   - 空的字段也可以正常返回，不需要添加 `IS NOT NULL` 或 `<> ''` 等条件
   - 即使字段为空，也要返回完整的一行数据

#### 注意事项

- **service_name 和 belong_area 必须使用模糊查询（LIKE）**，不要使用精确匹配（=）
- 其他字段一般不作为查询条件，主要用于返回结果
- 每次查询都返回完整的一行数据，不要只返回部分字段
- 时间字段格式为 YYYY-MM-DD
- 某些字段可能为空，这是正常的，不需要判断非空

"""
    
    return doc


def generate_sql_examples(ddl_content, csv_analysis):
    """生成sql_examples.json，聚焦三个核心查询任务"""
    # 提取表名
    table_match = re.search(r"CREATE TABLE\s+[`']?(\w+)[`']?", ddl_content, re.IGNORECASE)
    table_name = table_match.group(1) if table_match else 'info_policy_service'
    
    # 从CSV分析结果中获取实际数据样本
    service_name_samples = csv_analysis['fields'].get('service_name', {}).get('sample_values', [])
    belong_area_samples = csv_analysis['fields'].get('belong_area', {}).get('sample_values', [])
    create_dept_name_samples = csv_analysis['fields'].get('create_dept_name', {}).get('sample_values', [])
    org_name_samples = csv_analysis['fields'].get('org_name', {}).get('sample_values', [])
    service_level_samples = csv_analysis['fields'].get('service_level', {}).get('sample_values', [])
    
    examples = []
    
    # 任务1：根据服务事项名称+区域信息锁定具体服务事项的所有信息
    # 生成多种服务名称和区域的组合查询
    service_keywords = ['高新技术企业', '奖励', '补贴', '补助', '认定', '申报', '研发', '创新']
    area_keywords = ['合肥', '宿州', '亳州', '芜湖', '蚌埠']
    
    # 如果CSV中有实际数据，使用实际数据的关键词
    if service_name_samples:
        # 从实际服务名称中提取关键词
        for sample in service_name_samples[:5]:
            if sample:
                # 提取关键词（取前几个字或包含常见关键词）
                for keyword in service_keywords:
                    if keyword in sample:
                        for area in (belong_area_samples[:3] if belong_area_samples else area_keywords[:3]):
                            if area:
                                area_key = area.replace('市', '').replace('县', '').replace('区', '')
                                examples.append({
                                    "question": f"查询{area}的{keyword}相关的服务事项信息",
                                    "sql": f"SELECT * FROM {table_name} WHERE service_name LIKE '%{keyword}%' AND (belong_area LIKE '%{area_key}%' OR belong_area LIKE '%安徽省%')"
                                })
    
    # 补充一些通用的服务名称+区域查询
    for service_kw in service_keywords[:5]:
        for area_kw in area_keywords[:3]:
            examples.append({
                "question": f"查询{area_kw}市的{service_kw}相关的服务事项详细信息",
                "sql": f"SELECT * FROM {table_name} WHERE service_name LIKE '%{service_kw}%' AND (belong_area LIKE '%{area_kw}%' OR belong_area LIKE '%安徽省%')"
            })
    
    # 使用实际的服务名称样本（取关键词部分）
    if service_name_samples:
        for i, sample in enumerate(service_name_samples[:3]):
            if sample and len(sample) > 5:
                # 提取服务名称的关键部分（前10个字符或包含关键词的部分）
                keyword = sample[:10] if len(sample) > 10 else sample
                # 移除可能的标点符号
                keyword = keyword.replace('，', '').replace('。', '').replace('、', '')
                if belong_area_samples:
                    for area in belong_area_samples[:2]:
                        if area:
                            area_key = area.replace('市', '').replace('县', '').replace('区', '')
                            examples.append({
                                "question": f"查询{area}的{keyword}服务事项的完整信息",
                                "sql": f"SELECT * FROM {table_name} WHERE service_name LIKE '%{keyword}%' AND (belong_area LIKE '%{area_key}%' OR belong_area LIKE '%安徽省%')"
                            })
    
    # 任务2：按照实施主体查询
    # 使用 create_dept_name 查询
    if create_dept_name_samples:
        for dept in create_dept_name_samples[:5]:
            if dept and len(dept) > 2:
                # 提取部门关键词
                dept_keyword = dept[:8] if len(dept) > 8 else dept
                dept_keyword = dept_keyword.replace('局', '').replace('部门', '').replace('委员会', '')
                examples.append({
                    "question": f"查询{dept}实施的政策服务详细信息",
                    "sql": f"SELECT * FROM {table_name} WHERE create_dept_name LIKE '%{dept_keyword}%'"
                })
    
    # 使用 org_name 查询
    org_keywords = ['科技', '工信', '财政', '人社', '商务', '教育', '卫生']
    if org_name_samples:
        for org in org_name_samples[:5]:
            if org:
                org_key = org.replace('部门', '')
                examples.append({
                    "question": f"查询{org}的政策服务详细信息",
                    "sql": f"SELECT * FROM {table_name} WHERE org_name LIKE '%{org_key}%'"
                })
    
    # 补充一些通用的部门查询
    for org_kw in org_keywords[:5]:
        examples.append({
            "question": f"查询{org_kw}部门实施的政策服务详细信息",
            "sql": f"SELECT * FROM {table_name} WHERE org_name LIKE '%{org_kw}%'"
        })
    
    # 任务3：按照通办层级查询
    service_levels = ['国家', '省级', '市级', '区县级']
    for level in service_levels:
        examples.append({
            "question": f"查询{level}通办的政策服务详细信息",
            "sql": f"SELECT * FROM {table_name} WHERE service_level = '{level}'"
        })
        # 也生成一个使用LIKE的版本
        examples.append({
            "question": f"查询{level}级别的政策服务完整信息",
            "sql": f"SELECT * FROM {table_name} WHERE service_level LIKE '%{level}%'"
        })
    
    # 如果CSV中有实际的service_level数据，也使用
    if service_level_samples:
        for level in service_level_samples[:4]:
            if level and level in service_levels:
                examples.append({
                    "question": f"查询{level}通办层级的政策服务所有信息",
                    "sql": f"SELECT * FROM {table_name} WHERE service_level = '{level}'"
                })
    
    return examples


def main():
    """主函数"""
    print("=" * 60)
    print("开始生成政策服务训练数据...")
    print("=" * 60)
    
    # 文件路径
    ddl_path = "DDL/policy_service.ddl"
    csv_path = "DDL/info_policy_service_202511231041.csv"
    documents_path = "training_data/documents.md"
    sql_examples_path = "training_data/sql_examples.json"
    
    # 检查文件是否存在
    if not os.path.exists(ddl_path):
        print(f"错误: DDL文件不存在: {ddl_path}")
        return
    
    if not os.path.exists(csv_path):
        print(f"错误: CSV文件不存在: {csv_path}")
        return
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(documents_path), exist_ok=True)
    
    # 读取DDL
    print("\n正在读取DDL文件...")
    ddl_content = read_ddl(ddl_path)
    print("[OK] DDL文件读取完成")
    
    # 分析CSV
    print("\n正在分析CSV文件（这可能需要一些时间）...")
    csv_analysis = analyze_csv(csv_path, sample_size=2000)
    print(f"[OK] CSV文件分析完成（共 {csv_analysis['total_rows']} 行数据）")
    
    # 生成documents.md
    print("\n正在生成documents.md...")
    documents_content = generate_documents(ddl_content, csv_analysis)
    with open(documents_path, 'w', encoding='utf-8') as f:
        f.write(documents_content)
    print(f"[OK] documents.md 已生成: {documents_path}")
    
    # 生成sql_examples.json
    print("\n正在生成sql_examples.json...")
    sql_examples = generate_sql_examples(ddl_content, csv_analysis)
    with open(sql_examples_path, 'w', encoding='utf-8') as f:
        json.dump(sql_examples, f, ensure_ascii=False, indent=2)
    print(f"[OK] sql_examples.json 已生成: {sql_examples_path}")
    print(f"  共生成 {len(sql_examples)} 个SQL示例")
    
    print("\n" + "=" * 60)
    print("训练数据生成完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

