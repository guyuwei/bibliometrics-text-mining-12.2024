import re
import pandas as pd
import streamlit as st
from collections import defaultdict
import itertools


from collections import defaultdict
import itertools
import plotly.graph_objects as go


# 数据处理函数：计算作者合作关系
def process_author_data(df):
    """
    处理作者数据，计算作者合作关系
    :param df: 包含作者信息的DataFrame
    :return: 合作关系DataFrame（source, target, weight）
    """
    co_occurrence = defaultdict(int)

    # 优先使用"作者"字段，如果没有则尝试"作者地址"字段
    author_column = None
    if '作者' in df.columns:
        author_column = '作者'
    elif '作者地址' in df.columns:
        author_column = '作者地址'
    else:
        return pd.DataFrame()

    # 遍历每一行的作者字段
    for authors in df[author_column].dropna():
        if author_column == '作者':
            # 直接从作者字段提取，用分号分隔
            authors_list = [author.strip() for author in str(authors).split(';') if author.strip()]
        elif author_column == '作者地址':
            # 从作者地址字段提取，使用正则表达式
            pattern = r'\[(.*?)\](.*?)(?=\.)'
            matches = re.findall(pattern, str(authors))
            authors_list = []
            for each in matches:
                rest_info = each[0].replace("；", ";").replace("，", ",").replace(" ", "")
                author_info = rest_info.split(";")
                for author in author_info:
                    author_cleaned = author.strip().title().rstrip('.').replace(",", " ")
                    if author_cleaned:
                        authors_list.append(author_cleaned)

        # 计算每对作者的共现次数
        if len(authors_list) > 1:
            for pair in itertools.combinations(set(authors_list), 2):
                sorted_pair = tuple(sorted(pair))  # 确保作者对的顺序一致
                co_occurrence[sorted_pair] += 1
    
    # 将结果转换为DataFrame
    edges = [{"source": k[0], "target": k[1], "weight": v} for k, v in co_occurrence.items()]
    return pd.DataFrame(edges)



#统计每个作者的出版量和引用数
def calculate_number_of_authors_publication(df):
    # 优先使用"作者"字段，如果没有则尝试"作者地址"字段
    author_column = None
    citation_column = None
    
    # 检查作者字段
    if '作者' in df.columns:
        author_column = '作者'
    elif '作者地址' in df.columns:
        author_column = '作者地址'
    else:
        st.write("DataFrame 中缺少作者相关列。")
        return pd.DataFrame()
    
    # 检查引用字段
    if '核心合集的被引频次计数' in df.columns:
        citation_column = '核心合集的被引频次计数'
    else:
        st.write("DataFrame 中缺少引用相关列。")
        return pd.DataFrame()
    
    authors_citations = {}  # 存储作者的引用数
    authors_documents = {}  # 存储作者的文档数量
    
    # 处理作者信息
    for index, row in df.iterrows():
        authors_text = str(row[author_column])
        citations = row[citation_column]
        
        # 确保citations是数值类型
        try:
            if pd.notna(citations):
                citations_value = float(citations) if str(citations).replace('.', '').replace('-', '').isdigit() else 0
            else:
                citations_value = 0
        except (ValueError, TypeError):
            citations_value = 0
        
        if author_column == '作者':
            # 直接从作者字段提取，用分号分隔
            if pd.notna(authors_text) and authors_text.strip():
                author_list = [author.strip() for author in authors_text.split(';') if author.strip()]
                for author in author_list:
                    author_cleaned = author.strip().title().rstrip('.').replace(",", " ")
                    # 统计引用数
                    if author_cleaned in authors_citations:
                        authors_citations[author_cleaned] += citations_value
                    else:
                        authors_citations[author_cleaned] = citations_value
                    # 统计文档数量
                    if author_cleaned in authors_documents:
                        authors_documents[author_cleaned] += 1
                    else:
                        authors_documents[author_cleaned] = 1
        
        elif author_column == '作者地址':
            # 从作者地址字段提取，使用正则表达式
            pattern = r'\[(.*?)\](.*?)(?=\.)'
            matches = re.findall(pattern, authors_text)
            for each in matches:
                rest_info = each[0].replace("；", ";").replace("，", ",").replace(" ", "")  # 去除空格
                author_info = rest_info.split(";")
                for author in author_info:
                    author_cleaned = author.strip().title().rstrip('.').replace(",", " ")
                    if author_cleaned:  # 确保作者名不为空
                        # 统计引用数
                        if author_cleaned in authors_citations:
                            authors_citations[author_cleaned] += citations_value
                        else:
                            authors_citations[author_cleaned] = citations_value
                        # 统计文档数量
                        if author_cleaned in authors_documents:
                            authors_documents[author_cleaned] += 1
                        else:
                            authors_documents[author_cleaned] = 1

    if authors_citations:
        authors_stats = pd.DataFrame({
            '作者': list(authors_citations.keys()),
            'Citations': list(authors_citations.values()),
            'Documents': list(authors_documents.values())
        })
        return authors_stats
    else:
        st.write("无法从数据中提取作者信息。")
        return pd.DataFrame()


#计算核心作者的文章数量：
def calculate_core_author_publication(core_author_df, df):
    core_author_list = core_author_df["作者"].astype('str').unique()  # 获取独特的核心作者名单
    unique_articles_with_core_authors = set()  # 存储包含核心作者的唯一文章标识

    # 优先使用"作者"字段，如果没有则尝试"作者地址"字段
    author_column = None
    if '作者' in df.columns:
        author_column = '作者'
    elif '作者地址' in df.columns:
        author_column = '作者地址'
    else:
        raise ValueError("DataFrame 中缺少作者相关列。")
    
    # 检查是否有文献标题列
    if '文献标题' not in df.columns:
        raise ValueError("DataFrame 中缺少 '文献标题' 列。")

    for index, row in df.iterrows():
        authors_text = str(row[author_column])
        author_title = row['文献标题']
        
        if author_column == '作者':
            # 直接从作者字段提取，用分号分隔
            if pd.notna(authors_text) and authors_text.strip():
                author_list = [author.strip() for author in authors_text.split(';') if author.strip()]
                for author in author_list:
                    author_cleaned = author.strip().title().rstrip('.').replace(",", " ")
                    if author_cleaned in core_author_list:
                        unique_articles_with_core_authors.add(author_title)
                        break  # 找到核心作者后，跳出循环
        
        elif author_column == '作者地址':
            # 从作者地址字段提取，使用正则表达式
            pattern = r'\[(.*?)\](.*?)(?=\.)'
            matches = re.findall(pattern, authors_text)
            for each in matches:
                rest_info = each[0].replace("；", ";").replace("，", ",").replace(" ", "")  # 去除空格
                author_info = rest_info.split(";")
                for author in author_info:
                    author_cleaned = author.strip().title().rstrip('.').replace(",", " ")
                    if author_cleaned in core_author_list:
                        unique_articles_with_core_authors.add(author_title)
                        break  # 找到核心作者后，跳出循环

    # 返回包含核心作者的独特文章的标题
    return unique_articles_with_core_authors

import pandas as pd
from collections import defaultdict

def calculate_publication_by_author(df: pd.DataFrame):
    co_occurrence = defaultdict(int)
    
    # 优先使用"作者"字段，如果没有则尝试"作者地址"字段
    author_column = None
    if '作者' in df.columns:
        author_column = '作者'
    elif '作者地址' in df.columns:
        author_column = '作者地址'
    else:
        return pd.Series()
    
    for authors in df[author_column].dropna():
        if author_column == '作者':
            # 直接从作者字段提取，用分号分隔
            auths = [a.strip() for a in str(authors).split(';') if a.strip()]
            for a in auths:
                author_cleaned = a.strip().title().rstrip('.').replace(",", " ")
                if author_cleaned:
                    co_occurrence[author_cleaned] += 1
        elif author_column == '作者地址':
            # 从作者地址字段提取，使用正则表达式
            pattern = r'\[(.*?)\](.*?)(?=\.)'
            matches = re.findall(pattern, str(authors))
            for each in matches:
                rest_info = each[0].replace("；", ";").replace("，", ",").replace(" ", "")
                author_info = rest_info.split(";")
                for author in author_info:
                    author_cleaned = author.strip().title().rstrip('.').replace(",", " ")
                    if author_cleaned:
                        co_occurrence[author_cleaned] += 1
    
    return pd.Series(co_occurrence).sort_values(ascending=False)


# Calculate_Anaysis/Calculate_Country.py
import pandas as pd
import re
from collections import Counter

def calculate_publication_by_country(df: pd.DataFrame):
    if '作者地址' not in df.columns:
        return pd.Series()
    pattern = r"\[(.*?)\](.*?)(?=\.)"
    countries = []
    for addr in df['作者地址'].dropna().astype(str):
        matches = re.findall(pattern, addr)
        for m in matches:
            country = m[-1].split(',')[-1].strip()
            if country == 'Taiwan': country = 'Chinese Taiwan'
            countries.append(country)
    return pd.Series(Counter(countries)).sort_values(ascending=False)