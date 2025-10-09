import streamlit as st
import pandas as pd

# 计算平均每篇文献的被引用次数
def calculate_number_of_total_Timescitedcount(df):
    number_of_total_articles = df.shape[0]
    number_of_total_Timescitedcount = 0
    average_citations_per_doc = 0
    
    if '核心合集的被引频次计数' in df.columns:
        # 安全地处理引用次数数据
        for index, citations in df['核心合集的被引频次计数'].items():
            try:
                if pd.notna(citations):
                    # 尝试转换为数值
                    citation_value = float(citations) if str(citations).replace('.', '').replace('-', '').isdigit() else 0
                    number_of_total_Timescitedcount += max(0, citation_value)  # 确保不为负数
            except (ValueError, TypeError):
                continue  # 跳过无法转换的值
        
        if number_of_total_articles > 0:
            average_citations_per_doc = number_of_total_Timescitedcount / number_of_total_articles
    else:
        st.warning(
            "数据中缺少'核心合集的被引频次计数'列，无法计算平均每篇文献的引用次数:在EXCEL中检查该csv的列名与字段是否完全一致")
    
    return int(number_of_total_Timescitedcount), round(average_citations_per_doc, 2)

#
