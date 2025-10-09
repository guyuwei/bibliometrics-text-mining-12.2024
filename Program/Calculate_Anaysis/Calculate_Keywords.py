import streamlit as st
import pandas as pd

def calculate_number_of_keywords(df):
    """计算关键词统计信息"""
    if '作者关键词' in df.columns:
        total_keywords = []
        for keywords in df['作者关键词'].dropna():
            keyword_list = keywords.split(';')
            for keyword in keyword_list:
                total_keywords.append(keyword.strip().lower())
        total_unique_keywords = set(total_keywords)
        number_of_total_keywords = len(total_keywords)
        number_of_unique_keywords = len(total_unique_keywords)
        return total_keywords, total_unique_keywords, number_of_total_keywords, number_of_unique_keywords
    else:
        st.warning("数据中缺少'关键词'列，无法计算关键词总数:在EXCEL中检查该csv的列名与字段是否完全一致")
        return [], set(), 0, 0

def calculate_keywords_frequency(df):
    """计算关键词频率"""
    if '作者关键词' in df.columns:
        total_keywords = []
        for keywords in df['作者关键词'].dropna():
            keyword_list = keywords.split(';')
            for keyword in keyword_list:
                total_keywords.append(keyword.strip().lower())
        return pd.Series(total_keywords).value_counts()
    else:
        return pd.Series()