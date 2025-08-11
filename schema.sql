SET NAMES utf8mb4;

-- ----------------------------
-- Table structure for projects
-- ----------------------------
DROP TABLE IF EXISTS `projects`;
CREATE TABLE `projects` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '项目ID',
  `name` VARCHAR(255) NOT NULL COMMENT '项目名称',
  `description` TEXT COMMENT '项目描述',
  `base_url` VARCHAR(255) COMMENT '基础URL',
  `browser` VARCHAR(50) NOT NULL DEFAULT 'chromium' COMMENT '默认浏览器 (chromium, firefox, webkit)',
  `headless` BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否以无头模式运行',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='项目配置表';

-- ----------------------------
-- Table structure for modules
-- ----------------------------
DROP TABLE IF EXISTS `modules`;
CREATE TABLE `modules` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '模块ID',
  `project_id` INT NOT NULL COMMENT '所属项目ID',
  `name` VARCHAR(255) NOT NULL COMMENT '模块名称',
  `description` TEXT COMMENT '模块描述',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_project_modulename` (`project_id`, `name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试模块表';

-- ----------------------------
-- Table structure for test_cases
-- ----------------------------
DROP TABLE IF EXISTS `test_cases`;
CREATE TABLE `test_cases` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '用例ID',
  `project_id` INT NOT NULL COMMENT '所属项目ID',
  `module_id` INT NULL COMMENT '所属模块ID',
  `name` VARCHAR(255) NOT NULL COMMENT '用例名称',
  `description` TEXT COMMENT '用例描述',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试用例表';

-- ----------------------------
-- Table structure for test_steps
-- ----------------------------
DROP TABLE IF EXISTS `test_steps`;
CREATE TABLE `test_steps` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '步骤ID',
  `case_id` INT NOT NULL COMMENT '所属测试用例ID',
  `step_order` INT NOT NULL COMMENT '执行顺序',
  `keyword` VARCHAR(100) NOT NULL COMMENT '关键字 (e.g., goto, click, fill)',
  `locator` VARCHAR(255) COMMENT '定位器 (CSS Selector, XPath, etc.)',
  `value` TEXT COMMENT '操作值 (e.g., URL, input text)',
  `description` VARCHAR(255) COMMENT '步骤描述',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试步骤表';

-- ----------------------------
-- Table structure for test_runs
-- ----------------------------
DROP TABLE IF EXISTS `test_runs`;
CREATE TABLE `test_runs` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '运行ID',
  `case_id` INT NOT NULL COMMENT '测试用例ID',
  `status` VARCHAR(50) NOT NULL COMMENT '结果 (Passed, Failed, Skipped)',
  `start_time` DATETIME NOT NULL,
  `end_time` DATETIME NOT NULL,
  `duration` FLOAT COMMENT '持续时间 (秒)',
  `report_path` VARCHAR(255) COMMENT 'HTML报告路径',
  `log_path` VARCHAR(255) COMMENT '日志文件路径',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试运行结果表';

-- ----------------------------
-- Table structure for run_logs
-- ----------------------------
DROP TABLE IF EXISTS `run_logs`;
CREATE TABLE `run_logs` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `run_id` INT NOT NULL,
  `step_id` INT,
  `timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `level` VARCHAR(20) NOT NULL,
  `message` TEXT NOT NULL,
  `screenshot_path` VARCHAR(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='单次运行的详细日志';