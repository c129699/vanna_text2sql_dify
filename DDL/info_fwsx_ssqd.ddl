-- text2sql.info_fwsx_ssqd definition

CREATE TABLE `info_fwsx_ssqd` (
  `id` varchar(32) NOT NULL COMMENT '主键ID',
  `ssqd_dept_name` varchar(400) DEFAULT NULL COMMENT '实施清单所属部门名称 实施主体',
  `accept_condition` text DEFAULT NULL COMMENT '受理条件',
  `hanle_time` varchar(1000) DEFAULT NULL COMMENT '办理时间',
  `hanle_addr` text DEFAULT NULL COMMENT '办理地点',
  `zx_phone` varchar(20) DEFAULT NULL COMMENT '咨询电话 咨询方式',
  `ts_phone` varchar(20) DEFAULT NULL COMMENT '监督投诉方式',
  `enactment` text DEFAULT NULL COMMENT '设定证明依据 设定依据',
  `hanle_proc` text DEFAULT NULL COMMENT '办理流程',
  `matter_name` varchar(100) NOT NULL COMMENT '事项名称',
  `xzqh_jb` varchar(1) DEFAULT NULL COMMENT '行政区划级别，1省 2地级市 3 区县',
  `xzqh_name` varchar(100) DEFAULT NULL COMMENT '行政区划名称',
  `app_apply_url` varchar(500) NOT NULL COMMENT 'h5办事地址',
  `gateway_apply_url` varchar(500) NOT NULL COMMENT 'pc办事地址',
  PRIMARY KEY (`id`)
) ORGANIZATION INDEX DEFAULT CHARSET = utf8mb4 ROW_FORMAT = DYNAMIC COMPRESSION = 'zstd_1.3.8' REPLICA_NUM = 1 BLOCK_SIZE = 16384 USE_BLOOM_FILTER = FALSE ENABLE_MACRO_BLOCK_BLOOM_FILTER = FALSE TABLET_SIZE = 134217728 PCTFREE = 0 COMMENT = '实施清单';