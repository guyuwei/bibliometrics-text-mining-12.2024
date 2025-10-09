import streamlit as st
import pandas as pd
# 计算期刊总数
def custom_title_case(title):
    # 定义不需要大写的单词列表
    lowercase_words = {'of', 'in', 'and', 'the', 'for', 'on', 'with', 'at', 'by', 'to'}

    # 将标题拆分为单词列表
    words = title.split()

    # 对每个单词进行处理
    result = []
    for word in words:
        # 如果单词在不需要大写的列表中，保持小写
        if word.lower() in lowercase_words:
            result.append(word.lower())
        else:
            # 否则将单词首字母大写
            result.append(word.title())

    # 将处理后的单词列表重新组合为字符串
    return ' '.join(result)


def calculate_number_of_sources(df):
    if '出版物名称' in df.columns:
        total_unique_publicationnames = set(df['出版物名称'].astype(str).dropna())
        for title in total_unique_publicationnames:
            formatted_title = custom_title_case(title)
        number_of_total_unique_publicationname = len(total_unique_publicationnames)
        return total_unique_publicationnames, number_of_total_unique_publicationname
    else:
        st.warning("数据中缺少'出版物名称'列，无法计算关键词总数:在EXCEL中检查该csv的列名与字段是否完全一致")
        return set(), 0

#统计每个sources的出版量和引用数
def calculate_number_of_sources_publication(df):
    if df.empty or '出版物名称' not in df.columns or '核心合集的被引频次计数' not in df.columns:
        st.write("DataFrame 中缺少必要的列或为空。")
        return pd.DataFrame()

    sources_citations = {}  # 存储期刊的引用数
    sources_documents = {}  # 存储期刊的文档数量
    # 提取每篇文章的期刊
    sum_sources = df['出版物名称'].astype(str)
    for index, title in sum_sources.items():
        formatted_title = custom_title_case(title)
        citations = df.loc[index, '核心合集的被引频次计数']

        # 安全处理citations值，确保是数值类型
        try:
            # 确保citations是标量值，不是Series
            if isinstance(citations, pd.Series):
                citations = citations.iloc[0] if len(citations) > 0 else 0
            
            if pd.notna(citations):
                citations_value = float(citations) if str(citations).replace('.', '').replace('-', '').isdigit() else 0
            else:
                citations_value = 0
        except (ValueError, TypeError):
            citations_value = 0

        if formatted_title in sources_citations:
            sources_citations[formatted_title] += citations_value
        else:
            sources_citations[formatted_title] = citations_value
        # 统计文档数量
        if formatted_title in sources_documents:
            sources_documents[formatted_title] += 1
        else:
            sources_documents[formatted_title] = 1

    sources_stats = pd.DataFrame({
        'Sources': list(sources_citations.keys()),
        'Documents': list(sources_documents.values()),
        'Citations': list(sources_citations.values())
    })

    return sources_stats


def filter_and_sort_data(df, min_citations, min_documents, drop_sources, sources_list):
    """
    根据条件筛选和排序数据

    参数:
    - df: 原始数据框
    - min_citations: 最小引文量
    - min_documents: 最小文档量
    - drop_sources: 需要排除的期刊列表
    - sources_list: 所有期刊列表

    返回:
    - 筛选和排序后的数据框
    """
    # 筛选满足条件的期刊
    filtered_df = df[
        (df["Citations"] >= min_citations) &
        (df['Documents'] >= min_documents)
        ]

    # 生成不排除的期刊列表
    nodrop_source_list = [source for source in sources_list if source not in drop_sources]

    filtered_df = filtered_df[filtered_df['Sources'].isin(nodrop_source_list)]

    # 按引文量降序排序
    return filtered_df.sort_values(by='Citations', ascending=False)


import pandas as pd

def calculate_number_of_sources(df: pd.DataFrame):
    if '期刊名称' in df.columns:
        return df['期刊名称'].value_counts()
    else:
        return pd.Series(dtype='object')