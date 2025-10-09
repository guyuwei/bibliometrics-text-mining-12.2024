import math
import os
import sys
import seaborn as sns
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

sns.set_theme(style="whitegrid")

current_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.dirname(current_dir).replace("/Program","")
library_dir=project_root+ '/library/web_sources/'
picture_path=project_root+ '/output/picture'
csv_path= project_root+'/output/'
pic_indoc_path= library_dir=project_root+ '/library/doc_pic/'
sys.path.append(os.path.join(project_root, 'Calculate_Anaysis'))
sys.path.append(os.path.join(project_root, 'Documents_Processing'))
sys.path.append(os.path.join(project_root, 'Result_Visualization'))
from Calculate_Anaysis.Calculate_Author import calculate_core_author_publication,calculate_number_of_authors_publication
from Calculate_Anaysis.Calculate_Country import calculate_collaboration_countries,calculate_number_of_countries_publication
from Calculate_Anaysis.Calculate_Publication import calculate_publications_per_year
from Calculate_Anaysis.Calculate_Sources import calculate_number_of_sources,calculate_number_of_sources_publication,filter_and_sort_data
from Calculate_Anaysis.Calculate_Keywords import calculate_number_of_keywords
from Calculate_Anaysis.Calculate_Reference import calculate_number_of_total_references_cited
from Calculate_Anaysis.Calculate_Citiation import calculate_number_of_total_Timescitedcount
from Calculate_Anaysis.Calculate_Year import calculate_age
from Documents_Processing.Web_Format import st_radio, st_multiselect, st_markdown, st_latex, st_dataframe, st_subsubheader, st_subheader, st_button
from Documents_Processing.Uploading_Files import Load_TXT,Load_CSV

def save_and_upload_file(df, df_name, autotext):
    st_subsubheader(" 📥 Please save the information as soon as it is filled in.")
    Save_Form_to_Csv(df_name=df_name, df=df, autotext=autotext)
    st_subsubheader(" 📤 Open Another File")
    uploaded_file = st.file_uploader("Load Another Journal File", type="CSV", label_visibility="collapsed")
    return uploaded_file
def Save_Form_to_Csv(df_name, df,autotext,csv_path=csv_path):
    user_input_path =csv_path
    user_input_name = st.text_input("请输入" + df_name + "保存文件名",label_visibility="collapsed",value=autotext,).title()
    if user_input_name and not user_input_name.endswith('.csv'):
                user_input_name += '.csv'
    file_name =user_input_path+user_input_name
    col5, col6 = st.columns([1, 2])
    with col5:
        if st_button("Download " + df_name + " Table File"):
            df.to_csv(file_name, index=False, header=True)
            with col6:
                st.success(f"🎉{df_name} 成果保存至：{ file_name } 文件！")
                st.snow()




def process_tabledescribe_tab(df):

    number_of_total_articles = df.shape[0]
    count_result = {}  # 数据库的info
    missing_value_columns = st_multiselect('Select the parameters to be counted:', sorted(df.columns), default=df.columns)
    if missing_value_columns:
        for para in missing_value_columns:
            count_result[para] = {"共计": str(len(df[para].value_counts())), "缺失值": str(number_of_total_articles - len(df[para].value_counts()))}
        count_result = pd.DataFrame(count_result).sort_index(axis=1)
        st_dataframe(count_result,width=500, height=400,use_container_width=True)
        return number_of_total_articles
def process_Overall_Information_Overview_Tab(df,start,stop):
    st_subheader("Distribution of information on articles included in this database")

    number_of_total_articles = df.shape[0]
    sorted_data, years, publications_per_year = calculate_publications_per_year(df)
    total_keywords, total_unique_keywords, number_of_total_keywords, number_of_unique_keywords = calculate_number_of_keywords(df)
    try:
        sources_result = calculate_number_of_sources(df)
        if sources_result and len(sources_result) == 2:
            total_unique_publicationnames, number_of_total_unique_publicationname = sources_result
        else:
            total_unique_publicationnames, number_of_total_unique_publicationname = set(), 0
    except Exception as e:
        st.warning(f"计算期刊数量时出错: {str(e)}")
        total_unique_publicationnames, number_of_total_unique_publicationname = set(), 0
    try:
        citation_result = calculate_number_of_total_Timescitedcount(df)
        if citation_result and len(citation_result) == 2:
            number_of_total_Timescitedcount, average_citations_per_doc = citation_result
        else:
            number_of_total_Timescitedcount, average_citations_per_doc = 0, 0
    except Exception as e:
        st.warning(f"计算引用统计时出错: {str(e)}")
        number_of_total_Timescitedcount, average_citations_per_doc = 0, 0
    collaboration_result = calculate_collaboration_countries(df)
    total_collaboration_countries, summary_total_countries, number_of_single_country_papers, international_cooperation_percentage = collaboration_result[0]
    number_of_total_authors, number_of_total_unique_authors, num_of_single_author_articles, average_authors_per_doc = collaboration_result[1]
    try:
        reference_result = calculate_number_of_total_references_cited(df)
        if reference_result and len(reference_result) == 2:
            number_of_total_reference_cited, average_reference_per_doc = reference_result
        else:
            number_of_total_reference_cited, average_reference_per_doc = 0, 0
    except Exception as e:
        st.warning(f"计算参考文献统计时出错: {str(e)}")
        number_of_total_reference_cited, average_reference_per_doc = 0, 0
    Timespan = str(start) + '--' + str(stop)
    total_ages, average_age_per_doc = calculate_age(df)
    caluate_year_add_rate_publication = 0
    for i, v in enumerate(years):
        if start <= v <= stop:
            caluate_year_add_rate_publication = caluate_year_add_rate_publication + publications_per_year[i]
    annual_growth_publication_rate = caluate_year_add_rate_publication / (stop - start)
    # ——————————————————————————————————————————————————————# （一）总体信息概览：网页布局
    data = [
        ["Timespan", Timespan, "Sources", number_of_total_unique_publicationname],
        ["Documents", number_of_total_articles, "Annual Growth Rate", f"{annual_growth_publication_rate:.2f}%"],
        ["Authors", number_of_total_unique_authors, "Authors of single-authored docs：内测中", num_of_single_author_articles],
        ["International Co-Authorship", f"{international_cooperation_percentage:.2f}%", "Co-Authors per Doc", f"{average_authors_per_doc:.2f}"],
        ["Author's Keywords (DE)", number_of_unique_keywords, "References", number_of_total_reference_cited],
        ["Document Average Age", f"{average_age_per_doc:.2f}", "Average citations per doc", f"{average_citations_per_doc:.2f}"]
    ]
    info_df = pd.DataFrame(data, columns=["Metric ", "Value 1", "Metric 2", "Value 2"])
    st_dataframe(info_df,height=300,width=300,use_container_width=True)
    col3, col4 = st.columns([2,2])
    with col3:
        with st.expander("参数设置 ",expanded=False,icon="🛠️"):
            st.write("刻度线")
            a = st.radio(label="刻度线", options=["grid on", 'grid off', "仅x轴", '仅y轴'], horizontal=False,index=0,label_visibility="collapsed")
            st.write("线条颜色")
            line_colour = st.radio(label="线条颜色", options=['blue', 'red', 'black', 'green'], horizontal=False,index=2,label_visibility="collapsed")
        with col4:
            plot=st.button("Plot the annual output curve of the journal".title(), use_container_width=True, icon='📈')
    col1, col2 = st.columns(2)
    if plot:
            with col1:
                st.write("Annual Scientific Production")

                fig = plt.figure(dpi=500, figsize=[14, 5])
                plt.plot(years, publications_per_year, marker='*', linestyle='-', color=line_colour, linewidth=1.5)
                plt.xticks(ticks=range(start - 1, stop + 1, 1), fontsize=15)
                plt.xlabel("Year", fontsize=15)
                plt.ylabel("Articles", fontsize=15)
                step = int((max(publications_per_year) - min(publications_per_year)) / 5)
                plt.yticks(ticks=range(min(publications_per_year), max(publications_per_year) + 2, step), fontsize=15)
                plt.title('Annual Scientific Production', fontsize=16)
                if a == "grid on":
                    plt.grid()
                elif a == "仅x轴":
                    plt.grid(axis='x')
                elif a == "仅y轴":
                    plt.grid(axis='y')
                st.pyplot(fig, use_container_width=True)
            with col2:
                st.info("📊 图表展示区域 - 可在此处展示您的分析结果")

    return number_of_total_unique_authors
def process_Publication_Author_Analysis_Tab(df,number_of_total_unique_authors,number_of_total_articles):
    st_subheader("Distribution of author information in this database by research area")
    number_of_authors_publication_dict = calculate_number_of_authors_publication(df)
    number_of_authors_publication_df = pd.DataFrame(
        number_of_authors_publication_dict)
    total_unique_author_documents = number_of_authors_publication_df["Documents"].astype(int)
    total_unique_author_citations = number_of_authors_publication_df["Citations"].astype(int)
    n_max = max(total_unique_author_documents)  # 产出最多的作者发表的文章数量
    most_citiations = max(total_unique_author_citations)  # 被引量最多的作者的被引数量
    m = 0.749 * np.sqrt(n_max)  # 计算核心作者发表文章的最少数量 m
    rounded_m = math.ceil(m)  # 进1取整
    core_author_df = number_of_authors_publication_df[(number_of_authors_publication_df['Documents'] >= rounded_m)]  # 以m为阈值，筛选核心作者
    core_authors_count = core_author_df.shape[0]  # 核心作者数量
    core_author_unique_articles = calculate_core_author_publication(core_author_df, df)  # 遍历所有文章，筛选作者中至少包含一个核心作者的文章
    number_of_core_authors_articles = len(core_author_unique_articles)
    with st.expander("Price\'s Law Explanation",expanded=False):
        st_markdown(r'1. **Core Concept**')
        st_latex(r'\sum_{m+1}^{I} n(x) = \sqrt{N}')
        st_markdown(
            r'2. **Minimum Publications for Core Authors**')
        st_latex(r'm=0.749*\sqrt{n_{max}} ')
        data = [
            ["作者数量(N)", int(number_of_total_unique_authors)],
            ['总文章数量的一半', math.ceil(0.5 * number_of_total_articles)],
            ['该领域最多产的作家发表的文章数量(nmax)', int(n_max)],
            ["核心作者发表文章的最少数量(m)", int(rounded_m)],
            ["核心作者数量", core_authors_count],
            ["核心作者占总作者数量的百分比",
             f"{(core_authors_count / number_of_total_unique_authors) * 100:.2f}%"],

            ["核心作者发表的文章数量",
             number_of_core_authors_articles],
            ["核心作者发表文章占总文章的百分比",
             f"{(number_of_core_authors_articles / number_of_total_articles) * 100:.2f}%"]
        ]
    # st.sidebar.markdown("公式计算结果")

    info_df = pd.DataFrame(data, columns=["Metric", 'Value'])
    st_dataframe(info_df, use_container_width=True,height=330,width=300)
    return  n_max,rounded_m,most_citiations,number_of_authors_publication_df
def process_Publication_Author_Tab_Most_Productive(n_max,rounded_m,most_citiations,number_of_authors_publication_df):
    file_name = os.path.join(csv_path, "H_index&Affiliation.csv")
    st.subheader("Author rank in field of study: please enter additional information")
    col1, col2 = st.columns([3,1])
    edited_df_productive_authors=number_of_authors_publication_df

    if 'Affiliation' not in  edited_df_productive_authors.columns:
        edited_df_productive_authors['Affiliation'] = ''
    if 'H-index' not in    edited_df_productive_authors.columns:
        edited_df_productive_authors['H-index'] = ''
    with col1:
        with st.expander("Parsing Result",expanded=True):
            edited_df_productive_authors = st.data_editor(edited_df_productive_authors, use_container_width=True, height=350)
            authors_list= edited_df_productive_authors["作者"].tolist()

    with col2:
        st_subsubheader(" 📥  可选：保存作者信息")
        # 使保存变为可选操作
        if st.button("💾 保存作者信息", help="点击保存当前作者信息到CSV文件"):
            Save_Form_to_Csv(df_name="Authors Other info",df=edited_df_productive_authors,autotext="Input_H_index&Affiliation")
        st_subsubheader(" 📤 Open  Another File")
        uploaded_file = st.file_uploader("Load  Another File",type="CSV",label_visibility="collapsed")
        if uploaded_file is not None:
            edited_df_productive_authors= Load_CSV(uploaded_file)

            with col1:
                if  "Affiliation" in   edited_df_productive_authors.columns:
                    with st.expander("New upload file content",expanded=True):
                        st.dataframe( edited_df_productive_authors,height=350,width=300,use_container_width=True)
                        authors_list = edited_df_productive_authors["作者"].tolist()

                else:st.warning("Please upload the results of this step")
    st.subheader('The most prolific writer in the field of research')

    col1, col2 = st.columns([3,1])
    with col2:
            top_citation_edited_df_productive_sources = edited_df_productive_authors
            documents_min_productive_authors = st.number_input(
                "统计高产作家：Documents 需大于等于", min_value=0,
                max_value=int(n_max), step=1, value=int(rounded_m))
            citations_min_productive_authors = st.number_input(
                "统计高产作家：Citations 需大于等于", min_value=0,
                max_value=int(most_citiations), value=1, step=1)
            drop_author_list = st_multiselect('不纳入考虑的作者', options=authors_list, default=None)
            nodrop_author_list = []
            for i in authors_list:
                if i not in drop_author_list:
                    nodrop_author_list.append(i)
            top_citation_edited_df_productive_sources = top_citation_edited_df_productive_sources[top_citation_edited_df_productive_sources['作者'].isin(nodrop_author_list)]
            productive_authors_publication_df = top_citation_edited_df_productive_sources[
                (number_of_authors_publication_df['Documents'] >= documents_min_productive_authors) &
                (number_of_authors_publication_df["Citations"] >= citations_min_productive_authors)
                ]
            productive_authors_publication_df = productive_authors_publication_df.sort_values("Citations", ascending=False)
            # 可选保存
            if st.button("💾 保存高产作者信息", key="save_productive_authors"):
                Save_Form_to_Csv(df_name=' Highly Productive Authors ', df=top_citation_edited_df_productive_sources, autotext="Highly Productive Authors in Research Field")

            with col1:
                st.dataframe(productive_authors_publication_df, use_container_width=True, height=500, )

                st.info("📋 表格展示区域 - 可在此处展示详细的作者统计表格")

def process_Journay_Analysis_Tab(df):
    file_name = os.path.join(csv_path, "Journal_Citations.csv")
    st_subheader("Distribution of journal information in this database by field of study")
    # 计算期刊信息
    number_of_sources_publication_df = calculate_number_of_sources_publication(df)
    sources_citiation_list = number_of_sources_publication_df["Citations"].to_list()
    sources_documents_list = number_of_sources_publication_df["Documents"].to_list()

    # 初始化编辑后的数据框
    edited_df_productive_sources = number_of_sources_publication_df.copy()
    edited_df_productive_sources['C/D'] = ''
    edited_df_productive_sources['IF'] = ''
    edited_df_productive_sources['Best Quartile'] = ''

    st.subheader("Ranking of journals in your field of research: please enter additional information")
    col1, col2 = st.columns([3, 1])
    with col1:
        with st.expander("Parsing Results", expanded=True):
            edited_df_productive_sources = st.data_editor( edited_df_productive_sources,
                use_container_width=True,
                width=700,
            )

    top_productive_sources_df = edited_df_productive_sources
    sources_list = top_productive_sources_df ["Sources"].to_list()

    with col2:
        st.subheader(" 📥  可选：保存期刊信息")
        if st.button("💾 保存期刊信息", key="save_journal_info"):
            Save_Form_to_Csv(df_name="Journal Other info", df=edited_df_productive_sources, autotext="Input_Journal_IF")
        st.subheader(" 📤 Open Another File")
        uploaded_file = st.file_uploader("Load Another Journal File", type="CSV", label_visibility="collapsed")

    if uploaded_file is not None:
        try:
            top_productive_sources_df = Load_CSV(uploaded_file)
            with col1:
                if "C/D" in top_productive_sources_df.columns:
                    with st.expander("New upload file content", expanded=True):
                        st.dataframe(top_productive_sources_df, height=350, width=300, use_container_width=True)
                else:
                    st.warning("Please upload the results of this step")
        except Exception as e:
            st.error(f"Error loading file: {e}")
    st.subheader('The most prolific journals in the research field')

    col1, col2 = st.columns([3, 1])
    with col2:
        documents_min_productive_sources = st.number_input(
            "统计高产期刊：Documents 需大于等于", min_value=0,
            max_value=int(max(sources_documents_list)), step=1, value=0)
        citiatiosn_min_productive_sources = st.number_input(
            "统计高产期刊：Citations 需大于等于", min_value=0,
            max_value=int(max(sources_citiation_list)), value=0, step=1)
        drop_sources_list = st.multiselect('不纳入考虑的期刊', options=sources_list, default=None)

    top_citation_edited_df_productive_sources = filter_and_sort_data(
        top_productive_sources_df,
        citiatiosn_min_productive_sources,
        documents_min_productive_sources,
        drop_sources_list,
        sources_list
    )
    top_citation_edited_df_productive_sources = top_citation_edited_df_productive_sources.sort_values(by='Citations', ascending=False)[:10]
    top_citation_sum = top_citation_edited_df_productive_sources["Citations"].sum()
    number_of_total_reference_cited = number_of_sources_publication_df["Citations"].sum()
    top_citation_account_for = top_citation_sum / number_of_total_reference_cited * 100
    with col1:
        st.dataframe(top_citation_edited_df_productive_sources, use_container_width=True, height=500)
        st.subheader('Citations Top 10 Journals: %d of Citations, %.2f%% of total citations' % (top_citation_sum, top_citation_account_for))

        st.info("📋 期刊统计表格展示区域")

    with col2:
        if st.button("💾 保存高产期刊信息", key="save_productive_sources"):
            Save_Form_to_Csv(df_name='Highly Productive Sources', df=top_citation_edited_df_productive_sources, autotext="Highly Productive Sources in Research Field")


    st.markdown("----")

    st_subheader("Visualization of statistical results")
    col3, col4 = st.columns([1, 3])
    with col3:
        with st.expander("期刊绘图-参数设置 ", expanded=False, icon="🛠️"):
            color = st.radio(label="Choose a color for the bars:", options=["blue", "green", "orange", "pink"], horizontal=True, index=0)
            seq = st.radio(label="条形图顺序", options=["Ascending", "Descending"], index=0, horizontal=True)
            bar_width = st.slider("柱状图宽度", 0.5, 0.7, 0.5)
            ytick_size = st.slider("期刊名字号", 10, 25, 24)
            xtick_size = st.slider("CItiation数量字号", 10, 20, 18)
            label_size = st.slider("坐标名字号", 10, 30, 20)
        a = st.button("Plot the Top Sources".title(), use_container_width=True, icon='📈')
    with col4:
        if a:
            fig, ax = plt.subplots(figsize=(24, 8), dpi=300)
            bars = ax.barh(top_citation_edited_df_productive_sources["Sources"],
                           top_citation_edited_df_productive_sources["Citations"],
                           color=color, height=bar_width)
            # 在每个条形图上显示数值
            for bar in bars:
                yval = bar.get_y() + bar.get_height() / 2
                xval = bar.get_width()
                ax.text(xval, yval, int(xval), va='center', fontdict={"fontsize": xtick_size})
            ax.set_xlabel('Citations', fontsize=label_size, labelpad=label_size)
            ax.set_ylabel('SOURCES', fontsize=label_size, labelpad=label_size)
            ax.tick_params(axis='x', labelsize=xtick_size)
            ax.tick_params(axis='y', labelsize=ytick_size)
            if seq == "Descending":
                ax.invert_yaxis()  # 反转y轴，使条形图从上到下排列
            plt.tight_layout()
            st.pyplot(fig, clear_figure=True, use_container_width=True)

def process_Country_Analysis_Tab(df):
    number_of_countries_publication_series = calculate_number_of_countries_publication(df)
    
    # 检查Series是否为空
    if number_of_countries_publication_series.empty:
        st.warning("无法获取国家分析数据，请检查数据中是否包含作者地址信息")
        return
    
    # 将Series转换为DataFrame格式
    countries_documents_list = number_of_countries_publication_series.tolist()
    countries_citiation_list = [0] * len(countries_documents_list)  # 暂时设为0，因为没有引用数据
    
    # 创建DataFrame用于显示
    countries_df = pd.DataFrame({
        'Areas': number_of_countries_publication_series.index,
        'Documents': countries_documents_list,
        'Citations': countries_citiation_list,
        'Average Citation/Publication': [0] * len(countries_documents_list)
    })
    
    st_subheader("Distribution of country information on research areas in this database")
    col1, col2 = st.columns([3,1])
    with col2:
        documents_min_productive_countries = st.number_input(
            "统计高产国家：Documents 需大于等于", min_value=0,
            max_value=int(max(countries_documents_list)) if countries_documents_list else 0, step=1, value=0)
        citiatiosn_min_productive_countries = st.number_input(
            "统计高产国家：Citations 需大于等于", min_value=0,
            max_value=int(max(countries_citiation_list)) if countries_citiation_list else 0, value=0, step=1)
        
        # 过滤数据
        top_citation_edited_df_productive_countries = countries_df[
            (countries_df["Citations"] >= citiatiosn_min_productive_countries) &
            (countries_df['Documents'] >= documents_min_productive_countries)
        ]
        with col1:
            edited_df_productive_countries = st.data_editor(top_citation_edited_df_productive_countries[['Areas','Documents','Citations','Average Citation/Publication']], use_container_width=True,
                                                            height=500)

        countries_list = edited_df_productive_countries["Areas"].to_list()
        drop_countrie_list = st_multiselect('不纳入考虑的国家', options=countries_list, default=None)

        top_citation_edited_df_productive_countries = top_citation_edited_df_productive_countries[(
                                                                                                      top_citation_edited_df_productive_countries[
                                                                                                          "Citations"] >= citiatiosn_min_productive_countries) & (
                                                                                                      top_citation_edited_df_productive_countries[
                                                                                                          'Documents'] >= documents_min_productive_countries)]
        nodrop_source_list = []

        for i in countries_list:
            if i not in drop_countrie_list:
                nodrop_source_list.append(i)
    top_citation_edited_df_productive_countries = top_citation_edited_df_productive_countries[top_citation_edited_df_productive_countries['Areas'].isin(nodrop_source_list)]
    with col2:
        top_citation_edited_df_productive_countries_10 = top_citation_edited_df_productive_countries.sort_values(by='Citations', ascending=False).head(10)
        top_citation_sum=top_citation_edited_df_productive_countries_10["Citations"].sum()
        number_of_total_reference_cited=top_citation_edited_df_productive_countries["Citations"].sum()
        # 避免除零错误
        if number_of_total_reference_cited > 0:
            top_citation_account_for=top_citation_sum/number_of_total_reference_cited*100
        else:
            top_citation_account_for=0
    st_subsubheader('Citations top 10 countries: the most productive countries have %d citations, accounting for %.2f%%' % (top_citation_sum, top_citation_account_for))
    col1, col2 = st.columns([3,1])
    with col1:
        st.dataframe(top_citation_edited_df_productive_countries_10[['Areas','Documents','Citations','Average Citation/Publication']], use_container_width=True,height=450,width=300)
    with col2:
        st.info("📋 国家统计表格展示区域")

    st.markdown("---")
    st.subheader("Visualization of Statistical Results")

    # 创建两列布局
    col1, col2 = st.columns([1, 2])

    # 左侧列：参数设置
    with col1:
        with st.expander("National Mapping - Parameterization", expanded=False, icon="🛠️"):
            # 颜色选择
            color = st.radio(
                label="Choose a color for the country bars:",
                options=["Blue", "Green", "Orange", "Pink"],
                horizontal=True,
                index=0,
                label_visibility="collapsed"
            )

            # 排序方式选择
            seq = st.radio(
                label="Country_Bar Order",
                options=["Ascending", "Descending"],
                index=0,
                horizontal=True,
                label_visibility="collapsed"
            )

            # 滑动条设置
            col4, col5 = st.columns([2, 2])
            with col4:
                bar_width = st.slider("Country_Bar Width", 0.5, 0.7, 0.5)
                ytick_size = st.slider("Country_Font Size", 10, 25, 24)
            with col5:
                xtick_size = st.slider("Country_Citation Font Size", 10, 20, 18)
                label_size = st.slider("Country_Coordinate Name Number", 10, 30, 20)

            # 国家选择
            st.write("Select the country to be mapped".title())
            selected_countries = st.multiselect(
                label="选择需要绘制的国家",
                options=top_citation_edited_df_productive_countries_10,
                default=top_citation_edited_df_productive_countries_10,
                label_visibility="collapsed",
            )
            selected_countries_df = top_citation_edited_df_productive_countries_10[
                top_citation_edited_df_productive_countries_10['Areas'].isin(selected_countries)
            ]
            result = defaultdict(lambda: defaultdict(int))
            years_countries_publication_country =selected_countries_df["Areas"].astype(str)
            for index, country in years_countries_publication_country.items():
                # 安全地获取Years列，如果不存在则使用备用列
                try:
                    # 检查索引是否在DataFrame中
                    if index not in top_citation_edited_df_productive_countries_10.index:
                        years = [2024]
                        continue
                    
                    if 'Years' in top_citation_edited_df_productive_countries_10.columns:
                        years = top_citation_edited_df_productive_countries_10.loc[index, 'Years']
                    elif 'PY' in top_citation_edited_df_productive_countries_10.columns:
                        years = [top_citation_edited_df_productive_countries_10.loc[index, 'PY']]
                    elif '出版年' in top_citation_edited_df_productive_countries_10.columns:
                        years = [top_citation_edited_df_productive_countries_10.loc[index, '出版年']]
                    else:
                        # 如果没有年份信息，使用当前年份
                        years = [2024]
                        st.warning(f"未找到年份信息，使用默认年份 2024")
                    
                    # 确保years是列表格式
                    if not isinstance(years, (list, tuple)):
                        years = [years] if pd.notna(years) else [2024]
                    
                    unique_year = set(years)
                    for year in unique_year:
                        if pd.notna(year):
                            result[country][int(year)] = years.count(year)
                            
                except (KeyError, IndexError) as e:
                    st.warning(f"处理国家 {country} 的年份数据时出错: {str(e)}")
                    # 使用默认年份
                    result[country][2024] = 1

            years_countries_publication_country = pd.DataFrame(result).T.fillna(0).astype(int)

            years_countries_publication_country = years_countries_publication_country.reindex(sorted(years_countries_publication_country.columns), axis=1)
        with col1:
            st_subsubheader('Annual statistics of the number of articles per country/region')

            st.dataframe(years_countries_publication_country, use_container_width=True)

        # 按钮：绘制图表
        a = st.button("Plot the Top Country Histogram", use_container_width=True, icon='📊')
        b = st.button("Plot the Top Countries Annual Production", use_container_width=True, icon='📈')
        st_subsubheader("Analysis of Annual Production by  single Areas")
        selected_country_single= st.selectbox("选择国家/地区", years_countries_publication_country.index,label_visibility="collapsed")
        c=st.button("Plot the Single Country Annual Production", use_container_width=True, icon='📈')

    # 右侧列：图表展示
    with col2:
        if a:
            st.subheader('Citations Top 10 Countries Histogram')
            fig, ax = plt.subplots(figsize=(24, 8), dpi=300)
            bars = ax.barh(selected_countries_df["Areas"], selected_countries_df["Citations"], color=color.lower(), height=bar_width)

            # 在每个条形图上显示数值
            for bar in bars:
                yval = bar.get_y() + bar.get_height() / 2
                xval = bar.get_width()
                ax.text(xval, yval, int(xval), va='center', fontdict={"fontsize": xtick_size})  # va: vertical alignment

            ax.set_xlabel('Citations', fontsize=label_size, labelpad=label_size)
            ax.set_ylabel('Countries', fontsize=label_size, labelpad=label_size)
            ax.tick_params(axis='x', labelsize=xtick_size)
            ax.tick_params(axis='y', labelsize=ytick_size)

            if seq == "Descending":
                ax.invert_yaxis()

            plt.tight_layout()
            st.pyplot(fig, clear_figure=True, use_container_width=True)

        if b:
            st.subheader("Analysis of the number of articles per year by Countries")
            # 数据准备
            result_df =years_countries_publication_country

            # 柱状图
            st.write("#### Bar Chart")
            fig, ax = plt.subplots(figsize=(12, 6))
            result_df.T.plot(kind='bar', ax=ax)
            ax.set_xlabel("Year")
            ax.set_ylabel("Number of Publications")
            ax.set_title("Publications by Country and Year")
            st.pyplot(fig)

            # 堆叠柱状图
            st.write("#### Stacked Bar Chart")
            fig, ax = plt.subplots(figsize=(12, 6))
            result_df.T.plot(kind='bar', stacked=True, ax=ax)
            ax.set_xlabel("Year")
            ax.set_ylabel("Number of Publications")
            ax.set_title("Publications by Country and Year")

            st.pyplot(fig)

            # 折线图
            st.write("#### Line Graph")
            fig, ax = plt.subplots(figsize=(12, 6))
            result_df.T.plot(kind='line', marker='o', ax=ax)
            ax.set_xlabel("Year")
            ax.set_ylabel("Number of Publications")
            ax.set_title("Publications by Country and Year")

            # ax.set_title("Publications by Country and Year (Line Chart)")
            st.pyplot(fig)

            # 图片展示区域
            st.info("🌍 世界地图展示区域 - 可在此处展示国家发文量的地理分布图")
        if c:
            result_df =years_countries_publication_country

            st.write(f"#### {selected_country_single} Percentage of articles per year (pie chart)")
            fig, ax = plt.subplots(figsize=(8, 8))
            result_df.loc[selected_country_single].plot(kind='pie', autopct='%1.1f%%', ax=ax)
            ax.set_ylabel("")
            ax.set_title(f"Publications by Year in {selected_country_single}")
            st.pyplot(fig)


            # 年份文章总数趋势
            st.write("#### The trend of the total number of articles per year")
            yearly_total = result_df.sum(axis=0)
            fig, ax = plt.subplots(figsize=(10, 6))
            yearly_total.plot(kind='line', marker='o', ax=ax)
            ax.set_xlabel("Year")
            ax.set_ylabel("Total Publications")
            ax.set_title("Total Publications by Year")
            st.pyplot(fig)



