import streamlit as st
import re
import matplotlib.pyplot as plt
import pandas as pd
#国际合作
def calculate_collaboration_countries(df):
    if '作者地址' in df.columns:
        total_authors = []#作者地址提取的所有作者:2层嵌套
        summary_total_authors = []#作者地址提取的所有作者:1层嵌套
        num_of_single_author_articles=0
        total_collaboration_countries = []  # 所有文章的所有国家
        summary_total_countries = []  # 所有文章的所有国家：1层嵌套
        total_international_papers = 0
        number_of_single_country_papers = 0
        # ——————————01:提取每篇文章的所有作者
        if '作者地址' in df.columns:
            total_authors = []  # 作者地址提取的所有作者:2层嵌套
            summary_total_authors = []  # 作者地址提取的所有作者:1层嵌套

            # ——————————01:提取每篇文章的所有作者

            Correspondingauthoraddress = df['作者地址'].astype(str)
            for each_Correspondingauthoraddress in Correspondingauthoraddress:
                each_collaboration_countries=[]
                pattern = r'\[(.*?)\](.*?)(?=\.)'
                matches = re.findall(pattern, each_Correspondingauthoraddress)
                for each in matches:
                    rest_info = each[0].replace("；", ";").replace("，", ",")
                    author_info = rest_info.split(";")
                    for i in author_info:
                        author_info_st = i.strip().title().rstrip(
                            '.')
                        total_authors.append([author_info_st])
                        summary_total_authors.append(author_info_st)
            # ——————————02:提取每篇文章的国家
                for each in matches:
                    rest_info = each[-1]
                    country_info = rest_info.split(',')[-1].split(' ')[-1]
                    if country_info == "Taiwan":
                        country_info = "Chinese Taiwan"
                    each_collaboration_countries.append(country_info)

                total_collaboration_countries.append(set(each_collaboration_countries))  # 所有文章的所有国家：2层嵌套
                summary_total_countries.extend(set(each_collaboration_countries))

        unique_total_authors = set(summary_total_authors)  # 不重复的所有作者
        number_of_total_authors = len(summary_total_authors)  # 统计所有作者数量
        number_of_total_unique_authors = len(unique_total_authors)  # 统计所有不重复的作者数量
        average_authors_per_doc=number_of_total_authors/df.shape[0]
        for i in total_authors:
            if len(i) == 1:
                num_of_single_author_articles += 1
            else:
                st.write(i)
        for each in total_collaboration_countries:
            # __________________03:提取国际合作文献
            if len(each) == 1:
                number_of_single_country_papers = number_of_single_country_papers + 1
            elif len(each) > 1:
                total_international_papers = total_international_papers + 1
            # ——————————————————03:计算国际合作文献所占比例
        international_cooperation_percentage = (total_international_papers / df.shape[0]) * 100
    else:
        number_of_single_country_papers=0
        num_of_single_author_articles=0
        number_of_total_authors=0
        international_cooperation_percentage = 0
        st.warning("数据中缺少'作者地址'列，无法绘制年度发文量相关图表:在EXCEL中检查该csv的列名与字段是否完全一致")
    result=[(total_collaboration_countries, summary_total_countries, number_of_single_country_papers, international_cooperation_percentage),
            (number_of_total_authors,number_of_total_unique_authors,num_of_single_author_articles,average_authors_per_doc)]
    return (result )
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


import pandas as pd
import re

def  calculate_publication_by_country(df):
    # 检查必要的列是否存在
    if '作者地址' in df.columns and '核心合集的被引频次计数' in df.columns and '出版年' in df.columns:
        countries_citations = {}  # 存储每个国家的总引用数
        countries_documents = {}  # 存储每个国家的总文档数
        countries_years = {}      # 存储每个国家的年份列表
        total_collaboration_countries = []  # 存储每篇文章的国家列表
        summary_total_countries = []        # 存储所有文章的国家列表

        # 处理每篇文章的作者地址
        Correspondingauthoraddress = df['作者地址'].astype(str)
        for index, each_Correspondingauthoraddress in enumerate(Correspondingauthoraddress):
            each_collaboration_countries = []
            pattern = r'\[(.*?)\](.*?)(?=\.)'
            matches = re.findall(pattern, each_Correspondingauthoraddress)
            for each in matches:
                rest_info = each[-1]
                country_info = rest_info.split(',')[-1].split(' ')[-1]
                if country_info == "Taiwan":
                    country_info = "Chinese Taiwan"
                each_collaboration_countries.append(country_info)

            # 去重并保存每篇文章的国家列表
            total_collaboration_countries.append(list(set(each_collaboration_countries)))
            summary_total_countries.extend(list(set(each_collaboration_countries)))

        # 将国家列表添加到DataFrame中
        df['country'] = total_collaboration_countries
        total_collaboration_countries = df['country'].astype(str)
        # 统计每个国家的引用数、文档数和年份
        for index, each_countries in total_collaboration_countries.items():
            citations = df.loc[index, '核心合集的被引频次计数'].astype(int)
            year = df.loc[index, '出版年'].astype(int)
            each_countries = each_countries.replace("'","").replace("[","").replace("]","").split(", ")
            for each in each_countries:
                # 更新引用数
                if each in countries_citations:
                    countries_citations[each] += citations
                else:
                    countries_citations[each] = citations

                # 更新文档数
                if each in countries_documents:
                    countries_documents[each] += 1
                else:
                    countries_documents[each] = 1

                # 更新年份列表
                if each in countries_years:
                    countries_years[each].append(year)
                else:
                    countries_years[each] = [year]

        # 创建包含统计信息的DataFrame
        countries_stats = pd.DataFrame({
            'Areas': list(countries_citations.keys()),
            'Documents': list(countries_documents.values()),
            'Citations': list(countries_citations.values()),
            'Years': list(countries_years.values())
        })

        # 计算平均引用数
        countries_stats['Average Citation/Publication'] = [
            citations / documents if documents > 0 else 0
            for citations, documents in zip(countries_citations.values(), countries_documents.values())
        ]

        return countries_stats

    else:
        print("DataFrame 中缺少必要的列。")
        return pd.DataFrame()

def calculate_number_of_countries_publication(df):
    """计算各国发文数量"""
    if '作者地址' not in df.columns:
        st.warning("数据中缺少'作者地址'列")
        return pd.Series()
    
    country_counts = {}
    
    for _, row in df.iterrows():
        address = str(row['作者地址'])
        # 提取国家信息
        pattern = r'\[(.*?)\](.*?)(?=\.)'
        matches = re.findall(pattern, address)
        
        for each in matches:
            rest_info = each[-1]
            country_info = rest_info.split(',')[-1].split(' ')[-1]
            if country_info == "Taiwan":
                country_info = "Chinese Taiwan"
            
            if country_info in country_counts:
                country_counts[country_info] += 1
            else:
                country_counts[country_info] = 1
    
    return pd.Series(country_counts).sort_values(ascending=False)