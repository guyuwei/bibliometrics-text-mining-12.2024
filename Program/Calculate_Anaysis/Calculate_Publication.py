import streamlit as st


# 计算每年文章
def calculate_publications_per_year(df):
    if '出版年' in df.columns:
        df = df.copy()  # 创建副本避免SettingWithCopyWarning
        df['出版年'] = df['出版年'].astype(int)
        years = sorted(df['出版年'].unique())
        publications_per_year = df['出版年'].value_counts().sort_index().tolist()  # 排序后的逐年发表量
        data_to_sort = list(zip(years, publications_per_year))
        sorted_data = sorted(data_to_sort, key=lambda x: x[0])
        years, publications_per_year = zip(*sorted_data)
    else:
        years = []
        publications_per_year = []
        sorted_data = []
        st.warning("数据中缺少'出版年'列，无法绘制年度发文量相关图表:在EXCEL中检查该csv的列名与字段是否完全一致")
    return sorted_data, years, publications_per_year

import pandas as pd

def calculate_publication_by_type(df: pd.DataFrame):
    if '文献类型' in df.columns:
        return df['文献类型'].value_counts()
    else:
        return pd.Series()