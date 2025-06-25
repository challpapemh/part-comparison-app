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
                'Part Description_Stock': stock_row['Part Description'],
                'Part Number_Stock': stock_row['Part Number'],
                'Part Description_Comparison': best_match['Part Description'],
                'Part Number_Comparison': best_match['Part Number']
            })
    return pd.DataFrame(matches).drop_duplicates()

st.title("Part Number Comparison Tool")

stock_file = st.file_uploader("Upload Stock File (Excel or CSV)", type=['csv', 'xls', 'xlsx'])
comparison_file = st.file_uploader("Upload Comparison File (Excel or CSV)", type=['csv', 'xls', 'xlsx'])

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

        result_df = compare_part_lists_by_description(stock_df, comparison_df)

        st.subheader("Differences in Part Numbers (Based on Descriptions)")
        st.dataframe(result_df)

        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Comparison Results as CSV",
            data=csv,
            file_name='part_number_differences.csv',
            mime='text/csv'
        )

    except Exception as e:
        st.error(f"Error processing files: {e}")
