import io
import json
import re
import csv
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


# ============================================================
# إعداد الصفحة
# ============================================================
st.set_page_config(
    page_title="منصة تحليلات الجودة التعليمية",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;600;700;800&display=swap');

    :root {
        --primary: #136f63;
        --primary-dark: #0b4f47;
        --secondary: #d9a441;
        --ink: #16302d;
        --muted: #627773;
        --surface: #ffffff;
        --soft: #f2f8f6;
        --line: #dce9e6;
    }

    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: "Tajawal", sans-serif;
    }
    [data-testid="stAppViewContainer"] {
        direction: rtl;
        background:
          radial-gradient(circle at 12% 8%, rgba(217,164,65,.10), transparent 24rem),
          linear-gradient(180deg, #f7fbfa 0%, #ffffff 35%);
        color: var(--ink);
    }
    [data-testid="stMainBlockContainer"] {max-width: 1320px; padding-top: 1.5rem;}
    [data-testid="stSidebar"] {direction: rtl; border-left: 1px solid var(--line);}
    [data-testid="stSidebar"] > div {background: #f7fbfa;}
    h1, h2, h3 {color: var(--ink); letter-spacing: -.02em;}
    h2 {border-right: 4px solid var(--secondary); padding-right: .7rem; margin-top: 2rem;}

    .hero {
        position: relative; overflow: hidden; color: white;
        background: linear-gradient(125deg, #0b4f47 0%, #136f63 58%, #238c7d 100%);
        border-radius: 26px; padding: 2.35rem 2.5rem; margin-bottom: 1.35rem;
        box-shadow: 0 18px 45px rgba(11,79,71,.18);
    }
    .hero:after {
        content:""; position:absolute; width:260px; height:260px; left:-65px; top:-105px;
        border: 42px solid rgba(255,255,255,.07); border-radius:50%;
    }
    .hero-kicker {font-size:.88rem; font-weight:700; color:#ffe6ac; margin-bottom:.55rem;}
    .hero h1 {color:white; margin:0 0 .55rem; font-size:clamp(2rem,4vw,3.25rem); line-height:1.15;}
    .hero p {margin:0; color:#e5f4f1; font-size:1.08rem; max-width:760px;}
    .hero-badges {display:flex; gap:.55rem; flex-wrap:wrap; margin-top:1.2rem;}
    .hero-badge {background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.2); padding:.38rem .75rem; border-radius:99px; font-size:.82rem;}

    .feature-grid {display:grid; grid-template-columns:repeat(3,1fr); gap:.8rem; margin:.8rem 0 1.2rem;}
    .feature-card {background:white; border:1px solid var(--line); border-radius:17px; padding:1rem 1.1rem; box-shadow:0 6px 20px rgba(22,48,45,.04);}
    .feature-card b {display:block; color:var(--primary-dark); margin-bottom:.2rem;}
    .feature-card span {font-size:.87rem; color:var(--muted);}

    [data-testid="stFileUploader"] {background:white; border:1px dashed #7bb9ae; border-radius:20px; padding:1rem; box-shadow:0 8px 28px rgba(19,111,99,.07);}
    [data-testid="stFileUploaderDropzone"] {background:var(--soft); border-radius:14px; min-height:135px;}
    [data-testid="stMetric"] {background:white; border:1px solid var(--line); border-radius:16px; padding:1rem; box-shadow:0 5px 18px rgba(22,48,45,.04);}
    [data-testid="stMetricValue"] {color:var(--primary-dark); font-weight:800;}
    [data-testid="stDataFrame"] {border:1px solid var(--line); border-radius:14px; overflow:hidden;}
    [data-testid="stExpander"] {background:white; border:1px solid var(--line); border-radius:15px;}
    .stButton > button, .stDownloadButton > button {
        border-radius:12px; min-height:2.8rem; font-weight:700; border:1px solid var(--primary);
    }
    .stDownloadButton > button {background:var(--primary); color:white; width:100%;}
    .stDownloadButton > button:hover {background:var(--primary-dark); color:white; border-color:var(--primary-dark);}
    .privacy-note {background:#fffaf0; border:1px solid #f0d69b; color:#6f5317; border-radius:13px; padding:.75rem .9rem; font-size:.85rem; margin:.7rem 0 1rem;}
    .step {display:flex; gap:.65rem; align-items:flex-start; margin:.7rem 0; color:var(--muted); font-size:.88rem;}
    .step-num {min-width:25px; height:25px; display:grid; place-items:center; border-radius:50%; background:#dcefeb; color:var(--primary-dark); font-weight:800;}
    .footer {text-align:center; color:var(--muted); font-size:.8rem; padding:2.5rem 0 1rem;}
    @media (max-width: 760px) {
        [data-testid="stMainBlockContainer"] {padding:1rem .75rem;}
        .hero {padding:1.6rem 1.25rem; border-radius:19px;}
        .feature-grid {grid-template-columns:1fr;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
      <div class="hero-kicker">EDUCATIONAL QUALITY ANALYTICS</div>
      <h1>منصة تحليلات الجودة التعليمية</h1>
      <p>حوّل ملفات الاستبانات إلى مؤشرات جودة قابلة للقراءة، مع فحص البيانات والتحليل الوصفي وقياس الثبات الداخلي.</p>
      <div class="hero-badges">
        <span class="hero-badge">قراءة ذكية للملفات</span>
        <span class="hero-badge">استبعاد المعرّفات</span>
        <span class="hero-badge">تقارير Excel</span>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### دليل الاستخدام")
    st.markdown(
        """
        <div class="step"><span class="step-num">1</span><span>ارفع ملف الاستبانة أو ملف النتائج.</span></div>
        <div class="step"><span class="step-num">2</span><span>راجع نوع البيانات الذي اكتشفته المنصة.</span></div>
        <div class="step"><span class="step-num">3</span><span>تحقق من الأسئلة والمعرّفات المستبعدة.</span></div>
        <div class="step"><span class="step-num">4</span><span>راجع المؤشرات ونزّل تقرير Excel.</span></div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("#### الصيغ المدعومة")
    st.caption("Excel · CSV · TSV · ODS · PDF · Word · TXT · JSON · XML · Parquet · HTML")
    st.info("أفضل نتيجة تحليلية تتحقق عندما تكون الاستجابات في جدول واضح: صف لكل مشارك وعمود لكل سؤال.")


# ============================================================
# ثوابت عامة
# ============================================================
SUPPORTED_EXTENSIONS = [
    "xlsx", "xls", "xlsm",
    "csv", "tsv",
    "ods",
    "pdf",
    "docx",
    "txt",
    "json",
    "xml",
    "parquet",
    "html", "htm",
]

LIKERT_TOKENS = [
    "strongly agree", "agree", "neutral", "disagree", "strongly disagree",
    "very satisfied", "satisfied", "dissatisfied", "very dissatisfied",
    "excellent", "very good", "good", "fair", "poor",
    "موافق بشدة", "موافق", "محايد", "غير موافق", "غير موافق بشدة",
    "راض جدا", "راض جدًا", "راض", "محايد", "غير راض", "غير راض جدا", "غير راض جدًا",
    "ممتاز", "جيد جدا", "جيد جدًا", "جيد", "مقبول", "ضعيف",
]

AGGREGATE_TOKENS = [
    "mean", "average", "avg", "median", "std", "stdev", "sd",
    "variance", "percentage", "percent", "%", "count", "frequency",
    "satisfaction", "rate",
    "المتوسط", "المعدل", "الوسيط", "الانحراف", "التباين",
    "النسبة", "نسبة", "التكرار", "العدد", "الرضا",
]

QUESTION_TOKENS = [
    "question", "item", "statement", "survey item", "q",
    "السؤال", "العبارة", "البند", "الفقرة",
]

IDENTIFIER_TOKENS = [
    "id", "participant_id", "student_id", "respondent_id", "record_id",
    "email", "phone", "mobile", "name", "username",
    "رقم", "معرف", "الرقم الجامعي", "رقم الطالب", "رقم المشارك",
    "البريد", "الجوال", "الهاتف", "الاسم",
]


# ============================================================
# أدوات مساعدة
# ============================================================
def normalize_text(value) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def clean_numeric_series(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace("٪", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.replace("،", ".", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace("٫", ".", regex=False)
        .str.replace("−", "-", regex=False)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def make_unique_columns(columns):
    seen = {}
    result = []
    for col in columns:
        name = str(col).strip() if str(col).strip() else "Unnamed"
        if name not in seen:
            seen[name] = 0
            result.append(name)
        else:
            seen[name] += 1
            result.append(f"{name}_{seen[name]}")
    return result


def tidy_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")

    if df.empty:
        return df

    df.columns = make_unique_columns(df.columns)

    # إزالة أعمدة Unnamed الفارغة غالبًا
    drop_cols = []
    for col in df.columns:
        if normalize_text(col).startswith("unnamed"):
            if df[col].isna().mean() >= 0.95:
                drop_cols.append(col)
    if drop_cols:
        df = df.drop(columns=drop_cols)

    return df.reset_index(drop=True)


def try_promote_first_row_to_header(df: pd.DataFrame) -> pd.DataFrame:
    """
    محاولة ذكية لترقية أول صف إلى أسماء أعمدة عندما تكون الأعمدة الحالية
    أرقامًا أو Unnamed.
    """
    if df.empty or len(df) < 2:
        return df

    current_cols = [normalize_text(c) for c in df.columns]
    suspicious_headers = sum(
        c.startswith("unnamed") or c.isdigit() or c in {"0", "1", "2", "3", "4", "5"}
        for c in current_cols
    )

    first_row = df.iloc[0]
    first_non_null = first_row.notna().sum()
    first_textish = sum(
        isinstance(v, str) and len(v.strip()) > 0
        for v in first_row.dropna().tolist()
    )

    if (
        suspicious_headers >= max(1, len(df.columns) // 2)
        and first_non_null >= max(2, len(df.columns) // 2)
        and first_textish >= max(1, first_non_null // 2)
    ):
        new_df = df.iloc[1:].copy()
        new_df.columns = make_unique_columns(first_row.astype(str).tolist())
        return tidy_dataframe(new_df)

    return df


def detect_encoding(raw_bytes: bytes) -> str:
    for enc in ["utf-8-sig", "utf-8", "cp1256", "windows-1252", "latin1"]:
        try:
            raw_bytes.decode(enc)
            return enc
        except Exception:
            pass
    return "utf-8"


def detect_delimiter(text_sample: str, default=",") -> str:
    try:
        dialect = csv.Sniffer().sniff(text_sample, delimiters=[",", ";", "\t", "|"])
        return dialect.delimiter
    except Exception:
        return default


def looks_like_identifier(column_name: str, series: pd.Series) -> bool:
    name = normalize_text(column_name)

    name_suspicious = (
        any(token in name for token in IDENTIFIER_TOKENS)
        or bool(re.search(r"(^|[_\s-])id($|[_\s-])", name))
    )

    numeric = pd.to_numeric(series, errors="coerce").dropna()

    if numeric.empty:
        return name_suspicious

    unique_ratio = numeric.nunique() / max(len(numeric), 1)
    sequential = False

    if len(numeric) >= 3:
        values = np.sort(numeric.unique())
        if len(values) >= 3:
            diffs = np.diff(values)
            sequential = np.allclose(diffs, 1)

    # لا نعتبر العمود معرفًا فقط لأنه فريد إذا كانت قيمه تبدو كمقياس قصير.
    looks_like_small_scale = (
        numeric.nunique() <= 10
        and numeric.min() >= 0
        and numeric.max() <= 10
    )

    return name_suspicious or (unique_ratio >= 0.95 and not looks_like_small_scale) or sequential


def is_likert_column_name(column_name: str) -> bool:
    name = normalize_text(column_name)
    return any(token in name for token in LIKERT_TOKENS)


def is_aggregate_column_name(column_name: str) -> bool:
    name = normalize_text(column_name)
    return any(token in name for token in AGGREGATE_TOKENS)


def is_question_column_name(column_name: str) -> bool:
    name = normalize_text(column_name)
    return any(token == name or token in name for token in QUESTION_TOKENS)


def convert_numeric_candidates(df: pd.DataFrame, threshold: float = 0.70) -> pd.DataFrame:
    converted = df.copy()

    for column in converted.columns:
        original_non_missing = converted[column].notna().sum()
        if original_non_missing == 0:
            continue

        numeric_series = clean_numeric_series(converted[column])
        numeric_non_missing = numeric_series.notna().sum()
        ratio = numeric_non_missing / original_non_missing

        if ratio >= threshold:
            converted[column] = numeric_series

    return converted


# ============================================================
# قراءة الملفات
# ============================================================
def read_excel_like(uploaded_file, extension: str):
    uploaded_file.seek(0)

    if extension == "ods":
        excel = pd.ExcelFile(uploaded_file, engine="odf")
    elif extension == "xls":
        excel = pd.ExcelFile(uploaded_file, engine="xlrd")
    else:
        excel = pd.ExcelFile(uploaded_file)

    candidates = {}
    for sheet in excel.sheet_names:
        try:
            df = pd.read_excel(excel, sheet_name=sheet)
            df = tidy_dataframe(df)
            df = try_promote_first_row_to_header(df)
            if not df.empty:
                candidates[f"Sheet: {sheet}"] = df
        except Exception:
            continue

    return candidates, None


def read_csv_like(uploaded_file, extension: str):
    uploaded_file.seek(0)
    raw = uploaded_file.read()
    encoding = detect_encoding(raw)
    text = raw.decode(encoding, errors="replace")

    delimiter = "\t" if extension == "tsv" else detect_delimiter(text[:5000], default=",")
    df = pd.read_csv(io.StringIO(text), sep=delimiter)
    df = tidy_dataframe(df)
    df = try_promote_first_row_to_header(df)

    return {"Data": df}, f"Encoding: {encoding} | Delimiter: {repr(delimiter)}"


def read_json_file(uploaded_file):
    uploaded_file.seek(0)
    raw = uploaded_file.read()
    encoding = detect_encoding(raw)
    obj = json.loads(raw.decode(encoding, errors="replace"))

    candidates = {}

    if isinstance(obj, list):
        try:
            candidates["JSON records"] = tidy_dataframe(pd.json_normalize(obj))
        except Exception:
            candidates["JSON data"] = tidy_dataframe(pd.DataFrame(obj))

    elif isinstance(obj, dict):
        # محاولة تحويل القاموس كاملًا
        try:
            df = pd.json_normalize(obj)
            if not df.empty:
                candidates["JSON object"] = tidy_dataframe(df)
        except Exception:
            pass

        # البحث عن قوائم داخلية تصلح كجداول
        for key, value in obj.items():
            if isinstance(value, list) and value:
                try:
                    df = pd.json_normalize(value)
                    if not df.empty:
                        candidates[f"JSON: {key}"] = tidy_dataframe(df)
                except Exception:
                    pass

    if not candidates:
        raise ValueError("تعذر تحويل JSON إلى جدول قابل للتحليل.")

    return candidates, None


def read_xml_file(uploaded_file):
    uploaded_file.seek(0)
    df = pd.read_xml(uploaded_file)
    df = tidy_dataframe(df)
    return {"XML data": df}, None


def read_parquet_file(uploaded_file):
    uploaded_file.seek(0)
    df = pd.read_parquet(uploaded_file)
    df = tidy_dataframe(df)
    return {"Parquet data": df}, None


def read_html_file(uploaded_file):
    uploaded_file.seek(0)
    raw = uploaded_file.read()
    encoding = detect_encoding(raw)
    html = raw.decode(encoding, errors="replace")

    tables = pd.read_html(io.StringIO(html))
    candidates = {}

    for i, table in enumerate(tables, start=1):
        table = tidy_dataframe(table)
        table = try_promote_first_row_to_header(table)
        if not table.empty:
            candidates[f"HTML table {i}"] = table

    if not candidates:
        raise ValueError("لم يتم العثور على جداول HTML قابلة للتحليل.")

    return candidates, None


def read_docx_file(uploaded_file):
    from docx import Document

    uploaded_file.seek(0)
    doc = Document(uploaded_file)

    candidates = {}

    # الجداول أولًا
    for i, table in enumerate(doc.tables, start=1):
        rows = []
        for row in table.rows:
            rows.append([cell.text.strip() for cell in row.cells])

        if not rows:
            continue

        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]

        if len(rows) >= 2:
            header = make_unique_columns(rows[0])
            df = pd.DataFrame(rows[1:], columns=header)
        else:
            df = pd.DataFrame(rows)

        df = tidy_dataframe(df)
        if not df.empty:
            candidates[f"Word table {i}"] = df

    # النص الحر كمرشح إضافي
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    if paragraphs:
        text_df = pd.DataFrame({"text": paragraphs})
        candidates["Word text"] = text_df

    if not candidates:
        raise ValueError("ملف Word لا يحتوي على جداول أو نص قابل للاستخراج.")

    return candidates, None


def read_pdf_file(uploaded_file):
    import pdfplumber

    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()

    candidates = {}
    all_text = []
    table_counter = 0

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                all_text.append(f"[Page {page_no}]\n{text}")

            try:
                tables = page.extract_tables()
            except Exception:
                tables = []

            for table in tables:
                if not table or len(table) < 2:
                    continue

                clean_rows = []
                for row in table:
                    if row is None:
                        continue
                    clean_rows.append([
                        "" if cell is None else str(cell).strip()
                        for cell in row
                    ])

                if len(clean_rows) < 2:
                    continue

                width = max(len(r) for r in clean_rows)
                clean_rows = [r + [""] * (width - len(r)) for r in clean_rows]

                header = make_unique_columns(clean_rows[0])
                df = pd.DataFrame(clean_rows[1:], columns=header)
                df = tidy_dataframe(df)

                if not df.empty:
                    table_counter += 1
                    candidates[f"PDF table {table_counter} - page {page_no}"] = df

    if all_text:
        # نعرض النص كمرشح، لكن لا نفرض أنه بيانات جدولية.
        lines = []
        for chunk in all_text:
            for line in chunk.splitlines():
                line = line.strip()
                if line:
                    lines.append(line)
        if lines:
            candidates["PDF extracted text"] = pd.DataFrame({"text": lines})

    if not candidates:
        raise ValueError(
            "لم يتم استخراج نص أو جداول من PDF. "
            "قد يكون الملف ممسوحًا ضوئيًا (Scanned PDF) ويحتاج OCR."
        )

    return candidates, (
        "PDF: تم استخراج الجداول والنص المتاح. "
        "الملفات الممسوحة ضوئيًا بالكامل قد تحتاج OCR خارجيًا."
    )


def read_txt_file(uploaded_file):
    uploaded_file.seek(0)
    raw = uploaded_file.read()
    encoding = detect_encoding(raw)
    text = raw.decode(encoding, errors="replace")

    candidates = {}

    # محاولة اعتباره ملفًا جدوليًا
    delimiter = detect_delimiter(text[:5000], default=None)
    if delimiter:
        try:
            df = pd.read_csv(io.StringIO(text), sep=delimiter)
            df = tidy_dataframe(df)
            if df.shape[1] >= 2:
                candidates["TXT table"] = df
        except Exception:
            pass

    # النص الحر
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        candidates["TXT text"] = pd.DataFrame({"text": lines})

    if not candidates:
        raise ValueError("ملف TXT فارغ أو غير قابل للقراءة.")

    return candidates, f"Encoding: {encoding}"


def load_file(uploaded_file):
    extension = Path(uploaded_file.name).suffix.lower().lstrip(".")

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"نوع الملف غير مدعوم: .{extension}")

    if extension in {"xlsx", "xls", "xlsm", "ods"}:
        return read_excel_like(uploaded_file, extension), extension

    if extension in {"csv", "tsv"}:
        return read_csv_like(uploaded_file, extension), extension

    if extension == "json":
        return read_json_file(uploaded_file), extension

    if extension == "xml":
        return read_xml_file(uploaded_file), extension

    if extension == "parquet":
        return read_parquet_file(uploaded_file), extension

    if extension in {"html", "htm"}:
        return read_html_file(uploaded_file), extension

    if extension == "docx":
        return read_docx_file(uploaded_file), extension

    if extension == "pdf":
        return read_pdf_file(uploaded_file), extension

    if extension == "txt":
        return read_txt_file(uploaded_file), extension

    raise ValueError("نوع الملف غير مدعوم.")


# ============================================================
# اكتشاف بنية الاستبانة
# ============================================================
def detect_dataset_type(df: pd.DataFrame):
    """
    الأنواع:
    - respondent_level: كل صف مشارك، وكل عمود سؤال
    - frequency_distribution: صف لكل سؤال وأعمدة لفئات الإجابة
    - aggregated: متوسطات/نسب/انحرافات جاهزة
    - text: نص حر غير جدولي
    """
    if df.empty:
        return "unknown", 0.0, "البيانات فارغة"

    if df.shape[1] == 1:
        return "text", 0.95, "تم العثور على عمود نصي واحد."

    normalized_columns = [normalize_text(c) for c in df.columns]

    likert_count = sum(
        any(token in col for token in LIKERT_TOKENS)
        for col in normalized_columns
    )

    aggregate_count = sum(
        any(token in col for token in AGGREGATE_TOKENS)
        for col in normalized_columns
    )

    question_name_count = sum(
        any(token == col or token in col for token in QUESTION_TOKENS)
        for col in normalized_columns
    )

    converted = convert_numeric_candidates(df)
    numeric_cols = converted.select_dtypes(include=np.number).columns.tolist()

    if likert_count >= 2:
        return (
            "frequency_distribution",
            min(0.98, 0.75 + 0.05 * likert_count),
            "تم اكتشاف عدة أعمدة تحمل تسميات فئات Likert.",
        )

    if question_name_count >= 1 and aggregate_count >= 1:
        return (
            "aggregated",
            min(0.98, 0.75 + 0.05 * aggregate_count),
            "يوجد عمود للسؤال مع أعمدة متوسط/نسبة/تكرار أو مؤشرات مجمعة.",
        )

    if aggregate_count >= 2:
        return (
            "aggregated",
            min(0.95, 0.70 + 0.05 * aggregate_count),
            "تم اكتشاف عدة أعمدة لمؤشرات إحصائية مجمعة.",
        )

    candidate_questions = []
    for col in numeric_cols:
        if not looks_like_identifier(col, converted[col]):
            nunique = converted[col].nunique(dropna=True)
            if 2 <= nunique <= 15:
                candidate_questions.append(col)

    if len(candidate_questions) >= 2:
        return (
            "respondent_level",
            min(0.98, 0.75 + 0.03 * len(candidate_questions)),
            "تم اكتشاف عدة أعمدة رقمية قصيرة النطاق تبدو كإجابات أفراد.",
        )

    if len(numeric_cols) >= 2 and len(df) >= 5:
        return (
            "respondent_level",
            0.60,
            "البيانات تبدو جدوليّة وبها عدة أعمدة رقمية، لكن الثقة متوسطة.",
        )

    return "unknown", 0.40, "تعذر تحديد بنية الاستبانة تلقائيًا بثقة كافية."


def dataset_type_label(dataset_type: str) -> str:
    labels = {
        "respondent_level": "استجابات فردية Raw / Respondent-level",
        "frequency_distribution": "توزيع تكراري لفئات الإجابة",
        "aggregated": "نتائج مجمعة Aggregated",
        "text": "نص حر",
        "unknown": "غير محدد",
    }
    return labels.get(dataset_type, dataset_type)


def detect_question_columns(df: pd.DataFrame):
    converted = convert_numeric_candidates(df)
    numeric_columns = converted.select_dtypes(include=np.number).columns.tolist()

    candidates = []
    identifiers = []

    for col in numeric_columns:
        if looks_like_identifier(col, converted[col]):
            identifiers.append(col)
            continue

        values = converted[col].dropna()
        if values.empty:
            continue

        unique_count = values.nunique()
        min_val = values.min()
        max_val = values.max()

        # نطاق شائع لمقاييس Likert وغيرها
        likely_scale = (
            unique_count <= 15
            and min_val >= -1
            and max_val <= 10
        )

        # أو أن اسم العمود يبدو كسؤال
        likely_question_name = (
            is_question_column_name(col)
            or bool(re.match(r"^(q|س)\s*[\d_-]+", normalize_text(col)))
        )

        if likely_scale or likely_question_name:
            candidates.append(col)

    return converted, candidates, identifiers


def infer_scale(df: pd.DataFrame, columns):
    if not columns:
        return 1.0, 5.0, 0.0

    values = pd.concat([df[c] for c in columns], ignore_index=True).dropna()
    if values.empty:
        return 1.0, 5.0, 0.0

    actual_min = float(values.min())
    actual_max = float(values.max())

    common_scales = [
        (1.0, 5.0),
        (1.0, 7.0),
        (1.0, 10.0),
        (0.0, 4.0),
        (0.0, 5.0),
        (0.0, 10.0),
    ]

    for lo, hi in common_scales:
        if actual_min >= lo and actual_max <= hi:
            if np.isclose(actual_min, lo) or np.isclose(actual_max, hi):
                return lo, hi, 0.90

    return actual_min, actual_max, 0.60


# ============================================================
# التحليل الإحصائي
# ============================================================
def cronbach_alpha(df: pd.DataFrame) -> float:
    data = df.dropna(axis=0, how="any").astype(float)

    if data.shape[1] < 2:
        raise ValueError("يلزم اختيار سؤالين على الأقل.")
    if data.shape[0] < 2:
        raise ValueError("لا توجد صفوف مكتملة كافية لحساب الثبات.")

    item_variances = data.var(axis=0, ddof=1)
    total_scores = data.sum(axis=1)
    total_variance = total_scores.var(ddof=1)
    n_items = data.shape[1]

    if np.isclose(total_variance, 0):
        raise ValueError("تباين الدرجة الكلية يساوي صفرًا، لذلك لا يمكن حساب الثبات.")

    alpha = (n_items / (n_items - 1)) * (
        1 - item_variances.sum() / total_variance
    )
    return float(alpha)


def classify_alpha(alpha: float) -> str:
    if alpha >= 0.90:
        return "مرتفع جدًا"
    if alpha >= 0.80:
        return "جيد جدًا"
    if alpha >= 0.70:
        return "مقبول"
    if alpha >= 0.60:
        return "حدّي"
    return "ضعيف"


def build_descriptive(df: pd.DataFrame, columns):
    return pd.DataFrame({
        "السؤال": columns,
        "العدد": [df[c].count() for c in columns],
        "المتوسط": [df[c].mean() for c in columns],
        "الانحراف المعياري": [df[c].std(ddof=1) for c in columns],
        "الوسيط": [df[c].median() for c in columns],
        "أقل قيمة": [df[c].min() for c in columns],
        "أعلى قيمة": [df[c].max() for c in columns],
        "القيم المفقودة": [df[c].isna().sum() for c in columns],
    }).round(4)


def build_quality(df: pd.DataFrame, columns, suspicious_columns):
    rows = []
    for col in columns:
        rows.append({
            "العمود": col,
            "عدد القيم": int(df[col].notna().sum()),
            "القيم المفقودة": int(df[col].isna().sum()),
            "نسبة الفقد %": round(df[col].isna().mean() * 100, 2),
            "أقل قيمة": df[col].min(),
            "أعلى قيمة": df[col].max(),
            "عدد القيم الفريدة": int(df[col].nunique(dropna=True)),
            "يبدو كمعرّف": "نعم" if col in suspicious_columns else "لا",
        })
    return pd.DataFrame(rows)


def build_frequency(df: pd.DataFrame, columns):
    frames = []
    for col in columns:
        counts = (
            df[col]
            .value_counts(dropna=False)
            .sort_index()
            .rename_axis("القيمة")
            .reset_index(name="التكرار")
        )
        counts.insert(0, "السؤال", col)
        counts["النسبة %"] = (counts["التكرار"] / len(df) * 100).round(2)
        frames.append(counts)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def prepare_excel_report(
    summary_df,
    descriptive_df=None,
    quality_df=None,
    frequency_df=None,
    selected_df=None,
    source_df=None,
):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        if descriptive_df is not None and not descriptive_df.empty:
            descriptive_df.to_excel(writer, sheet_name="Descriptive", index=False)

        if quality_df is not None and not quality_df.empty:
            quality_df.to_excel(writer, sheet_name="Data Quality", index=False)

        if frequency_df is not None and not frequency_df.empty:
            frequency_df.to_excel(writer, sheet_name="Frequencies", index=False)

        if selected_df is not None and not selected_df.empty:
            selected_df.to_excel(writer, sheet_name="Selected Data", index=False)

        if source_df is not None and not source_df.empty:
            source_df.head(50000).to_excel(writer, sheet_name="Source Preview", index=False)

    output.seek(0)
    return output


def show_report_preview(sheets: dict, expanded: bool = True):
    """عرض أوراق التقرير داخل المنصة قبل تنزيل ملف Excel."""
    available = [
        (name, frame)
        for name, frame in sheets.items()
        if frame is not None and isinstance(frame, pd.DataFrame) and not frame.empty
    ]

    if not available:
        return

    with st.expander("معاينة التقرير قبل التنزيل", expanded=expanded):
        st.caption(
            "هذه المعاينة تمثل محتوى أوراق ملف Excel. "
            "قد يقتصر عرض البيانات الكبيرة على أول 100 سجل للحفاظ على سرعة المنصة."
        )
        tabs = st.tabs([name for name, _ in available])
        for tab, (_, frame) in zip(tabs, available):
            with tab:
                st.dataframe(frame.head(100), use_container_width=True)
                if len(frame) > 100:
                    st.info(f"تظهر أول 100 سجلات من أصل {len(frame):,} سجلًا.")


def donut_metric(label: str, value: float, color: str = "#136f63", note: str = ""):
    """بطاقة مؤشر دائري خفيفة لا تحتاج مكتبات رسوم إضافية."""
    safe_value = 0.0 if pd.isna(value) else float(np.clip(value, 0, 100))
    st.markdown(
        f"""
        <div style="background:#fff;border:1px solid #dce9e6;border-radius:18px;
                    padding:18px 12px;text-align:center;box-shadow:0 5px 18px rgba(22,48,45,.05)">
          <div style="width:132px;height:132px;margin:0 auto 12px;border-radius:50%;
                      background:conic-gradient({color} 0 {safe_value:.2f}%,#e8f0ee {safe_value:.2f}% 100%);
                      display:grid;place-items:center">
            <div style="width:94px;height:94px;border-radius:50%;background:white;
                        display:grid;place-items:center;color:#0b4f47;font-size:1.35rem;font-weight:800">
              {safe_value:.1f}%
            </div>
          </div>
          <div style="font-weight:800;color:#16302d">{label}</div>
          <div style="font-size:.78rem;color:#627773;margin-top:4px">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# واجهة رفع الملف
# ============================================================
st.markdown(
    """
    <div class="feature-grid">
      <div class="feature-card"><b>① اكتشاف تلقائي</b><span>تحديد بنية الاستبانة ونوع البيانات ودرجة الثقة.</span></div>
      <div class="feature-card"><b>② تحليل موثوق</b><span>وصف إحصائي، مؤشر رضا، جودة بيانات وثبات داخلي.</span></div>
      <div class="feature-card"><b>③ تقرير قابل للتنزيل</b><span>ملف Excel منظم يضم الملخص والنتائج التفصيلية.</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "ابدأ برفع ملف الاستبانة أو نتائجها",
    type=SUPPORTED_EXTENSIONS,
    help=(
        "مدعوم: Excel, CSV, TSV, ODS, PDF, Word DOCX, TXT, JSON, XML, "
        "Parquet, HTML."
    ),
)

if not uploaded_file:
    st.markdown(
        '<div class="privacy-note">🔒 تنبيه: تجنب رفع الأسماء والأرقام الجامعية وأي بيانات شخصية غير لازمة للتحليل.</div>',
        unsafe_allow_html=True,
    )
    st.info("بانتظار ملف البيانات للبدء في التحليل.", icon="📂")
    st.stop()


# ============================================================
# قراءة الملف
# ============================================================
try:
    (loaded_result, extension) = load_file(uploaded_file)
    candidates, reader_note = loaded_result
except Exception as exc:
    st.error(f"تعذر قراءة الملف: {exc}")
    st.stop()

if not candidates:
    st.error("لم يتم العثور على بيانات قابلة للتحليل داخل الملف.")
    st.stop()

st.success(f"تمت قراءة الملف بنجاح: {uploaded_file.name}", icon="✅")
st.progress(25, text="المرحلة 1 من 4 — تمت قراءة الملف واستخراج البيانات")

if reader_note:
    st.caption(reader_note)

candidate_names = list(candidates.keys())

if len(candidate_names) > 1:
    selected_candidate = st.selectbox(
        "تم العثور على أكثر من جدول/قسم. اختر البيانات المطلوب تحليلها",
        candidate_names,
    )
else:
    selected_candidate = candidate_names[0]

raw_df = tidy_dataframe(candidates[selected_candidate])

if raw_df.empty:
    st.error("الجزء المحدد لا يحتوي على بيانات.")
    st.stop()


# ============================================================
# Smart File Analyzer
# ============================================================
detected_type, detection_confidence, detection_reason = detect_dataset_type(raw_df)

st.subheader("المحلل الذكي للملف")

c1, c2, c3, c4 = st.columns(4)
c1.metric("نوع الملف", extension.upper())
c2.metric("الصفوف", f"{len(raw_df):,}")
c3.metric("الأعمدة", len(raw_df.columns))
c4.metric("ثقة الاكتشاف", f"{detection_confidence * 100:.0f}%")

st.info(
    f"**نوع البيانات المكتشف:** {dataset_type_label(detected_type)}  \n{detection_reason}",
    icon="🧠",
)

dataset_options = {
    "استجابات فردية Raw / Respondent-level": "respondent_level",
    "توزيع تكراري لفئات الإجابة": "frequency_distribution",
    "نتائج مجمعة Aggregated": "aggregated",
    "نص حر": "text",
    "غير محدد": "unknown",
}

default_label = next(
    (label for label, value in dataset_options.items() if value == detected_type),
    "غير محدد",
)

override_label = st.selectbox(
    "نوع البيانات",
    list(dataset_options.keys()),
    index=list(dataset_options.keys()).index(default_label),
    help="يمكنك تصحيح اكتشاف المنصة إذا كان غير صحيح.",
)

dataset_type = dataset_options[override_label]

with st.expander("معاينة البيانات الأولية", expanded=True):
    st.dataframe(raw_df.head(30), use_container_width=True)

st.progress(50, text="المرحلة 2 من 4 — تم اكتشاف بنية البيانات")


# ============================================================
# التعامل مع النص الحر
# ============================================================
if dataset_type == "text":
    st.warning(
        "تم استخراج النص، لكن لا توجد بنية جدولية مؤكدة تسمح بإجراء التحليل الإحصائي مباشرة."
    )

    text_col = raw_df.columns[0]
    extracted_text = "\n".join(raw_df[text_col].astype(str).tolist())

    st.text_area(
        "النص المستخرج",
        value=extracted_text[:30000],
        height=350,
    )

    summary_df = pd.DataFrame([{
        "اسم الملف": uploaded_file.name,
        "نوع الملف": extension,
        "نوع البيانات": dataset_type_label(dataset_type),
        "عدد الأسطر/السجلات": len(raw_df),
        "ملاحظة": "النص يحتاج تحويلًا إلى جدول أو استخراجًا أكثر تخصصًا قبل التحليل الإحصائي.",
    }])

    output = prepare_excel_report(summary_df, source_df=raw_df)

    show_report_preview({
        "الملخص": summary_df,
        "المحتوى المستخرج": raw_df,
    })

    st.download_button(
        "تنزيل النص/البيانات المستخرجة كـ Excel",
        data=output,
        file_name="extracted_content.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.stop()


# ============================================================
# النتائج المجمعة أو التوزيعات الجاهزة
# ============================================================
if dataset_type in {"aggregated", "frequency_distribution"}:
    st.subheader("البيانات المستخرجة")

    converted_df = convert_numeric_candidates(raw_df)
    st.dataframe(converted_df, use_container_width=True)

    numeric_columns = converted_df.select_dtypes(include=np.number).columns.tolist()

    if dataset_type == "frequency_distribution":
        likert_columns = [c for c in converted_df.columns if is_likert_column_name(c)]
        if likert_columns:
            st.info(
                "اكتشفت المنصة أعمدة فئات استجابة Likert: "
                + "، ".join(likert_columns)
            )

    st.info(
        "لن يتم حساب Cronbach's Alpha لهذه البيانات تلقائيًا، "
        "لأن الثبات الداخلي يتطلب عادةً استجابات الأفراد لكل بند وليس المتوسطات أو التكرارات المجمعة."
    )

    # عرض ملخص رقمي للحقول الرقمية الموجودة دون الادعاء أنها أسئلة فردية
    aggregate_summary = pd.DataFrame()
    if numeric_columns:
        aggregate_summary = converted_df[numeric_columns].describe().T.reset_index()
        aggregate_summary = aggregate_summary.rename(columns={"index": "المتغير"})
        st.subheader("ملخص الحقول الرقمية")
        st.dataframe(aggregate_summary, use_container_width=True)

    summary_df = pd.DataFrame([{
        "اسم الملف": uploaded_file.name,
        "نوع الملف": extension,
        "نوع البيانات": dataset_type_label(dataset_type),
        "عدد السجلات": len(converted_df),
        "عدد الأعمدة": len(converted_df.columns),
        "Cronbach Alpha": "غير محسوب - البيانات مجمعة",
    }])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        converted_df.to_excel(writer, sheet_name="Extracted Data", index=False)
        if not aggregate_summary.empty:
            aggregate_summary.to_excel(writer, sheet_name="Numeric Summary", index=False)

    output.seek(0)

    show_report_preview({
        "الملخص": summary_df,
        "البيانات المستخرجة": converted_df,
        "الملخص الرقمي": aggregate_summary,
    })

    st.download_button(
        "تنزيل النتائج المستخرجة",
        data=output,
        file_name="educational_quality_aggregated_analysis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.success("اكتملت معالجة البيانات المجمعة.")
    st.stop()


# ============================================================
# الاستجابات الفردية
# ============================================================
converted_df, auto_question_columns, auto_identifier_columns = detect_question_columns(raw_df)

numeric_columns = converted_df.select_dtypes(include=np.number).columns.tolist()

if not numeric_columns:
    st.error(
        "لم يتم العثور على أعمدة رقمية مناسبة. "
        "تأكد من أن استجابات المشاركين موجودة كقيم رقمية."
    )
    st.stop()

st.subheader("تحديد أسئلة الاستبانة")

if auto_question_columns:
    st.caption(
        f"اكتشفت المنصة مبدئيًا {len(auto_question_columns)} عمودًا يبدو كأسئلة استبانة."
    )
else:
    st.warning(
        "لم تتمكن المنصة من تحديد الأسئلة بثقة. "
        "اختر الأعمدة يدويًا من القائمة."
    )

selected_columns = st.multiselect(
    "اختر أعمدة أسئلة الاستبانة",
    options=numeric_columns,
    default=auto_question_columns if auto_question_columns else numeric_columns,
    help="لا تُدخل المعرّفات مثل رقم الطالب أو رقم المشارك ضمن الأسئلة.",
)

if not selected_columns:
    st.warning("اختر عمودًا واحدًا على الأقل.")
    st.stop()

suspicious_columns = [
    col for col in selected_columns
    if looks_like_identifier(col, converted_df[col])
]

if suspicious_columns:
    st.warning(
        "الأعمدة التالية تبدو كمعرّفات أو أرقام تسلسلية: "
        + "، ".join(suspicious_columns)
        + ". يفضّل إزالتها من اختيار الأسئلة."
    )

analysis_df = converted_df[selected_columns].copy()
st.progress(75, text="المرحلة 3 من 4 — تم اعتماد الأعمدة الجاهزة للتحليل")

# ============================================================
# فحص الجودة
# ============================================================
st.subheader("فحص جودة البيانات")

quality_df = build_quality(
    analysis_df,
    selected_columns,
    suspicious_columns,
)
st.dataframe(quality_df, use_container_width=True)

auto_min, auto_max, scale_confidence = infer_scale(analysis_df, selected_columns)

with st.expander("خيارات مقياس الاستجابة", expanded=True):
    sc1, sc2, sc3 = st.columns(3)

    expected_min = sc1.number_input(
        "أقل قيمة متوقعة",
        value=float(auto_min),
    )

    expected_max = sc2.number_input(
        "أعلى قيمة متوقعة",
        value=float(auto_max),
    )

    sc3.metric("ثقة اكتشاف المقياس", f"{scale_confidence * 100:.0f}%")

if expected_min >= expected_max:
    st.error("يجب أن تكون أعلى قيمة أكبر من أقل قيمة.")
    st.stop()

out_of_range = {}

for col in selected_columns:
    invalid_count = int(
        (
            (analysis_df[col] < expected_min)
            | (analysis_df[col] > expected_max)
        )
        .fillna(False)
        .sum()
    )

    if invalid_count:
        out_of_range[col] = invalid_count

if out_of_range:
    st.warning(
        "توجد قيم خارج النطاق المتوقع: "
        + "، ".join([f"{col}: {count}" for col, count in out_of_range.items()])
    )


# ============================================================
# التحليل الوصفي
# ============================================================
st.subheader("التحليل الوصفي")

descriptive_df = build_descriptive(analysis_df, selected_columns)
st.dataframe(descriptive_df, use_container_width=True)


# ============================================================
# مؤشر الرضا
# ============================================================
st.subheader("مؤشر الرضا")

scale_span = expected_max - expected_min

if scale_span > 0:
    satisfaction_df = descriptive_df[["السؤال", "المتوسط"]].copy()
    satisfaction_df["مؤشر الرضا %"] = (
        (satisfaction_df["المتوسط"] - expected_min)
        / scale_span
        * 100
    ).clip(0, 100).round(2)

    st.dataframe(satisfaction_df, use_container_width=True)

    chart_df = (
        satisfaction_df
        .set_index("السؤال")[["مؤشر الرضا %"]]
        .sort_values("مؤشر الرضا %", ascending=False)
        .head(20)
    )
    st.caption("مقارنة مؤشر الرضا بين البنود — أعلى 20 بندًا")
    st.bar_chart(chart_df, color="#136f63", horizontal=False)
else:
    satisfaction_df = pd.DataFrame()


# ============================================================
# الثبات الداخلي
# ============================================================
st.subheader("الثبات الداخلي")

alpha_value = None
alpha_status = None

if len(selected_columns) < 2:
    st.info("اختر سؤالين على الأقل لحساب Cronbach's Alpha.")
else:
    try:
        alpha_value = cronbach_alpha(analysis_df)
        alpha_status = classify_alpha(alpha_value)

        a1, a2, a3 = st.columns(3)
        a1.metric("Cronbach's Alpha", f"{alpha_value:.4f}")
        a2.metric("التصنيف", alpha_status)
        a3.metric(
            "عدد الصفوف المكتملة",
            int(analysis_df.dropna(axis=0, how="any").shape[0]),
        )

        if suspicious_columns:
            st.info(
                "قيمة Alpha الحالية تشمل الأعمدة المختارة. "
                "إذا كان بينها معرف، أزله من اختيار الأسئلة."
            )

        if alpha_value < 0 or alpha_value > 1:
            st.warning(
                "قيمة Alpha خارج النطاق المعتاد 0–1. "
                "قد يكون السبب بنودًا معكوسة غير مصححة أو مشكلة في بنية البيانات."
            )

    except Exception as exc:
        st.error(f"تعذر حساب Cronbach's Alpha: {exc}")


# ============================================================
# توزيع الإجابات
# ============================================================
st.subheader("توزيع الإجابات")

frequency_df = build_frequency(analysis_df, selected_columns)
st.dataframe(frequency_df, use_container_width=True)


# ============================================================
# ملخص عام
# ============================================================
st.subheader("ملخص التحليل")

overall_mean = float(
    pd.concat(
        [analysis_df[c] for c in selected_columns],
        ignore_index=True,
    ).mean()
)

overall_satisfaction = (
    ((overall_mean - expected_min) / (expected_max - expected_min) * 100)
    if expected_max > expected_min
    else np.nan
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("عدد السجلات", f"{len(analysis_df):,}")
m2.metric("عدد الأسئلة", len(selected_columns))
m3.metric("المتوسط العام", f"{overall_mean:.3f}")
m4.metric("الرضا العام", f"{overall_satisfaction:.1f}%")

# ============================================================
# لوحة الإحصاءات المرئية
# ============================================================
st.subheader("لوحة الإحصاءات المرئية")

total_cells = analysis_df.shape[0] * analysis_df.shape[1]
available_cells = int(analysis_df.notna().sum().sum())
completeness_pct = (available_cells / total_cells * 100) if total_cells else 0
alpha_pct = float(np.clip(alpha_value * 100, 0, 100)) if alpha_value is not None else 0

circle1, circle2, circle3 = st.columns(3)
with circle1:
    donut_metric("الرضا العام", overall_satisfaction, "#136f63", "محسوب وفق نطاق المقياس")
with circle2:
    donut_metric("اكتمال البيانات", completeness_pct, "#d9a441", "نسبة القيم غير المفقودة")
with circle3:
    donut_metric(
        "الثبات الداخلي",
        alpha_pct,
        "#2878a5",
        alpha_status if alpha_status else "غير متاح",
    )

visual_tab1, visual_tab2 = st.tabs(["أعمدة مؤشرات البنود", "أعمدة توزيع الإجابات"])

with visual_tab1:
    if not satisfaction_df.empty:
        visual_satisfaction = (
            satisfaction_df
            .sort_values("مؤشر الرضا %", ascending=False)
            .head(20)
            .set_index("السؤال")[["مؤشر الرضا %"]]
        )
        st.bar_chart(visual_satisfaction, color="#136f63")
    else:
        st.info("لا تتوفر بيانات كافية لرسم مؤشرات البنود.")

with visual_tab2:
    combined_answers = (
        pd.concat([analysis_df[c] for c in selected_columns], ignore_index=True)
        .dropna()
        .value_counts()
        .sort_index()
        .rename_axis("قيمة الإجابة")
        .to_frame("التكرار")
    )
    if not combined_answers.empty:
        st.bar_chart(combined_answers, color="#d9a441")
        st.caption("يجمع الرسم جميع إجابات البنود المختارة لإظهار شكل التوزيع العام.")
    else:
        st.info("لا تتوفر إجابات كافية لرسم التوزيع.")

if not satisfaction_df.empty:
    best_item = satisfaction_df.loc[satisfaction_df["مؤشر الرضا %"].idxmax()]
    weakest_item = satisfaction_df.loc[satisfaction_df["مؤشر الرضا %"].idxmin()]
    insight_left, insight_right = st.columns(2)
    insight_left.success(
        f"أعلى بند رضا: **{best_item['السؤال']}** — {best_item['مؤشر الرضا %']:.1f}%",
        icon="↗️",
    )
    insight_right.warning(
        f"البند الأكثر حاجة للتحسين: **{weakest_item['السؤال']}** — {weakest_item['مؤشر الرضا %']:.1f}%",
        icon="🎯",
    )


# ============================================================
# تنزيل النتائج
# ============================================================
st.subheader("تنزيل النتائج")

summary_df = pd.DataFrame([{
    "اسم الملف": uploaded_file.name,
    "نوع الملف": extension,
    "القسم/الجدول المختار": selected_candidate,
    "نوع البيانات": dataset_type_label(dataset_type),
    "ثقة اكتشاف النوع": detection_confidence,
    "عدد السجلات": len(raw_df),
    "عدد الأسئلة المختارة": len(selected_columns),
    "الأعمدة المشبوهة": ", ".join(suspicious_columns),
    "Cronbach Alpha": alpha_value,
    "تصنيف Alpha": alpha_status,
    "النطاق المتوقع": f"{expected_min} - {expected_max}",
    "المتوسط العام": overall_mean,
    "مؤشر الرضا العام %": overall_satisfaction,
}])

output = io.BytesIO()

with pd.ExcelWriter(output, engine="openpyxl") as writer:
    summary_df.to_excel(writer, sheet_name="Summary", index=False)
    descriptive_df.to_excel(writer, sheet_name="Descriptive", index=False)
    quality_df.to_excel(writer, sheet_name="Data Quality", index=False)
    frequency_df.to_excel(writer, sheet_name="Frequencies", index=False)
    analysis_df.to_excel(writer, sheet_name="Selected Data", index=False)

    if not satisfaction_df.empty:
        satisfaction_df.to_excel(writer, sheet_name="Satisfaction", index=False)

output.seek(0)

st.progress(100, text="المرحلة 4 من 4 — اكتمل التحليل وأصبح التقرير جاهزًا")

show_report_preview({
    "الملخص": summary_df,
    "التحليل الوصفي": descriptive_df,
    "جودة البيانات": quality_df,
    "مؤشر الرضا": satisfaction_df,
    "التكرارات": frequency_df,
    "البيانات المختارة": analysis_df,
})

st.download_button(
    "تنزيل تقرير Excel الكامل",
    data=output,
    file_name="educational_quality_analysis.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.success("اكتمل التحليل وأصبح التقرير جاهزًا للتنزيل.", icon="✅")
st.markdown(
    '<div class="footer">منصة تحليلات الجودة التعليمية · تحليل البيانات لاتخاذ قرارات قابلة للقياس</div>',
    unsafe_allow_html=True,
)
