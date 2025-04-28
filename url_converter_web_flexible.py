import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from io import BytesIO

st.set_page_config(page_title="🌐 URL Converter Web", layout="centered")

# Language-to-path mapping
LANG_MAP = {
    "ja-JP": "/content/lifetech/japan/en-jp",
    "zh-CN": "/content/lifetech/greater-china/en-cn",
    "zh-TW": "/content/lifetech/greater-china/en-hk",
    "es-LATAM": "/content/lifetech/latin-america/en-mx",
    "es-ES": "/content/lifetech/europe/en-es",
    "fr-FR": "/content/lifetech/europe/en-fr",
    "de-DE": "/content/lifetech/europe/en-de",
    "pt-BR": "/content/lifetech/latin-america/en-br",
    "ko-KR": "/content/lifetech/ipac/en-kr"
}

def clean_url(url):
    if not isinstance(url, str):
        return None
    parsed = urlparse(url)
    path = parsed.path
    if "/home/" not in path:
        return None
    cleaned = path.split("/home/", 1)[1].removesuffix(".html")
    return "/home/" + cleaned

def detect_first_url(row):
    for cell in row:
        if isinstance(cell, str) and cell.startswith("http") and "/home/" in cell:
            return cell
    return None

def process_file(file):
    df = pd.read_excel(file, sheet_name=0, header=3)
    results = []
    language_columns = [col for col in df.columns if any(code in str(col) for code in LANG_MAP.keys())]

    for _, row in df.iterrows():
        original_url = detect_first_url(row)
        cleaned_path = clean_url(original_url)
        if not cleaned_path:
            continue
        for col in language_columns:
            for code in LANG_MAP:
                if code in str(col) and str(row[col]).strip().upper() == "X":
                    results.append({
                        "Original URL": original_url,
                        "Language": code,
                        "Localized Path": LANG_MAP[code] + cleaned_path
                    })

    result_df = pd.DataFrame(results)
    return result_df.sort_values(by=["Language"]) if not result_df.empty else pd.DataFrame()

st.title("🌍 URL Converter (Streamlit Web - Flexible Mode)")

uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df_result = process_file(uploaded_file)
        if df_result.empty:
            st.warning("No valid data found in the file.")
        else:
            st.success("✅ Conversion completed!")
            st.dataframe(df_result)

            # Generate downloadable Excel
            output = BytesIO()
            df_result.to_excel(output, index=False)
            output.seek(0)

            st.download_button(
                label="📥 Download Converted Excel",
                data=output,
                file_name="converted_urls.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"❌ Error: {e}")