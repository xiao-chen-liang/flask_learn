/*
 Navicat Premium Data Transfer

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 80030
 Source Host           : localhost:3306
 Source Schema         : postgraduate

 Target Server Type    : MySQL
 Target Server Version : 80030
 File Encoding         : 65001

 Date: 19/04/2024 17:39:10
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for detail
-- ----------------------------
DROP TABLE IF EXISTS `detail`;
CREATE TABLE `detail`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `sn` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '学号',
  `course` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '课程',
  `type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '性质',
  `grade` int NULL DEFAULT NULL COMMENT '成绩',
  `point` decimal(10, 2) NULL DEFAULT NULL COMMENT '学分',
  `required` int NULL DEFAULT 1 COMMENT '0表示不包括，1表示包括',
  `semester` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '学期',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4549 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for report
-- ----------------------------
DROP TABLE IF EXISTS `report`;
CREATE TABLE `report`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `sn` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '学号',
  `college` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '学院',
  `major` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '专业',
  `grade` int NULL DEFAULT NULL COMMENT '年级',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '姓名',
  `total` decimal(10, 2) NULL DEFAULT NULL COMMENT '总学分',
  `required` decimal(10, 2) NULL DEFAULT NULL COMMENT '必修学分',
  `specialized` decimal(10, 2) NULL DEFAULT NULL COMMENT '专业选修学分',
  `public` decimal(10, 2) NULL DEFAULT NULL COMMENT '公共选修学分',
  `socre` decimal(10, 2) NULL DEFAULT NULL COMMENT '智育成绩',
  ` comprehensive` decimal(10, 2) NULL DEFAULT NULL COMMENT '综合成绩',
  `sum` decimal(10, 2) NULL DEFAULT NULL COMMENT '总得分',
  `date` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '打印日期',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 82 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for rule
-- ----------------------------
DROP TABLE IF EXISTS `rule`;
CREATE TABLE `rule`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `college` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '学院',
  `grade` int NULL DEFAULT NULL COMMENT '年级',
  `specialized` int NULL DEFAULT 1 COMMENT '专业选修课，0表示不包含，1表示包含',
  `public` int NULL DEFAULT 1 COMMENT '公共选修课，0表示不包含，1表示包含',
  `policy` int NULL DEFAULT 1 COMMENT '形式与政策，0表示不包含，1表示包含',
  `pe` int NULL DEFAULT 1 COMMENT '体育，0表示不包含，1表示包含',
  `skill` int NULL DEFAULT 1 COMMENT '军事技能，0表示不包含，1表示包含',
  `theory` int NULL DEFAULT 1 COMMENT '军事理论，0表示不包含，1表示包含',
  `score` decimal(10, 2) NULL DEFAULT 0.85 COMMENT '智育成绩权重',
  `comprehensive` decimal(10, 2) NULL DEFAULT 0.15 COMMENT '综合成绩权重',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 60 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
