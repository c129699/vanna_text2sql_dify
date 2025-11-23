-- zcxy_info_provdb.info_policy_service definition

CREATE TABLE `info_policy_service` (
  `id` varchar(100) NOT NULL COMMENT '政策服务唯一标识ID',
  `service_name` varchar(200) DEFAULT NULL COMMENT '服务名称，如\"高新技术企业认定奖励\"',
  `belong_area` varchar(200) DEFAULT NULL COMMENT '所属区域，如\"合肥市\"、\"宿州市\"等',
  `org_name` varchar(100) DEFAULT NULL COMMENT '部门分类，如\"科技部门\"、\"工信部门\"、\"财政部门\"等',
  `apply_condition` longtext DEFAULT NULL COMMENT '申报条件，详细描述申请该政策服务需要满足的条件',
  `service_level` varchar(20) DEFAULT NULL COMMENT '服务级别，存储文字值：国家、省级、市级、区县级',
  `contact_telephone` varchar(50) DEFAULT NULL COMMENT '联系电话',
  `apply_materials` varchar(1000) DEFAULT NULL COMMENT '申报材料，列出申请时需要提交的材料清单',
  `apply_end_time` varchar(20) DEFAULT NULL COMMENT '申报结束时间，格式：YYYY-MM-DD',
  `apply_start_time` varchar(20) DEFAULT NULL COMMENT '申报开始时间，格式：YYYY-MM-DD',
  `address` varchar(200) DEFAULT NULL COMMENT '办理地址，政策服务的办理地点',
  `cash_standard` varchar(5000) DEFAULT NULL COMMENT '兑现标准，详细说明政策奖励或补贴的标准和金额',
  `cash_way` varchar(50) DEFAULT NULL COMMENT '政策兑现方式，存储文字值：一键确认、直接兑现、亮码识别、立即兑现、限时办理',
  `policy_term` text DEFAULT NULL COMMENT '政策具体条款，政策的详细条款内容',
  `service_procedure` text DEFAULT NULL COMMENT '办理流程，申请和办理该政策服务的具体流程步骤',
  `create_dept_name` varchar(200) DEFAULT NULL COMMENT '创建部门名称，发布该政策服务的部门全称',
  PRIMARY KEY (`id`)
) ORGANIZATION INDEX DEFAULT CHARSET = utf8mb4 ROW_FORMAT = DYNAMIC COMPRESSION = 'zstd_1.3.8' REPLICA_NUM = 1 BLOCK_SIZE = 16384 USE_BLOOM_FILTER = FALSE ENABLE_MACRO_BLOCK_BLOOM_FILTER = FALSE TABLET_SIZE = 134217728 PCTFREE = 0 COMMENT = '政策服务表：存储各类政策服务信息';