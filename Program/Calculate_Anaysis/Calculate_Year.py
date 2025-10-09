import streamlit as st
import pandas as pd
# 根据筛选出指定年份区间内的文章
def exact_targetarticles_within_yearspan(df, start, stop):
    start,stop=int(start),int(stop)
    if '出版年' in df.columns:
        df['出版年'] = df['出版年'].astype(int)
        filtered_df = df[(df['出版年'] >= start) & (df['出版年'] <= stop)]
    else:
        st.warning("数据中缺少'出版年'列，无法根据年份筛选文章:在EXCEL中检查该csv的列名与字段是否完全一致")
    return filtered_df
#计算文章年龄
def calculate_age(df):
    total_ages= []
    sum_ages=0
    if '出版年' in df.columns:
        df['出版年']=df['出版年'].astype(int)
        years = sorted(df['出版年'].unique())
        ddl_cal=max(years)
        for each_year in df['出版年']:
                total_ages.append( ddl_cal - each_year)
                sum_ages = sum_ages + ( ddl_cal- each_year)
        average_age_per_doc=sum_ages/len(total_ages)
    else:
        average_age_per_doc=0
        st.warning("数据中缺少'出版年'列，无法计算文章年龄:在EXCEL中检查该csv的列名与字段是否完全一致")
    return total_ages,average_age_per_doc


def calculate_publications_per_year(df: pd.DataFrame):
    if '出版年' in df.columns:
        df = df.copy()  # 创建副本避免SettingWithCopyWarning
        years = df['出版年'].dropna().astype(int)
        return years.value_counts().sort_index()
    else:
        return pd.Series(dtype='int64')

