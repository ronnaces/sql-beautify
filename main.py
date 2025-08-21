import streamlit as st
import re
import io
import zipfile
import textwrap
from typing import Match

# ---------- 页面配置 ----------
st.set_page_config(
    page_title="SQL 对齐对比工具",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 使用自定义 CSS 注入来优化视觉效果
st.markdown("""
<style>
    /* 全局样式 */
    :root {
        --primary-color: #4CAF50; /* 绿色系主色 */
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
    /* Streamlit 核心组件样式 */
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

st.title("🔧 SQL Alignment & Preview Tool")

# ---------- 侧边栏配置 ----------
with st.sidebar:
    st.header("⚙️ Configuration")
    wrap_comment_width = st.slider("Comment wrap width", 30, 120, 60, 5)
    show_line_numbers = st.checkbox("Show line numbers", value=False)
    case_sensitive = st.checkbox("Case-sensitive", value=False)

    st.markdown("---")
    st.markdown("""
    - 🔄 Left: Original SQL
    - ✨ Right: Aligned SQL
    - 📂 Supports batch file upload
    - 💬 COMMENT auto-wrapping
    - 🎛️ Expand/Collapse preview
    """)


def align_create_table(sql_text: str, wrap_comment_width: int, case_sensitive: bool) -> str:
    """
    Main alignment function that orchestrates the alignment of CREATE TABLE and COMMENT statements.
    """
    flags = re.S | re.X | (0 if case_sensitive else re.I)

    # 1. Align all COMMENT statements (ON TABLE and ON COLUMN) together.
    sql_text = _align_all_comments(sql_text, wrap_comment_width, flags)

    # 2. Align the column definitions within the CREATE TABLE statement.
    sql_text = _align_create_table_columns(sql_text, flags)

    # 3. Final cleanup: remove extra newlines between CREATE TABLE and COMMENT statements.
    sql_text = re.sub(
        r'(\);\s*)\n+(\s*COMMENT)',
        r'\1\n\2',
        sql_text,
        flags=re.S | re.I
    )

    return sql_text


def _align_create_table_columns(sql_text: str, flags: int) -> str:
    """
    Aligns the column definitions within a CREATE TABLE statement.
    """
    create_pat = re.compile(r"""
        (CREATE\s+TABLE\s+(?:
            "?[^"]+"?\.)?       # Optional schema name
            "?[^"]+"?           # Table name
            \s*\()              # Opening parenthesis
        (.*?)                   # Capture all column definitions
        (\s*\)\s*;)             # Closing parenthesis and semicolon
    """, flags=flags)

    def align_columns_replacer(match: Match) -> str:
        raw = match.group(2)
        # Robustly split columns by comma, ignoring commas inside quotes.
        chunks = [seg.strip() for seg in re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', raw) if seg.strip()]

        # Parse each column line into its components.
        parsed_rows = []
        for chunk in chunks:
            m = re.match(r'("([^"]+)"\s*)(\S+)(.*)', chunk)
            if m:
                full_col_part, col_name, type_, rest = m.groups()
                parsed_rows.append({'full_col': full_col_part.strip(), 'type_': type_, 'rest': rest.strip()})
            else:
                parsed_rows.append({'full_col': '', 'type_': '', 'rest': chunk.strip()})

        max_full_col_len = max((len(r['full_col']) for r in parsed_rows), default=0)
        max_type_len = max((len(r['type_']) for r in parsed_rows), default=0)

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
    """
    Aligns both COMMENT ON TABLE and COMMENT ON COLUMN statements to a common IS keyword position.
    """
    all_comments_pat = re.compile(r"""
        ((?:COMMENT\s+ON\s+(?:
            TABLE\s+"?[^"]+"?(?:\."?[^"]+"?)?|     # Matches COMMENT ON TABLE
            COLUMN\s+"?[^"]+"?\.+"?[^"]+"?\.+"?[^"]+"?    # Matches COMMENT ON COLUMN
        ))\s+)IS\s+\'([^\']*)\';
    """, flags=flags)

    all_comment_parts = [m.group(1) for m in all_comments_pat.finditer(sql_text)]

    if not all_comment_parts:
        return sql_text

    max_len = max(len(part) for part in all_comment_parts)

    def repl_comm(m: Match) -> str:
        part_before_is, body = m.group(1), m.group(2)
        if '\n' not in body:
            body = "\n".join(textwrap.wrap(
                body, width=wrap_comment_width,
                break_long_words=False, break_on_hyphens=False))
        return f"{part_before_is.ljust(max_len)}IS '{body}';"

    return all_comments_pat.sub(repl_comm, sql_text)


# ---------- 统计 ----------
def get_stats(sql: str) -> dict:
    """Calculates statistics for the SQL text."""
    lines = sql.splitlines()
    return {
        'total': len(lines),
        'non_empty': len([l for l in lines if l.strip()]),
        'comments': len([l for l in lines if l.strip().startswith('--')]),
        'fields': sql.upper().count('NOT NULL') + sql.upper().count('DEFAULT')
    }


# ---------- 主界面 ----------
tab1, tab2 = st.tabs(["📝 Single SQL", "📂 Batch Files"])

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
    st.subheader("📂 Batch SQL Files")
    files = st.file_uploader("Select .sql/.txt", type=["sql", "txt"], accept_multiple_files=True)

    # 新增可配置的文件前缀
    download_prefix = st.text_input("Download file prefix", value="aligned_")

    if files:
        st.success(f"Selected {len(files)} file(s)")
        if st.button("🚀 Start Batch Processing", type="primary"):

            # 初始化进度条和状态信息
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

            # 下载按钮
            st.download_button("📦 Download ZIP", zip_buf.getvalue(), f"{download_prefix}sql_files.zip",
                               "application/zip")
            st.download_button("📝 Download Summary Report", summary_report, "batch_summary_report.txt", "text/plain")

st.markdown("---")
st.markdown("<div style='text-align:center;color:#666;font-size:0.8em;'>SQL Alignment Tool © 2025</div>",
            unsafe_allow_html=True)
