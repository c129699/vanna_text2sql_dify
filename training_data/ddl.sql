-- 实施清单表定义
-- info_fwsx_ssqd: 政务服务实施清单表，用于存储政务服务事项的详细信息

CREATE TABLE `info_fwsx_ssqd` (
  `id` varchar(32) NOT NULL COMMENT '主键ID',
  `ssqd_code` varchar(40) NOT NULL COMMENT '实施清单code',
  `ssqd_dept_code` varchar(30) DEFAULT NULL COMMENT '实施清单所属部门编码',
  `ssqd_dept_name` varchar(400) DEFAULT NULL COMMENT '实施清单所属部门名称 实施主体',
  `accept_condition` text DEFAULT NULL COMMENT '受理条件',
  `is_charge` varchar(20) DEFAULT NULL COMMENT '是否收费，0否1是',
  `promise_time` varchar(50) DEFAULT NULL COMMENT '承诺办结时限',
  `hanle_form` varchar(20) DEFAULT NULL COMMENT '办理形式',
  `hanle_form_name` varchar(100) DEFAULT NULL COMMENT '办理形式名称',
  `is_book` varchar(20) DEFAULT NULL COMMENT '是否支持预约，0否1是',
  `hanle_time` varchar(1000) DEFAULT NULL COMMENT '办理时间',
  `hanle_time_range` varchar(400) DEFAULT NULL COMMENT '办理时间段',
  `hanle_addr` text DEFAULT NULL COMMENT '办理地点',
  `zx_phone` varchar(20) DEFAULT NULL COMMENT '咨询电话 咨询方式',
  `ts_phone` varchar(20) DEFAULT NULL COMMENT '监督投诉方式',
  `result_receive_way` varchar(100) DEFAULT NULL COMMENT '结果领取方式',
  `result_receive_way_name` varchar(500) DEFAULT NULL COMMENT '结果领取方式 物流快递',
  `enactment` text DEFAULT NULL COMMENT '设定证明依据 设定依据',
  `hanle_proc` text DEFAULT NULL COMMENT '办理流程',
  `create_by` varchar(255) DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(255) DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL,
  `del_flag` char(1) DEFAULT '0' COMMENT '0正常，1已删除',
  `matter_name` varchar(100) NOT NULL COMMENT '事项名称',
  `xzqh_parent_code` varchar(32) DEFAULT NULL COMMENT '行政区划上级编码(地市)',
  `xzqh_code` varchar(32) DEFAULT NULL COMMENT '行政区划编码（区县）',
  `xzqh_jb` varchar(1) DEFAULT NULL COMMENT '行政区划级别，1省 2地级市 3 区县',
  `xzqh_name` varchar(100) DEFAULT NULL COMMENT '行政区划名称',
  `app_apply_url` varchar(500) NOT NULL COMMENT 'h5办事地址',
  `gateway_apply_url` varchar(500) NOT NULL COMMENT 'pc办事地址',
  PRIMARY KEY (`id`)
) ORGANIZATION INDEX DEFAULT CHARSET = utf8mb4 ROW_FORMAT = DYNAMIC COMPRESSION = 'zstd_1.3.8' REPLICA_NUM = 1 BLOCK_SIZE = 16384 USE_BLOOM_FILTER = FALSE ENABLE_MACRO_BLOCK_BLOOM_FILTER = FALSE TABLET_SIZE = 134217728 PCTFREE = 0 COMMENT = '实施清单';

