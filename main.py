import streamlit as st
import re
import io
import zipfile
import textwrap
from typing import Match, Dict, List, Tuple

st.set_page_config(
    page_title="SQL Alignment Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    :root {
        --primary-color: #4CAF50;
        --background-color: #1a1a1a;
        --secondary-background-color: #2e2e2e;
        --text-color: #f0f0f0;
        --font-family: 'Inter', sans-serif;
    }
    body {
        color: var(--text-color);
        background-color: var(--background-color);
        font-family: var(--font-family);
    }
    .stApp {
        background-color: var(--background-color);
    }
    .st-emotion-cache-1cypcdb {
        color: var(--text-color);
        background-color: var(--secondary-background-color);
    }
    .st-emotion-cache-13ln4j9 {
        background-color: var(--background-color);
    }
    .st-emotion-cache-1avcm0c {
        background-color: var(--secondary-background-color);
        border-radius: 12px;
        padding: 20px;
    }
    h1, h2, h3, h4, h5, h6 {
        color: var(--primary-color);
    }
    .stButton>button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 8px;
        border: none;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.3);
    }
    .stButton>button:hover {
        background-color: #66BB6A;
        transform: scale(1.05);
        transition: transform 0.2s ease-in-out;
    }
    .stCodeBlock {
        background-color: #282c34;
        color: #abb2bf;
        border-radius: 8px;
    }
    .metric-container {
        padding: 15px;
        background-color: var(--secondary-background-color);
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    .st-expander {
        background-color: var(--secondary-background-color);
        border-radius: 12px;
        padding: 10px;
    }
    .stProgress > div > div > div > div {
        background-color: var(--primary-color);
    }
</style>
""", unsafe_allow_html=True)

st.title("🔧 SQL Alignment & Java DO to SQL Tool")

with st.sidebar:
    st.header("⚙️ Configuration")
    wrap_comment_width = st.slider("Comment wrap width", 30, 120, 60, 5)
    show_line_numbers = st.checkbox("Show line numbers", value=False)
    case_sensitive = st.checkbox("Case-sensitive", value=False)

    st.markdown("---")
    st.markdown("### Java DO to SQL Settings")
    schema_name = st.text_input("Schema name", value="public")
    add_drop_table = st.checkbox("Add DROP TABLE", value=True)
    add_base_do_fields = st.checkbox("Add BaseDO fields", value=True)
    add_sequence = st.checkbox("Add sequence", value=True)
    use_camel_to_snake = st.checkbox("CamelCase to snake_case", value=True)

    st.markdown("#### Database Type")
    db_type = st.selectbox("Database", ["PostgreSQL", "MySQL", "Oracle"])

    st.markdown("---")
    st.markdown("""
    **Features:**
    - 🔄 Left: Original SQL
    - ✨ Right: Aligned SQL
    - ☕ Java DO → SQL CREATE TABLE
    - 📂 Supports batch file upload
    - 💬 COMMENT auto-wrapping
    - 🎛️ Expand/Collapse preview
    """)


def align_create_table(sql_text: str, wrap_comment_width: int, case_sensitive: bool) -> str:
    flags = re.S | re.X | (0 if case_sensitive else re.I)

    sql_text = _align_all_comments(sql_text, wrap_comment_width, flags)

    sql_text = _align_create_table_columns(sql_text, flags)

    sql_text = re.sub(
        r'(\);\s*)\n+(\s*COMMENT)',
        r'\1\n\2',
        sql_text,
        flags=re.S | re.I
    )

    return sql_text


def _align_create_table_columns(sql_text: str, flags: int) -> str:
    create_pat = re.compile(r"""
        (CREATE\s+TABLE\s+(?:
            "?\w+"?\.)?       
            "?\w+"?            
            \s*\()             
        (.*?)                  
        (\s*\)\s*;)            
    """, flags=flags)

    def align_columns_replacer(match: Match) -> str:
        raw = match.group(2)
        chunks = [seg.strip() for seg in re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', raw) if seg.strip()]

        parsed_rows = []
        for chunk in chunks:
            m = re.match(r'("([^"]+)"\s*)(\S+)(.*)', chunk)
            if m:
                full_col_part, col_name, type_, rest = m.groups()
                parsed_rows.append({'full_col': full_col_part.strip(), 'type_': type_, 'rest': rest.strip()})
            else:
                parsed_rows.append({'full_col': '', 'type_': '', 'rest': chunk.strip()})

        valid_rows = [r for r in parsed_rows if r['full_col']]

        max_full_col_len = max((len(r['full_col']) for r in valid_rows), default=0)
        max_type_len = max((len(r['type_']) for r in valid_rows), default=0)

        aligned = []
        for row in parsed_rows:
            if row['full_col']:
                line = f'    {row["full_col"].ljust(max_full_col_len)} {row["type_"].ljust(max_type_len)} {row["rest"]}'.rstrip()
            else:
                line = f'    {row["rest"]}'
            aligned.append(line)

        return match.group(1) + "\n" + ",\n".join(aligned) + match.group(3)

    return create_pat.sub(align_columns_replacer, sql_text)


def _align_all_comments(sql_text: str, wrap_comment_width: int, flags: int) -> str:
    all_comments_pat = re.compile(r"""
        (COMMENT\s+ON\s+(?:TABLE|COLUMN)\s+[^;]+?)\s+IS\s+'([^']*)';
    """, flags=flags | re.DOTALL)

    all_comment_parts = [m.group(1).strip() for m in all_comments_pat.finditer(sql_text)]

    if not all_comment_parts:
        return sql_text

    max_len = max(len(part) for part in all_comment_parts) + 2

    def repl_comm(m: Match) -> str:
        part_before_is, body = m.group(1), m.group(2)

        if '\n' not in body:
            body = "\n".join(textwrap.wrap(
                body, width=wrap_comment_width,
                break_long_words=False, break_on_hyphens=False))

        return f"{part_before_is.ljust(max_len)} IS '{body}';"

    return all_comments_pat.sub(repl_comm, sql_text)


def _clean_comment(comment_block: str) -> str:
    if not comment_block:
        return ""

    clean_text = comment_block.strip().lstrip('/*').lstrip('*').rstrip('*/').strip()

    lines = clean_text.split('\n')
    for line in lines:
        line = line.strip().lstrip('*').strip()
        if line and not line.startswith('@'):
            return line
    return ""


def camel_to_snake(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def java_type_to_sql(java_type: str, field_name: str = "", db_type: str = "PostgreSQL") -> Tuple[str, str, str]:
    if db_type == "PostgreSQL":
        type_mapping = {
            'String': 'varchar(255)',
            'Integer': 'int4',
            'int': 'int4',
            'Long': 'int8',
            'long': 'int8',
            'Double': 'numeric(10,2)',
            'double': 'numeric(10,2)',
            'Float': 'float4',
            'float': 'float4',
            'Boolean': 'int2',
            'boolean': 'int2',
            'Date': 'timestamp(6)',
            'LocalDate': 'date',
            'LocalDateTime': 'timestamp(6)',
            'LocalTime': 'time',
            'Timestamp': 'timestamp(6)',
            'BigDecimal': 'numeric(10,2)',
            'byte[]': 'bytea',
            'Byte[]': 'bytea'
        }
    else:
        type_mapping = {
            'String': 'VARCHAR(255)',
            'Integer': 'INT',
            'int': 'INT',
            'Long': 'BIGINT',
            'long': 'BIGINT',
            'Double': 'DECIMAL(10,2)',
            'double': 'DECIMAL(10,2)',
            'Float': 'FLOAT',
            'float': 'FLOAT',
            'Boolean': 'TINYINT(1)',
            'boolean': 'TINYINT(1)',
            'Date': 'DATETIME',
            'LocalDate': 'DATE',
            'LocalDateTime': 'DATETIME',
            'LocalTime': 'TIME',
            'Timestamp': 'TIMESTAMP',
            'BigDecimal': 'DECIMAL(10,2)',
            'byte[]': 'BLOB',
            'Byte[]': 'BLOB'
        }

    java_type = re.sub(r'<.*?>', '', java_type).strip()

    sql_type = type_mapping.get(java_type, 'varchar(255)' if db_type == "PostgreSQL" else 'VARCHAR(255)')
    constraints = ""
    default_value = ""

    field_lower = field_name.lower()

    if field_lower in ['id', 'uid']:
        if db_type == "PostgreSQL":
            sql_type = 'int8'
            constraints = 'NOT NULL PRIMARY KEY'
        else:
            sql_type = 'BIGINT'
            constraints = 'AUTO_INCREMENT PRIMARY KEY'
    elif field_lower == 'tenant_id':
        if db_type == "PostgreSQL":
            sql_type = 'int8'
        constraints = 'NOT NULL'
        default_value = 'DEFAULT 0'
    elif 'email' in field_lower:
        sql_type = 'varchar(100)' if db_type == "PostgreSQL" else 'VARCHAR(100)'
    elif 'phone' in field_lower:
        sql_type = 'varchar(20)' if db_type == "PostgreSQL" else 'VARCHAR(20)'
    elif 'password' in field_lower:
        sql_type = 'varchar(128)' if db_type == "PostgreSQL" else 'VARCHAR(128)'
    elif field_lower in ['name', 'code']:
        if field_lower == 'code':
            sql_type = 'varchar(100)' if db_type == "PostgreSQL" else 'VARCHAR(100)'
        constraints = 'NOT NULL'
    elif field_lower == 'description':
        sql_type = 'varchar(500)' if db_type == "PostgreSQL" else 'VARCHAR(500)'
    elif field_lower in ['status', 'sort']:
        if db_type == "PostgreSQL":
            sql_type = 'int4'
        constraints = 'NOT NULL'
        default_value = 'DEFAULT 0'
    elif field_lower in ['creator', 'updater']:
        sql_type = 'varchar(64)' if db_type == "PostgreSQL" else 'VARCHAR(64)'
    elif field_lower in ['create_time', 'update_time']:
        if db_type == "PostgreSQL":
            sql_type = 'timestamp(6)'
        constraints = 'NOT NULL'
        default_value = 'DEFAULT CURRENT_TIMESTAMP'
    elif field_lower == 'deleted':
        if db_type == "PostgreSQL":
            sql_type = 'int2'
        constraints = 'NOT NULL'
        default_value = 'DEFAULT 0'

    return sql_type, constraints, default_value


def parse_java_class(java_code: str) -> Dict:
    result = {
        'class_name': '',
        'fields': [],
        'class_comment': '',
        'table_name': '',
        'key_sequence': ''
    }

    class_match = re.search(r'(?:public\s+)?class\s+(\w+)', java_code)
    if class_match:
        result['class_name'] = class_match.group(1)

    table_name_match = re.search(r'@TableName\s*\(\s*"([^"]+)"\s*\)', java_code)
    if table_name_match:
        result['table_name'] = table_name_match.group(1)

    key_sequence_match = re.search(r'@KeySequence\s*\(\s*"([^"]+)"\s*\)', java_code)
    if key_sequence_match:
        result['key_sequence'] = key_sequence_match.group(1)

    class_comment_match = re.search(r'/\*\*(.*?)\*/\s*(?:@\w+[^\n]*\n\s*)*public\s+class', java_code, re.DOTALL)
    if class_comment_match:
        raw_comment = class_comment_match.group(1)
        comment = _clean_comment(raw_comment)
        result['class_comment'] = comment

    field_pattern = re.compile(r'''
        (\s*/{1,2}\*[\s\S]*?\*/\s*)? 
        (?:@\w+[^\n]*\n\s*)* 
        (?:private|public|protected)?\s*
        (?:static\s+)?(?:final\s+)?
        (\w+(?:<[^>]+>)?)\s+
        (\w+)
        (?:\s*=\s*[^;]+)?
        \s*;
    ''', re.VERBOSE | re.MULTILINE | re.DOTALL)

    for match in field_pattern.finditer(java_code):
        comment_block = match.group(1)
        field_type = match.group(2).strip()
        field_name = match.group(3).strip()

        comment = _clean_comment(comment_block) if comment_block else ''

        result['fields'].append({
            'name': field_name,
            'type': field_type,
            'comment': comment
        })
    return result


def java_do_to_sql(java_code: str, schema_name: str = "public",
                   add_drop_table: bool = True, add_base_do_fields: bool = True,
                   add_sequence: bool = True, use_camel_to_snake: bool = True,
                   db_type: str = "PostgreSQL") -> str:
    parsed = parse_java_class(java_code)

    if not parsed['class_name']:
        return "-- Error: Could not parse Java class"

    table_name = parsed['table_name'] if parsed['table_name'] else camel_to_snake(parsed['class_name'])
    full_table_name = f'"{schema_name}"."{table_name}"' if db_type == "PostgreSQL" else f"`{table_name}`"

    sql_lines = []

    if add_drop_table:
        sql_lines.append("-- ------------------------------")
        sql_lines.append(f"-- Table structure for {table_name}")
        sql_lines.append("-- ------------------------------")
        sql_lines.append(f'DROP TABLE IF EXISTS {full_table_name};')

    sql_lines.append(f'CREATE TABLE {full_table_name} (')

    all_fields = []
    all_comments = []

    for field in parsed['fields']:
        field_name = field['name']
        sql_field_name = camel_to_snake(field_name) if use_camel_to_snake else field_name.lower()

        sql_type, constraints, default_value = java_type_to_sql(field['type'], sql_field_name, db_type)

        field_parts = {
            'name': f'"{sql_field_name}"' if db_type == "PostgreSQL" else f"`{sql_field_name}`",
            'type': sql_type,
            'constraints': constraints,
            'default': default_value
        }
        all_fields.append(field_parts)

        if field['comment']:
            if sql_field_name == 'id':
                all_comments.append((sql_field_name, 'ID'))
            else:
                all_comments.append((sql_field_name, field['comment']))

    if add_base_do_fields:
        base_fields = [
            ('tenantId', 'Long', 'Tenant ID'),
            ('creator', 'String', 'Creator'),
            ('createTime', 'LocalDateTime', 'Create Time'),
            ('updater', 'String', 'Updater'),
            ('updateTime', 'LocalDateTime', 'Update Time'),
            ('deleted', 'Boolean', 'Logical Delete')
        ]

        for field_name, field_type, comment in base_fields:
            sql_field_name = camel_to_snake(field_name) if use_camel_to_snake else field_name.lower()
            sql_type, constraints, default_value = java_type_to_sql(field_type, sql_field_name, db_type)

            if not any(f['name'] == f'"{sql_field_name}"' for f in all_fields):
                field_parts = {
                    'name': f'"{sql_field_name}"' if db_type == "PostgreSQL" else f"`{sql_field_name}`",
                    'type': sql_type,
                    'constraints': constraints,
                    'default': default_value
                }
                all_fields.append(field_parts)
                all_comments.append((sql_field_name, comment))

    max_name_len = max(len(f['name']) for f in all_fields) if all_fields else 0
    max_type_len = max(len(f['type']) for f in all_fields) if all_fields else 0

    field_definitions = []
    for field_parts in all_fields:
        line = f"    {field_parts['name'].ljust(max_name_len)} {field_parts['type'].ljust(max_type_len)}"

        if field_parts['constraints']:
            line += f" {field_parts['constraints']}"
        if field_parts['default']:
            line += f" {field_parts['default']}"

        field_definitions.append(line.rstrip())

    sql_lines.append(',\n'.join(field_definitions))
    sql_lines.append(');')

    comment_lines = []
    if db_type == "PostgreSQL":
        for sql_field_name, comment_text in all_comments:
            comment_line = f'COMMENT ON COLUMN {full_table_name}."{sql_field_name}" IS \'{comment_text}\';'
            comment_lines.append(comment_line)
        if parsed['class_comment']:
            table_comment = parsed['class_comment']
            if 'DO' in table_comment:
                table_comment = table_comment.replace(' DO', '').strip()
            if not table_comment.endswith('table'):
                table_comment += ' table'
            table_comment_line = f'COMMENT ON TABLE {full_table_name} IS \'{table_comment}\';'
            comment_lines.append(table_comment_line)
    else:
        for sql_field_name, comment_text in all_comments:
            comment_line = f'ALTER TABLE `{table_name}` MODIFY COLUMN `{sql_field_name}` {field_parts["type"]} COMMENT \'{comment_text}\';'
            comment_lines.append(comment_line)
        if parsed['class_comment']:
            table_comment = parsed['class_comment']
            if 'DO' in table_comment:
                table_comment = table_comment.replace(' DO', '').strip()
            if not table_comment.endswith('table'):
                table_comment += ' table'
            table_comment_line = f'ALTER TABLE `{table_name}` COMMENT = \'{table_comment}\';'
            comment_lines.append(table_comment_line)

    final_sql = '\n'.join(sql_lines)
    if comment_lines:
        final_sql += '\n' + '\n'.join(comment_lines)

    if add_sequence and db_type == "PostgreSQL" and parsed['key_sequence']:
        sequence_name = parsed['key_sequence']
        final_sql += f'\n\nDROP SEQUENCE IF EXISTS {sequence_name};'
        final_sql += f'\nCREATE SEQUENCE {sequence_name}\n    START 1;'

    return final_sql


def get_stats(sql: str) -> dict:
    lines = sql.splitlines()
    return {
        'total': len(lines),
        'non_empty': len([l for l in lines if l.strip()]),
        'comments': len([l for l in lines if
                         l.strip().startswith('--') or l.strip().startswith('COMMENT') or l.strip().startswith(
                             'ALTER TABLE')]),
        'fields': sql.upper().count('NOT NULL') + sql.upper().count('DEFAULT')
    }


tab1, tab2, tab3 = st.tabs(["📝 Single SQL", "☕ Java DO to SQL", "📂 Batch Files"])

with tab1:
    st.subheader("Single SQL Alignment & Preview")
    sql_in = st.text_area("Enter your SQL", height=320, placeholder="CREATE TABLE ...")

    if sql_in.strip():
        aligned = align_create_table(sql_in, wrap_comment_width, case_sensitive)
        stats = get_stats(sql_in)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="metric-container"><h5>Total Lines</h5><h3>{stats["total"]}</h3></div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div class="metric-container"><h5>Fields</h5><h3>{stats["fields"]}</h3></div>',
                        unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-container"><h5>Effective Lines</h5><h3>{stats["non_empty"]}</h3></div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div class="metric-container"><h5>Comment Lines</h5><h3>{stats["comments"]}</h3></div>',
                        unsafe_allow_html=True)

        with st.expander("Left-Right Comparison", expanded=True):
            lcol, rcol = st.columns(2)
            with lcol:
                st.markdown("#### 📄 Original SQL")
                code = "\n".join(
                    f"{i + 1:3d}: {l}" for i, l in enumerate(sql_in.splitlines())) if show_line_numbers else sql_in
                st.code(code, language='sql')
            with rcol:
                st.markdown("#### ✨ Aligned SQL")
                code = "\n".join(
                    f"{i + 1:3d}: {l}" for i, l in enumerate(aligned.splitlines())) if show_line_numbers else aligned
                st.code(code, language='sql')

        st.download_button("📥 Download Aligned SQL", aligned, "aligned.sql", "text/sql")
        report = f"-- Alignment Report\n-- Original Lines: {stats['total']}\n{aligned}"
        st.download_button("📊 Download Report", report, "report.sql", "text/sql")

with tab2:
    st.subheader("☕ Java Domain Object to SQL")
    st.markdown("Paste your Java DO class below to generate CREATE TABLE statement")

    java_example = """public class"""

    java_code = st.text_area(
        "Java DO Class Code",
        height=300,
        placeholder=java_example
    )

    if java_code.strip():
        try:
            generated_sql = java_do_to_sql(
                java_code,
                schema_name,
                add_drop_table,
                add_base_do_fields,
                add_sequence,
                use_camel_to_snake,
                db_type
            )

            if not generated_sql.startswith("-- Error"):
                aligned_sql = align_create_table(generated_sql, wrap_comment_width, case_sensitive)

                with st.expander("Java to SQL Conversion Result", expanded=True):
                    lcol, rcol = st.columns(2)
                    with lcol:
                        st.markdown("#### ☕ Java DO Class")
                        st.code(java_code, language='java')
                    with rcol:
                        st.markdown("#### 🗃️ Generated SQL")
                        display_sql = "\n".join(
                            f"{i + 1:3d}: {l}" for i, l in enumerate(aligned_sql.splitlines())
                        ) if show_line_numbers else aligned_sql
                        st.code(display_sql, language='sql')

                stats = get_stats(aligned_sql)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(
                        f'<div class="metric-container"><h5>Generated Lines</h5><h3>{stats["total"]}</h3></div>',
                        unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="metric-container"><h5>Fields</h5><h3>{stats["fields"]}</h3></div>',
                                 unsafe_allow_html=True)
                with col3:
                    parsed = parse_java_class(java_code)
                    st.markdown(
                        f'<div class="metric-container"><h5>Java Fields</h5><h3>{len(parsed["fields"])}</h3></div>',
                        unsafe_allow_html=True)

                parsed_info = parse_java_class(java_code)
                table_name = parsed_info['table_name'] if parsed_info['table_name'] else camel_to_snake(
                    parsed_info['class_name'])
                filename = f"{table_name}.sql"
                st.download_button("📥 Download Generated SQL", aligned_sql, filename, "text/sql")

            else:
                st.error(generated_sql)
        except Exception as e:
            st.error(f"Error converting Java to SQL: {str(e)}")

with tab3:
    st.subheader("📂 Batch SQL Files")
    files = st.file_uploader("Select .sql/.txt files", type=["sql", "txt"], accept_multiple_files=True)

    download_prefix = st.text_input("Download file prefix", value="aligned_")

    if files:
        st.success(f"Selected {len(files)} file(s)")
        if st.button("🚀 Start Batch Processing", type="primary"):

            progress_bar = st.progress(0)
            status_text = st.empty()

            summary_report = "--- Batch Processing Summary ---\n"
            processed_count = 0

            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for i, f in enumerate(files):
                    status_text.info(f"Processing file: {f.name}...")
                    try:
                        raw = f.read().decode(errors="ignore")
                        aligned = align_create_table(raw, wrap_comment_width, case_sensitive)

                        file_stats = get_stats(raw)
                        aligned_filename = f"{download_prefix}{f.name}"
                        zf.writestr(aligned_filename, aligned)

                        summary_report += (
                            f"\nFile: {f.name}\n"
                            f"  - Original Lines: {file_stats['total']}\n"
                            f"  - Aligned File Name: {aligned_filename}\n"
                        )
                        processed_count += 1

                    except Exception as e:
                        summary_report += f"\nFile: {f.name}\n  - Error processing file: {e}\n"

                    progress_bar.progress((i + 1) / len(files))

            progress_bar.empty()
            status_text.success("✅ Batch processing complete!")

            st.markdown("---")
            st.subheader("Batch Processing Results")
            st.info(f"Successfully processed {processed_count} out of {len(files)} files.")

            st.download_button("📦 Download ZIP", zip_buf.getvalue(), f"{download_prefix}sql_files.zip",
                               "application/zip")
            st.download_button("📝 Download Summary Report", summary_report, "batch_summary_report.txt", "text/plain")

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#666;font-size:0.8em;'>SQL Alignment & Java DO Conversion Tool © 2025</div>",
    unsafe_allow_html=True)