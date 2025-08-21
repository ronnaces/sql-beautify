# SQL 对齐与预览工具

欢迎使用 **SQL 对齐与预览工具**！这个应用程序旨在帮助您快速、高效地格式化和整理 SQL 代码，特别是 `CREATE TABLE` 语句。通过简洁的界面和强大的对齐引擎，您可以轻松地将杂乱无章的代码变得清晰易读，从而提升开发和维护效率。

---

### 主要功能

#### ✨ **单条 SQL 对齐**

* **实时预览**：在左侧文本框中输入或粘贴 SQL 代码，右侧的预览区域会**实时自动**显示格式化后的结果。
* **左右对比**：通过分栏显示原始代码和对齐后的代码，您可以直观地看到格式化前后的差异。
* **统计报告**：自动分析并显示代码的行数、有效行数、注释行数和字段数，让您对代码概况一目了然。
* **下载选项**：一键下载对齐后的 SQL 文件或包含对齐报告的完整文件。

#### 📂 **批量处理**

* **文件上传**：支持同时上传多个 `.sql` 或 `.txt` 文件。
* **处理进度条**：在处理大量文件时，页面会显示**实时进度条**和**状态提示**，让您清楚地知道处理进度。
* **可配置前缀**：您可以自定义下载文件的文件名前缀，方便批量管理。
* **处理摘要报告**：处理完成后，您可以下载一个详细的文本报告，其中包含了每个文件的处理结果和潜在错误。
* **批量打包下载**：所有处理后的文件都会被打包成一个 ZIP 文件供您下载，节省您的时间。

---

### 配置选项

在左侧的侧边栏，您可以找到一系列选项来定制对齐行为：

* **注释换行宽度**：调整注释文本自动换行的最大字符数，以适应您的代码风格。
* **显示行号**：在代码预览中显示或隐藏行号。
* **大小写敏感**：选择对齐时是否区分关键字的大小写。

### 示例

- 原始的SQL

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
```

- 格式化后的SQL

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

希望这个 `README` 能对您有所帮助！