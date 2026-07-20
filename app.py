
import io
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Educational Quality Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("Educational Quality Analytics")
st.caption("نسخة أولية لتحليل ملفات الاستبانات التعليمية")

def clean_numeric_series(series: pd.Series) -> pd.Series:
    """تحويل القيم الرقمية النصية إلى أرقام مع الإبقاء على القيم غير الصالحة كـ NaN."""
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace("،", ".", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(cleaned, errors="coerce")

def cronbach_alpha(df: pd.DataFrame) -> float:
    """
    حساب Cronbach's Alpha.
    يجب أن يحتوي df على عمودين رقميين على الأقل وصفين مكتملين على الأقل.
    """
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

uploaded_file = st.file_uploader(
    "ارفع ملف Excel",
    type=["xlsx", "xls"],
    help="يفضل أن يكون الصف الأول أسماء الأعمدة، وكل صف لاحق يمثل مشاركًا واحدًا."
)

if not uploaded_file:
    st.info("ارفع ملف Excel للبدء.")
    st.stop()

try:
    excel_file = pd.ExcelFile(uploaded_file)
except Exception as exc:
    st.error(f"تعذر فتح ملف Excel: {exc}")
    st.stop()

sheet_name = st.selectbox("اختر ورقة العمل", excel_file.sheet_names)

try:
    raw_df = pd.read_excel(excel_file, sheet_name=sheet_name)
except Exception as exc:
    st.error(f"تعذر قراءة ورقة العمل: {exc}")
    st.stop()

if raw_df.empty:
    st.error("ورقة العمل فارغة.")
    st.stop()

raw_df.columns = [str(col).strip() for col in raw_df.columns]

st.subheader("معاينة البيانات")
st.dataframe(raw_df.head(20), use_container_width=True)

duplicate_columns = raw_df.columns[raw_df.columns.duplicated()].tolist()
if duplicate_columns:
    st.error(f"توجد أسماء أعمدة مكررة: {duplicate_columns}")
    st.stop()

all_missing_columns = raw_df.columns[raw_df.isna().all()].tolist()
if all_missing_columns:
    st.warning(
        "تم العثور على أعمدة فارغة بالكامل وسيتم تجاهلها: "
        + ", ".join(all_missing_columns)
    )
    raw_df = raw_df.drop(columns=all_missing_columns)

converted_df = raw_df.copy()
conversion_report = []

for column in converted_df.columns:
    original_non_missing = converted_df[column].notna().sum()
    numeric_series = clean_numeric_series(converted_df[column])
    numeric_non_missing = numeric_series.notna().sum()

    ratio = numeric_non_missing / original_non_missing if original_non_missing else 0

    if ratio >= 0.70:
        converted_df[column] = numeric_series
        conversion_report.append((column, ratio))

numeric_columns = converted_df.select_dtypes(include=np.number).columns.tolist()

if not numeric_columns:
    st.error(
        "لم يتم العثور على أعمدة رقمية مناسبة. "
        "تأكد من أن إجابات الاستبانة مكتوبة كأرقام مثل 1 إلى 5."
    )
    st.stop()

default_columns = numeric_columns[: min(10, len(numeric_columns))]

selected_columns = st.multiselect(
    "اختر أعمدة أسئلة الاستبانة",
    options=numeric_columns,
    default=default_columns
)

if not selected_columns:
    st.warning("اختر عمودًا واحدًا على الأقل.")
    st.stop()

analysis_df = converted_df[selected_columns].copy()

st.subheader("فحص جودة البيانات")

quality_rows = []
for col in selected_columns:
    quality_rows.append({
        "العمود": col,
        "عدد القيم": int(analysis_df[col].notna().sum()),
        "القيم المفقودة": int(analysis_df[col].isna().sum()),
        "نسبة الفقد %": round(analysis_df[col].isna().mean() * 100, 2),
        "أقل قيمة": analysis_df[col].min(),
        "أعلى قيمة": analysis_df[col].max(),
        "عدد القيم الفريدة": int(analysis_df[col].nunique(dropna=True)),
    })

quality_df = pd.DataFrame(quality_rows)
st.dataframe(quality_df, use_container_width=True)

with st.expander("خيارات مقياس الاستجابة"):
    expected_min = st.number_input("أقل قيمة متوقعة", value=1.0)
    expected_max = st.number_input("أعلى قيمة متوقعة", value=5.0)

if expected_min >= expected_max:
    st.error("يجب أن تكون أعلى قيمة أكبر من أقل قيمة.")
    st.stop()

out_of_range = {}
for col in selected_columns:
    invalid_count = int(
        ((analysis_df[col] < expected_min) | (analysis_df[col] > expected_max))
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

st.subheader("التحليل الوصفي")

descriptive_df = pd.DataFrame({
    "السؤال": selected_columns,
    "العدد": [analysis_df[c].count() for c in selected_columns],
    "المتوسط": [analysis_df[c].mean() for c in selected_columns],
    "الانحراف المعياري": [analysis_df[c].std(ddof=1) for c in selected_columns],
    "الوسيط": [analysis_df[c].median() for c in selected_columns],
    "أقل قيمة": [analysis_df[c].min() for c in selected_columns],
    "أعلى قيمة": [analysis_df[c].max() for c in selected_columns],
    "القيم المفقودة": [analysis_df[c].isna().sum() for c in selected_columns],
}).round(4)

st.dataframe(descriptive_df, use_container_width=True)

st.subheader("الثبات الداخلي")

alpha_value = None
alpha_status = None

if len(selected_columns) < 2:
    st.info("اختر سؤالين على الأقل لحساب Cronbach's Alpha.")
else:
    try:
        alpha_value = cronbach_alpha(analysis_df)
        alpha_status = classify_alpha(alpha_value)

        col1, col2, col3 = st.columns(3)
        col1.metric("Cronbach's Alpha", f"{alpha_value:.4f}")
        col2.metric("التصنيف", alpha_status)
        col3.metric(
            "عدد الصفوف المكتملة",
            int(analysis_df.dropna(axis=0, how="any").shape[0])
        )

        if alpha_value < 0 or alpha_value > 1:
            st.warning(
                "قيمة Alpha خارج النطاق المعتاد من 0 إلى 1. "
                "قد يدل ذلك على ترميز عكسي غير مصحح أو مشكلات في البيانات."
            )
    except Exception as exc:
        st.error(f"تعذر حساب Cronbach's Alpha: {exc}")

st.subheader("توزيع الإجابات")

frequency_frames = []
for col in selected_columns:
    counts = (
        analysis_df[col]
        .value_counts(dropna=False)
        .sort_index()
        .rename_axis("القيمة")
        .reset_index(name="التكرار")
    )
    counts.insert(0, "السؤال", col)
    counts["النسبة %"] = (counts["التكرار"] / len(analysis_df) * 100).round(2)
    frequency_frames.append(counts)

frequency_df = pd.concat(frequency_frames, ignore_index=True)
st.dataframe(frequency_df, use_container_width=True)

st.subheader("تنزيل النتائج")

summary_df = pd.DataFrame([{
    "عدد السجلات": len(raw_df),
    "عدد الأسئلة المختارة": len(selected_columns),
    "Cronbach Alpha": alpha_value,
    "تصنيف Alpha": alpha_status,
    "النطاق المتوقع": f"{expected_min} - {expected_max}",
}])

output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    summary_df.to_excel(writer, sheet_name="Summary", index=False)
    descriptive_df.to_excel(writer, sheet_name="Descriptive", index=False)
    quality_df.to_excel(writer, sheet_name="Data Quality", index=False)
    frequency_df.to_excel(writer, sheet_name="Frequencies", index=False)
    analysis_df.to_excel(writer, sheet_name="Selected Data", index=False)

output.seek(0)

st.download_button(
    "تنزيل تقرير Excel",
    data=output,
    file_name="educational_quality_analysis.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.success("اكتمل التحليل الأولي.")
