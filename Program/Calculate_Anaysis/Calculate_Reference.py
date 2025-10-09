import streamlit as st
import pandas as pd
import re
import sys

def extract_authors(reference_text):
    # 正则表达式：匹配作者名（姓+名或名+姓的形式，支持姓+名缩写的组合）
    # 这里我们假设作者姓名是由字母组成的，且每个名字由空格分隔
    author_pattern = r'([A-Za-z]+(?: [A-Za-z]+\.)?)+'

    # 提取所有作者名
    authors = re.findall(author_pattern, reference_text)

    # 去除无意义的单词（如"Autodesk"等公司名称，通常是多个单词）
    valid_authors = [author.strip() for author in authors if len(author.split()) > 1]
    total_valid_authors=[]
    for i in valid_authors:
        author_cleaned = i.strip().title().rstrip('.')
        total_valid_authors.append(author_cleaned)
    # 去重并排序
    unique_authors = sorted(set(total_valid_authors))
    return unique_authors


def calculate_number_of_total_references_cited(df):
    number_of_total_articles = df.shape[0]
    if '引用的参考文献数' in df.columns:
        total_references_cited = df['引用的参考文献数'].astype(int)
        number_of_total_reference_cited = total_references_cited.sum()
        average_reference_per_doc = number_of_total_reference_cited / number_of_total_articles
    else:
        number_of_total_reference_cited = 0
        average_reference_per_doc = 0
        st.warning(
            "数据中缺少'引用的参考文献数'列，无法计算平均每篇文献的引用文献数量: 在EXCEL中检查该csv的列名与字段是否完全一致")
    return number_of_total_reference_cited, average_reference_per_doc


# 提取每篇文章的作者引文作者
def extract_each_article_author_refauthor(df):
    article_author={}#存储每篇文章的作者
    article_refauthor={}#存储每篇文章的引文作者
    if '作者地址' in df.columns and '引用的参考文献' and '文献标题' in df.columns:
        sum_title=df["文献标题"].astype(str)
        # 遍历每篇文章的作者和引用的参考文献作者
        for index, each_title  in sum_title.items():
            references_cited = df.loc[index, '引用的参考文献']
            if pd.isna(references_cited):
                continue
                each_refauthor=""
            else:
                #提取每篇文章的引文作者
                each_refauthor = extract_authors(references_cited)
            article_refauthor[each_title] = sorted(each_refauthor)
            # 提取每篇文章的作者
            each_ariticle_author = []
            each_Correspondingauthoraddress = df.loc[index, '作者地址']
            pattern = r'\[(.*?)\](.*?)(?=\.)'
            matches = re.findall(pattern, each_Correspondingauthoraddress)
            for each in matches:
                rest_info = each[0].replace("；", ";").replace("，", ",").replace(" ", "")  # 去除空格
                author_info = rest_info.split(";")
                for author in author_info:
                    author_cleaned = author.strip().title().rstrip('.')
                    author_cleaned=author_cleaned.replace(",", " ")
                    each_ariticle_author.append(author_cleaned)

            article_author[each_title] =sorted(set(each_ariticle_author))
        authors_stats = pd.DataFrame({
                    "文献标题":list(article_author.keys()),
                    '作者': list(article_author.values()),
                })
        refauthors_stats = pd.DataFrame({
                    "文献标题":list(article_author.keys()),

                    '引文作者': list(article_refauthor.values()),
                })
        return authors_stats ,refauthors_stats
    else:
        st.warning("数据中缺少 '引用的参考文献' 列，无法提取引用信息。")
        return pd.DataFrame(),pd.DataFrame()

def extract_reference_info(df):
    authors_ref_authors = {}  # 存储作者的引文作者
    co_authorship_dict = {}  # 存储共同引用关系
    return None
# def extract_reference_info(df):

#         for author in author_info:
#                     author_cleaned = author.strip().title().rstrip('.')
#                     # 统计引用关系：即每个作者引用的作者
#                     if author_cleaned in article_author_refauthor:
#                         references_cited_2=references_cited
#                         references_cited_2=extract_authors(references_cited_2)
#                         authors_ref_authors[author_cleaned].append(references_cited_2)
#                     else:
#                         authors_ref_authors[author_cleaned] = [references_cited_2]
#
#                     # 记录共同引用关系：即多个作者共同引用了某个参考文献
#                     for co_author in author_info:
#                         co_author_cleaned = co_author.strip().title().rstrip('.')
#                         if author_cleaned != co_author_cleaned:
#                             pair = tuple(sorted([author_cleaned, co_author_cleaned]))  # 排序确保无论谁先谁后都一致
#                             if pair in co_authorship_dict:
#                                 co_authorship_dict[pair] += 1  # 共同引用次数增加
#                             else:
#                                 co_authorship_dict[pair] = 1  # 初始化共同引用次数
#
#         # 提取引用作者和共同引用关系
#         total_authors_in_articles = list(authors_ref_authors.keys())
#         total_references_cited = list(authors_ref_authors.values())
#         # 统计每篇引用文献的作者
#         total_references_info = []
#         for reference in total_references_cited:
#             if isinstance(reference, str) and reference.strip():  # 确保是非空字符串
#                 reference_authors = extract_authors(reference)
#                 total_references_info.append(reference_authors)
#             else:
#                 total_references_info.append([])  # 空值时，返回空列表
#
#         authors_df = pd.DataFrame(total_authors_in_articles, columns=["作者"])
#         references_df_authors = pd.DataFrame(total_references_info)
#         # 将引用关系和共同引用关系转换为 DataFrame
#         citation_edges = []
#         citation_counts = {}  # 存储引用关系的次数
#         for author_a, cited_references in authors_ref_authors.items():
#             for reference in cited_references:
#                 for author_b in extract_authors(reference):  # 假设extract_authors从引用中提取作者
#                     if author_a != author_b:
#                         pair = tuple(sorted([author_a, author_b]))  # 确保排序
#                         citation_counts[pair] = citation_counts.get(pair, 0) + 1
#
#         # 使用引用次数作为边的权重
#         citation_edges = [(author_a, author_b, count) for (author_a, author_b), count in citation_counts.items()]
#         co_authorship_edges = [(a, b, weight) for (a, b), weight in co_authorship_dict.items()]
#
#         # 创建DataFrame
#         citation_network_df = pd.DataFrame(citation_edges, columns=["author_a", "author_b", "weight"])
#         co_authorship_network_df = pd.DataFrame(co_authorship_edges, columns=["author_a", "author_b", "weight"])
#
#         return authors_stats, authors_df, references_df_authors, citation_network_df, co_authorship_network_df
#     else:
#         st.warning("数据中缺少 '引用的参考文献' 列，无法提取引用信息。")
#         return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


def filter_references_by_authors(author_list,reference_list):
    authors_in_articles =author_list
    references_in_articles =[]
    for i in reference_list:
        if i :
            references_in_articles.append(i)
    total_authors_in_articles =list(set(authors_in_articles))
    total_reference_authors =list(set(references_in_articles))
    total_filtered_references=[]
    for ref in total_reference_authors:
        if ref in total_authors_in_articles:
            total_filtered_references.append(ref)
    filtered_df = pd.DataFrame(total_filtered_references)
    return filtered_df,total_reference_authors,total_authors_in_articles,total_filtered_references

