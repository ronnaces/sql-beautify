# SQL 对齐与预览工具

[English](./README.md) | **简体中文**

欢迎使用 **SQL 对齐与预览工具**！  
这个应用程序旨在帮助您 **快速格式化和整理 SQL 代码**，尤其是 `CREATE TABLE` 语句。  
通过简洁的界面和强大的对齐引擎，您可以轻松地将杂乱的 SQL 转换为 **清晰、易读、专业的格式**，提升开发和维护效率。  

---

### 功能特色

#### ✨ **单条 SQL 对齐**

* **实时预览**：在左侧编辑器中粘贴 SQL，右侧预览区域会 **即时显示对齐后的结果**。  
* **左右对比**：原始 SQL 与格式化 SQL **并排展示**，对比更直观。  
* **代码统计**：自动统计总行数、有效行数、注释行数和字段数量，便于快速分析。  
* **导出选项**：一键下载格式化后的 SQL 或完整报告。  

#### 📂 **批量处理**

* **文件上传**：支持批量上传 `.sql` 或 `.txt` 文件。  
* **进度提示**：实时显示处理进度条和状态更新。  
* **文件名前缀**：可自定义下载文件的前缀，方便批量管理。  
* **处理报告**：自动生成报告，包含处理结果和潜在问题。  
* **ZIP 打包下载**：所有格式化文件会打包成 ZIP，便于统一下载。  

---

### 个性化设置

在左侧的设置栏中，您可以调整对齐规则：

* **注释换行宽度**：调整注释文字自动换行的最大长度。  
* **显示行号**：可选择在预览中显示或隐藏行号。  
* **大小写敏感**：设置在对齐时是否区分关键字大小写。  

---

### 示例

* **原始 SQL**

```postgresql
-- ----------------------------
-- Table structure for demo
-- ----------------------------
DROP TABLE IF EXISTS "public"."demo";
CREATE TABLE "public"."demo" (
  "id" int8 NOT NULL ,
  "tenant_id" int8 NOT NULL DEFAULT 0,
  "name" varchar(255) NOT NULL,
  "age" int4,
  "type" int2 NOT NULL,
  "ip" inet,
  "port" int4,
  "status" bool DEFAULT false,
  "usage" numeric(5,2) NOT NULL DEFAULT 0.00,
  "balance" numeric(18,2) NOT NULL DEFAULT 0.00,
  "meta" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "version" varchar(30),
  "creator" varchar(64),
  "create_time" timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updater" varchar(64),
  "update_time" timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "deleted" int2 NOT NULL DEFAULT 0,
  "remark" varchar(500)
)
;
COMMENT ON COLUMN "public"."demo"."id" IS '主键';
COMMENT ON COLUMN "public"."demo"."tenant_id" IS '租户ID';
COMMENT ON COLUMN "public"."demo"."name" IS '名称';
COMMENT ON COLUMN "public"."demo"."age" IS '年龄（0-150）';
COMMENT ON COLUMN "public"."demo"."type" IS '设备类型：1-直连 2-网关子 3-网关';
COMMENT ON COLUMN "public"."demo"."ip" IS 'IP地址';
COMMENT ON COLUMN "public"."demo"."port" IS '端口（1-65535）';
COMMENT ON COLUMN "public"."demo"."usage" IS '使用率百分比（0-100）';
COMMENT ON COLUMN "public"."demo"."balance" IS '余额（保留2位小数）';
COMMENT ON COLUMN "public"."demo"."meta" IS '扩展JSON';
COMMENT ON COLUMN "public"."demo"."version" IS '版本号（生成列）';
COMMENT ON COLUMN "public"."demo"."creator" IS '创建人';
COMMENT ON COLUMN "public"."demo"."create_time" IS '创建时间';
COMMENT ON COLUMN "public"."demo"."updater" IS '更新人';
COMMENT ON COLUMN "public"."demo"."update_time" IS '更新时间';
COMMENT ON COLUMN "public"."demo"."deleted" IS '逻辑删除';
COMMENT ON COLUMN "public"."demo"."remark" IS '描述';
COMMENT ON TABLE "public"."demo" IS '示例表';
````

* **格式化 SQL**

```postgresql
-- ----------------------------
-- Table structure for demo
-- ----------------------------
DROP TABLE IF EXISTS "public"."demo";
CREATE TABLE "public"."demo" (
    "id"          int8          NOT NULL,
    "tenant_id"   int8          NOT NULL DEFAULT 0,
    "name"        varchar(255)  NOT NULL,
    "age"         int4,
    "type"        int2          NOT NULL,
    "ip"          inet,
    "port"        int4,
    "status"      bool          DEFAULT false,
    "usage"       numeric(5,2)  NOT NULL DEFAULT 0.00,
    "balance"     numeric(18,2) NOT NULL DEFAULT 0.00,
    "meta"        jsonb         NOT NULL DEFAULT '{}'::jsonb,
    "version"     varchar(30),
    "creator"     varchar(64),
    "create_time" timestamp(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updater"     varchar(64),
    "update_time" timestamp(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deleted"     int2          NOT NULL DEFAULT 0,
    "remark"      varchar(500)
)
;
COMMENT ON COLUMN "public"."demo"."id"          IS '主键';
COMMENT ON COLUMN "public"."demo"."tenant_id"   IS '租户ID';
COMMENT ON COLUMN "public"."demo"."name"        IS '名称';
COMMENT ON COLUMN "public"."demo"."age"         IS '年龄（0-150）';
COMMENT ON COLUMN "public"."demo"."type"        IS '设备类型：1-直连 2-网关子 3-网关';
COMMENT ON COLUMN "public"."demo"."ip"          IS 'IP地址';
COMMENT ON COLUMN "public"."demo"."port"        IS '端口（1-65535）';
COMMENT ON COLUMN "public"."demo"."usage"       IS '使用率百分比（0-100）';
COMMENT ON COLUMN "public"."demo"."balance"     IS '余额（保留2位小数）';
COMMENT ON COLUMN "public"."demo"."meta"        IS '扩展JSON';
COMMENT ON COLUMN "public"."demo"."version"     IS '版本号（生成列）';
COMMENT ON COLUMN "public"."demo"."creator"     IS '创建人';
COMMENT ON COLUMN "public"."demo"."create_time" IS '创建时间';
COMMENT ON COLUMN "public"."demo"."updater"     IS '更新人';
COMMENT ON COLUMN "public"."demo"."update_time" IS '更新时间';
COMMENT ON COLUMN "public"."demo"."deleted"     IS '逻辑删除';
COMMENT ON COLUMN "public"."demo"."remark"      IS '描述';
COMMENT ON TABLE "public"."demo"                IS '示例表';
```