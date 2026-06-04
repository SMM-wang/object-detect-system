CREATE DATABASE IF NOT EXISTS aerial_detect DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aerial_detect;

CREATE TABLE IF NOT EXISTS sys_user (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(64) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  nickname VARCHAR(64),
  role VARCHAR(32) NOT NULL DEFAULT 'user',
  status TINYINT NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  KEY idx_sys_user_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS detect_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  file_name VARCHAR(255) NOT NULL,
  file_type VARCHAR(32) NOT NULL,
  file_hash VARCHAR(128) NOT NULL,
  model_version VARCHAR(64) NOT NULL,
  confidence DECIMAL(4,3) NOT NULL,
  iou DECIMAL(4,3) NOT NULL,
  result_json JSON,
  analysis_text TEXT,
  object_count INT NOT NULL DEFAULT 0,
  elapsed_ms INT NOT NULL,
  status VARCHAR(32) NOT NULL,
  error_msg VARCHAR(512),
  created_at DATETIME NOT NULL,
  CONSTRAINT fk_detect_log_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
  KEY idx_detect_log_user_id (user_id),
  KEY idx_detect_log_created_at (created_at),
  KEY idx_detect_log_model_version (model_version),
  KEY idx_detect_log_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
