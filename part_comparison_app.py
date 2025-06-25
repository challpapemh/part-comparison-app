import streamlit as st
import pandas as pd
from difflib import SequenceMatcher

def compare_part_lists_by_description(stock_df, comparison_df, threshold=0.6):
    stock_descs = stock_df[['Part Number', 'Part Description']].dropna().drop_duplicates()
    comparison_descs = comparison_df[['Part Number', 'Part Description']].dropna().drop_duplicates()

    matches = []
    for _, stock_row in stock_descs.iterrows():
        best_match = None
        highest_ratio = 0
        for _, comp_row in comparison_descs.iterrows():
            ratio = SequenceMatcher(None, stock_row['Part Description'].lower(), comp_row['Part Description'].lower()).ratio()
            if ratio > highest_ratio and ratio >= threshold:
                best_match = comp_row
                highest_ratio = ratio
        if best_match is not None and stock_row['Part Number'] != best_match['Part Number']:
            matches.append({
                'Original_Remove': stock_row['Part Description'],
                'Part Number_Remove': stock_row['Part Number'],
                'New Parts_Add': best_match['Part Description'],
                'Part Number_Add': best_match['Part Number']
            })
    return pd.DataFrame(matches).drop_duplicates()

st.set_page_config(page_title="Part Number Comparison", layout="centered")
st.title("🔍 Part Number Comparison Tool")

st.markdown("""
This app compares two part lists based on description similarity.
- Upload the **original part list** and the **new part list** (CSV or Excel).
- Files must contain **Part Number** and **Part Description** columns.
- Adjust the similarity sensitivity using the slider below.
- The app will highlight parts that appear different but are similarly described.
""")

similarity_threshold = st.slider("Match Sensitivity (Higher = Stricter)", min_value=0.0, max_value=1.0, value=0.6, step=0.05)

stock_file = st.file_uploader("📂 Upload Original Parts List", type=['csv', 'xls', 'xlsx'])
comparison_file = st.file_uploader("📂 Upload New Parts List", type=['csv', 'xls', 'xlsx'])

if stock_file and comparison_file:
    try:
        if stock_file.name.endswith(('.xls', '.xlsx')):
            stock_df = pd.read_excel(stock_file)
        else:
            stock_df = pd.read_csv(stock_file, encoding='latin1')

        if comparison_file.name.endswith(('.xls', '.xlsx')):
            comparison_df = pd.read_excel(comparison_file)
        else:
            comparison_df = pd.read_csv(comparison_file, encoding='latin1')

        result_df = compare_part_lists_by_description(stock_df, comparison_df, threshold=similarity_threshold)

        st.subheader("🧾 Differences in Part Numbers (Based on Descriptions)")
        st.write(f"🔎 **{len(result_df)} differences found** with similarity threshold of `{similarity_threshold}`.")
        st.dataframe(result_df, use_container_width=True)

        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Download Results as CSV",
            data=csv,
            file_name='part_number_differences.csv',
            mime='text/csv'
        )

    except Exception as e:
        st.error(f"❌ Error processing files: {e}")
