# 实施清单数据库文档

## 表结构说明

### info_fwsx_ssqd 表

实施清单表：存储各类实施清单信息，包括事项名称、行政区划、实施主体、受理条件、办理时间、办理地点、咨询电话、监督投诉方式、设定依据、办理流程、办事地址等详细信息。

#### 主要字段说明

- **id**: 主键ID
  - 数据类型: varchar(32)
  - 注意：查询时不需要返回此字段

- **ssqd_dept_name**: 实施清单所属部门名称 实施主体
  - 数据类型: varchar(400)
  - 示例值: 合肥市科学技术局, 宿州市人力资源和社会保障局

- **accept_condition**: 受理条件
  - 数据类型: text
  - 详细描述申请该事项需要满足的条件

- **hanle_time**: 办理时间
  - 数据类型: varchar(1000)
  - 示例值: 工作日 9:00-17:00, 周一至周五

- **hanle_addr**: 办理地点
  - 数据类型: text
  - 示例值: 合肥市政务服务中心, 宿州市政务服务大厅

- **zx_phone**: 咨询电话 咨询方式
  - 数据类型: varchar(20)
  - 示例值: 0551-63538803, 0564-3371294

- **ts_phone**: 监督投诉方式
  - 数据类型: varchar(20)
  - 示例值: 0551-12345, 0564-12345

- **enactment**: 设定证明依据 设定依据
  - 数据类型: text
  - 详细说明设定该事项的法律法规依据

- **hanle_proc**: 办理流程
  - 数据类型: text
  - 详细描述申请和办理该事项的具体流程步骤

- **matter_name**: 事项名称
  - 数据类型: varchar(100)
  - 示例值: 高新技术企业认定, 企业研发费用加计扣除, 创业补贴申请
  - **核心查询字段**：用于查询特定事项

- **xzqh_jb**: 行政区划级别
  - 数据类型: varchar(1)
  - 可能的值: 1（省）、2（地级市）、3（区县）
  - 说明：1表示省级，2表示地级市，3表示区县级

- **xzqh_name**: 行政区划名称
  - 数据类型: varchar(100)
  - 示例值: 安徽省, 合肥市, 宿州市, 亳州市, 芜湖市, 瑶海区
  - **核心查询字段**：用于查询特定区域的事项

- **app_apply_url**: h5办事地址
  - 数据类型: varchar(500)
  - 移动端办事链接地址

- **gateway_apply_url**: pc办事地址
  - 数据类型: varchar(500)
  - PC端办事链接地址

#### 核心查询场景（重要）

**所有查询都必须返回完整的一行数据（除了id字段，其他所有字段都要返回）**

1. **根据事项名称+行政区划区域查询完整信息**（核心场景）
   - 查询字段：`matter_name`（事项名称）和 `xzqh_name`（行政区划名称）
   - 查询方式：**必须使用模糊查询（LIKE）**
     - `matter_name LIKE '%事项名称关键词%'`
     - `xzqh_name LIKE '%区域关键词%' OR xzqh_name LIKE '%安徽省%'`（**重要：查询区域时总是要包含"安徽省"**）
     - 如果查询的是某个市（如"合肥市"），则要同时匹配该市和"安徽省"：`(xzqh_name LIKE '%合肥%' OR xzqh_name LIKE '%安徽省%')`
     - 如果查询的是某个区县（如"瑶海区"），则要同时匹配该区县、所属市和"安徽省"：`(xzqh_name LIKE '%瑶海%' OR xzqh_name LIKE '%合肥%' OR xzqh_name LIKE '%安徽省%')`
   - 返回：完整的一行数据（除了id，所有字段都要返回）
   - SQL模式：`SELECT ssqd_dept_name, accept_condition, hanle_time, hanle_addr, zx_phone, ts_phone, enactment, hanle_proc, matter_name, xzqh_jb, xzqh_name, app_apply_url, gateway_apply_url FROM info_fwsx_ssqd WHERE matter_name LIKE '%事项名称%' AND (xzqh_name LIKE '%区域%' OR xzqh_name LIKE '%安徽省%')`
   - 示例：查询"高新技术企业认定"相关的办事项在"合肥市"的详细信息

#### 查询规则

1. **主要查询字段**：
   - `matter_name`（事项名称）和 `xzqh_name`（行政区划名称）是核心查询字段
   - 这两个字段**必须使用模糊查询（LIKE）**，不要使用精确匹配（=）
   - **重要：查询 `xzqh_name` 时，总是要使用 `OR xzqh_name LIKE '%安徽省%'` 条件**
   - 如果查询的是某个市，则：`(xzqh_name LIKE '%市名%' OR xzqh_name LIKE '%安徽省%')`
   - 如果查询的是某个区县，则：`(xzqh_name LIKE '%区县名%' OR xzqh_name LIKE '%所属市名%' OR xzqh_name LIKE '%安徽省%')`

2. **返回字段规则**：
   - **每次查询都必须返回完整的一行数据（除了id字段）**
   - 必须返回的字段：`ssqd_dept_name, accept_condition, hanle_time, hanle_addr, zx_phone, ts_phone, enactment, hanle_proc, matter_name, xzqh_jb, xzqh_name, app_apply_url, gateway_apply_url`
   - 可以使用 `SELECT *` 但要注意排除id字段，或者明确列出所有字段

3. **模糊查询规则**：
   - 事项名称和区域名称的查询都是模糊匹配，用户给出的关键词可能不完整
   - 例如：用户说"高新技术企业"，实际表中可能是"高新技术企业认定"
   - 例如：用户说"合肥"，实际表中可能是"合肥市"

4. **区域层级查询规则**：
   - 如果用户查询的是某个区县，可能匹配到该区县、所属市、或省级（安徽省）的记录
   - 如果用户查询的是某个市，可能匹配到该市或省级（安徽省）的记录
   - 因此查询条件中要使用OR连接多个可能的区域匹配

#### 注意事项

- **matter_name 和 xzqh_name 必须使用模糊查询（LIKE）**，不要使用精确匹配（=）
- 查询区域时，总是要包含"安徽省"作为备选条件
- 每次查询都返回完整的一行数据（除了id），不要只返回部分字段
- 某些字段可能为空，这是正常的，不需要判断非空
- 事项名称和区域名称的查询都是模糊匹配，关键词可能不完整
