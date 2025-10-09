import streamlit as st
import pandas as pd
from itertools import combinations


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
        years = df['出版年'].dropna().astype(int)
        return years.value_counts().sort_index()
    else:
        return pd.Series()


import pandas as pd
import re
from collections import defaultdict
import networkx as nx

def generate_cooccurrence_network(df: pd.DataFrame):
    G = nx.Graph()
    if '作者关键词' in df.columns:
        for keywords in df['作者关键词'].dropna():
            kws = [k.strip().lower() for k in keywords.split(';')]
            for u, v in combinations(set(kws), 2):
                if G.has_edge(u, v):
                    G[u][v]['weight'] += 1
                else:
                    G.add_edge(u, v, weight=1)
    return G

def calculate_coupling(df):
    """计算作者耦合关系"""
    if '作者' not in df.columns:
        st.warning("数据中缺少'作者'列")
        return pd.DataFrame()
    
    coupling_data = []
    
    for _, row in df.iterrows():
        authors = str(row['作者']).split(';') if pd.notna(row['作者']) else []
        authors = [author.strip() for author in authors if author.strip()]
        
        # 计算每对作者的耦合关系
        for i in range(len(authors)):
            for j in range(i + 1, len(authors)):
                coupling_data.append({
                    'source': authors[i],
                    'target': authors[j],
                    'weight': 1
                })
    
    if coupling_data:
        coupling_df = pd.DataFrame(coupling_data)
        # 合并相同的合作关系
        coupling_df = coupling_df.groupby(['source', 'target']).agg({'weight': 'sum'}).reset_index()
        return coupling_df
    else:
        return pd.DataFrame()

def calculate_author_collaboration_network(df):
    """计算作者合作网络"""
    return calculate_coupling(df)
