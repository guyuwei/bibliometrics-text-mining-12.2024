import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import re
from datetime import datetime
from collections import defaultdict
import itertools
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from PIL.ImageOps import expand
from pandas.io.common import file_exists
import networkx as nx
import numpy as np
from wordcloud import WordCloud
import io
import base64
from scipy import stats
import seaborn as sns
try:
    from streamlit_option_menu import option_menu
except ImportError:
    # 如果导入失败，使用简单的替代方案
    def option_menu(menu_title, options, icons=None, menu_icon=None, default_index=0, orientation="vertical", styles=None):
        return st.selectbox(menu_title, options, index=default_index)
import sys
import os
from Calculate_Anaysis.Calculate_Network import calculate_coupling
try:
    from st_on_hover_tabs import on_hover_tabs
except ImportError:
    # 如果导入失败，使用简单的替代方案
    def on_hover_tabs(tabName, iconName, default_choice=0):
        return st.selectbox("选择页面", tabName, index=default_choice)
from Calculate_Anaysis.Calculate_Author import calculate_core_author_publication,calculate_number_of_authors_publication,process_author_data
from Calculate_Anaysis.Calculate_Country import calculate_collaboration_countries
from Calculate_Anaysis.Calculate_Publication import calculate_publications_per_year
from Calculate_Anaysis.Calculate_Sources import calculate_number_of_sources
from Calculate_Anaysis.Calculate_Keywords import calculate_number_of_keywords
from Calculate_Anaysis.Calculate_Reference import calculate_number_of_total_references_cited,filter_references_by_authors,extract_each_article_author_refauthor
from Calculate_Anaysis.Calculate_Citiation import calculate_number_of_total_Timescitedcount
from Calculate_Anaysis.Calculate_Year import exact_targetarticles_within_yearspan,calculate_age
from Calculate_Anaysis.Calculate_Advanced import AdvancedAnalysis, calculate_advanced_metrics
from Result_Visualization.Descriptive_Statistics import Form_Information_Description,shift_edited_df_into_list
from Result_Visualization.Publications_and_Authors import draw_author_density_visualiaztion,draw_author_overlay_visualiaztion,draw_author_network_visualiaztion
from Result_Visualization.Enhanced_Visualization import EnhancedVisualization, create_dashboard_summary
from Result_Visualization.Plot_Config import get_plot_config
from Documents_Processing.Uploading_Files import Load_TXT,Load_CSV
from Documents_Processing.Export_Functions import DataExporter, export_analysis_data, create_download_link, create_interactive_dashboard_export
from Documents_Processing.Web_Format import st_header, st_subheader, st_selectbox, st_card, st_tags, st_radio, st_button, st_slider, st_checkbox, st_text_area, st_text_input, \
    st_multiselect, st_warning, st_markdown, st_latex, st_table, st_dataframe, st_sidebar_slider, st_file_uploader, st_expander,st_subsubheader,set_page_title_with_image
from Documents_Processing.Web_Process import process_wos_page_upload, process_database_page, process_wos_page_download, process_Overall_Information_Overview_Tab, \
    process_Journay_Analysis_Tab, process_Publication_Author_Tab_Most_Productive, project_root
from Documents_Processing.Tab_Process import process_tabledescribe_tab,process_Publication_Author_Analysis_Tab,process_Publication_Author_Tab_Most_Productive,process_Overall_Information_Overview_Tab,process_Journay_Analysis_Tab,process_Country_Analysis_Tab
from Documents_Processing.Report_Generator import create_report_generator_tab
from Result_Visualization.Network_Visualization import draw_network_visualization,draw_author_network

#————————————————————————————————————————————————————————————path
current_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.dirname(current_dir).replace("/Program","")
library_dir=project_root+ '/library/web_sources/'
picture_path=project_root+ '/output/picture'
csv_path= project_root+'/output/'
audio_file=library_dir+"guita_bgm.mp3"
icon_file_1=library_dir+"奥特曼1.png"
icon_file_2=library_dir+'奥特曼2.png'
icon_file_3=library_dir+'奥特曼3.png'
icon_file_4=library_dir+'奥特曼4.png'
css_file=library_dir+"style.css"
#______________________________________________________________________________________________________________________ 设置页面配置

# 数据加载缓存
@st.cache_data
def load_data(uploaded_file):
    """加载和预处理数据"""
    if uploaded_file is None:
        return None
    
    try:
        if uploaded_file.name.endswith('.txt'):
            df = parse_txt_with_llm(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            df = Load_CSV(uploaded_file)
        elif uploaded_file.name.endswith('.bib'):
            # 使用增强的文件上传器加载BIB文件
            try:
                from Documents_Processing.Enhanced_File_Uploader import load_file_universal
                df = load_file_universal(uploaded_file)
            except ImportError:
                st.error("BIB文件解析功能不可用，请检查模块导入")
                return None
        else:
            st.error("不支持的文件格式，请上传.txt、.csv或.bib文件")
            return None
        
        if df is None or df.empty:
            st.warning("文件解析失败或文件为空")
            return None
        
        # 数据清洗和标准化
        df = clean_and_standardize_data(df)
        return df
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return None

def parse_wos_file(uploaded_file):
    """
    解析Web of Science (WOS) 格式的TXT文件
    WOS文件格式：每行以2-3个字符的字段代码开头，后跟空格和内容
    """
    try:
        # 读取文件内容
        try:
            data = uploaded_file.read().decode("utf-8")
        except UnicodeDecodeError:
            try:
                uploaded_file.seek(0)
                data = uploaded_file.read().decode("utf-8-sig")
            except UnicodeDecodeError:
                try:
                    uploaded_file.seek(0)
                    data = uploaded_file.read().decode("latin-1")
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    data = uploaded_file.read().decode("cp1252")
        
        # 解析WOS格式
        records = []
        current_record = {}
        
        lines = data.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查记录分隔符
            if line == 'ER':
                # 记录结束，保存当前记录
                if current_record:
                    records.append(current_record)
                    current_record = {}
                continue
            elif line == 'EF':
                # 文件结束
                if current_record:
                    records.append(current_record)
                break
            
            # 解析字段 - 只处理标准的WOS字段代码
            if len(line) >= 3 and line[2] == ' ':
                field_code = line[:2]
                field_value = line[3:].strip()
                
                # 只处理有效的WOS字段代码
                valid_fields = {
                    'AU', 'AF', 'TI', 'SO', 'LA', 'DT', 'DE', 'ID', 'AB', 'C1', 'RP', 'EM', 'RI', 
                    'CR', 'NR', 'TC', 'Z9', 'U1', 'U2', 'PU', 'PI', 'PA', 'SN', 'EI', 'J9', 'JI', 
                    'PD', 'PY', 'VL', 'IS', 'BP', 'EP', 'DI', 'PG', 'WC', 'SC', 'GA', 'UT', 'PM', 
                    'DA', 'OA', 'AR', 'FU', 'FX', 'BN', 'BS', 'BA', 'BF', 'BE', 'HO', 'CT', 'CY', 
                    'CL', 'SP', 'SU', 'TA', 'PS', 'PN', 'MA', 'GE', 'UN', 'SE', 'SI', 'CA', 'WE',
                    'VR', 'PT', 'C3', 'OI', 'EA', 'HC', 'HP', 'DB', 'D2', 'PG', 'WC', 'SC', 'GA',
                    'UT', 'PM', 'DA', 'OA', 'AR', 'FU', 'FX', 'BN', 'BS', 'BA', 'BF', 'BE', 'HO',
                    'CT', 'CY', 'CL', 'SP', 'SU', 'TA', 'PS', 'PN', 'MA', 'GE', 'UN', 'SE', 'SI',
                    'CA', 'WE', 'VR', 'PT', 'C3', 'OI', 'EA', 'HC', 'HP', 'DB', 'D2'
                }
                
                if field_code in valid_fields:
                    # 处理多行字段（如作者、地址等）
                    if field_code in current_record:
                        current_record[field_code] += '; ' + field_value
                    else:
                        current_record[field_code] = field_value
        
        if not records:
            st.warning("未找到有效的文献记录")
            return pd.DataFrame()
        
        # 转换为DataFrame
        df = pd.DataFrame(records)
        
        # 显示解析结果
        st.info(f"✅ 成功解析 {len(df)} 条文献记录")
        st.info(f"📋 识别到字段: {', '.join(df.columns.tolist())}")
        
        return df
        
    except Exception as e:
        st.error(f"WOS文件解析失败: {str(e)}")
        return pd.DataFrame()

def parse_txt_with_llm(uploaded_file):
    """使用WOS专用解析函数解析TXT文件"""
    return parse_wos_file(uploaded_file)

def clean_and_standardize_data(df):
    """清洗和标准化数据"""
    # 首先处理重复列名
    if df.columns.duplicated().any():
        # 重命名重复的列
        new_columns = []
        seen_columns = {}
        for col in df.columns:
            if col in seen_columns:
                seen_columns[col] += 1
                new_columns.append(f"{col}_{seen_columns[col]}")
            else:
                seen_columns[col] = 0
                new_columns.append(col)
        df.columns = new_columns
    
    # 标准化列名 - 映射WOS标准字段到分析用列名
    column_mapping = {
        # 核心字段
        'AU': 'Authors', 'AF': 'Authors',  # 作者
        'TI': 'Title',  # 标题
        'SO': 'Source',  # 期刊/来源
        'PY': 'Year',  # 年份
        'AB': 'Abstract',  # 摘要
        'DE': 'Keywords',  # 关键词
        'ID': 'KeywordsPlus',  # 扩展关键词
        'C1': 'Address',  # 地址
        'CR': 'References',  # 参考文献
        'TC': 'TimesCited',  # 被引次数
        'Z9': 'TotalTimesCited',  # 总被引次数
        
        # 期刊信息
        'J9': 'JournalAbbreviation',  # 期刊缩写
        'JI': 'JournalISO',  # ISO期刊缩写
        'VL': 'Volume',  # 卷
        'IS': 'Issue',  # 期
        'BP': 'BeginningPage',  # 起始页
        'EP': 'EndingPage',  # 结束页
        'DI': 'DOI',  # DOI
        'SN': 'ISSN',  # ISSN
        'EI': 'eISSN',  # eISSN
        
        # 作者信息
        'RP': 'ReprintAddress',  # 重印地址
        'EM': 'EmailAddresses',  # 邮箱
        'RI': 'ResearcherID',  # 研究员ID
        'OI': 'ORCID',  # ORCID
        
        # 分类信息
        'WC': 'WebOfScienceCategory',  # WOS分类
        'SC': 'SubjectCategory',  # 学科分类
        'LA': 'Language',  # 语言
        'DT': 'DocumentType',  # 文档类型
        'PT': 'PublicationType',  # 出版类型
        
        # 出版商信息
        'PU': 'Publisher',  # 出版商
        'PI': 'PublisherCity',  # 出版商城市
        'PA': 'PublisherAddress',  # 出版商地址
        
        # 其他信息
        'UT': 'AccessionNumber',  # 入藏号
        'PM': 'PubMedID',  # PubMed ID
        'AR': 'ArticleNumber',  # 文章编号
        'PG': 'PageCount',  # 页数
        'PD': 'PublicationDate',  # 发表日期
        
        # 资助信息
        'FU': 'FundingAgency',  # 资助机构
        'FX': 'FundingText',  # 资助文本
        
        # 使用统计
        'U1': 'UsageCount180',  # 180天使用次数
        'U2': 'UsageCountSince2013',  # 2013年以来使用次数
        
        # 会议信息
        'CT': 'ConferenceTitle',  # 会议标题
        'CY': 'ConferenceDate',  # 会议日期
        'CL': 'ConferenceLocation',  # 会议地点
        'HO': 'ConferenceHost',  # 会议主办方
        
        # 书籍信息
        'BN': 'ISBN',  # ISBN
        'BA': 'BookAuthors',  # 书籍作者
        'BE': 'Editors',  # 编辑
        'TA': 'BookTitle',  # 书籍标题
        
        # 其他
        'DA': 'DateAdded',  # 添加日期
        'OA': 'OpenAccess',  # 开放获取
        'HC': 'HighlyCited',  # 高被引
        'HP': 'HotPaper',  # 热点论文
    }
    
    # 重命名列 - 只重命名存在的列
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df = df.rename(columns={old_col: new_col})
    
    # 合并相同功能的列
    # 合并作者全名到作者列
    if 'AF' in df.columns and 'Authors' in df.columns:
        # 将AF列合并到Authors列
        df['Authors'] = df['Authors'].fillna('') + ';' + df['AF'].fillna('')
        df = df.drop(columns=['AF'])
    elif 'AF' in df.columns:
        df = df.rename(columns={'AF': 'Authors'})
    
    # 处理重复的Authors列
    if df.columns.duplicated().any():
        # 找到重复的Authors列并合并
        authors_cols = [col for col in df.columns if col == 'Authors']
        if len(authors_cols) > 1:
            # 合并所有Authors列
            df['Authors'] = df[authors_cols].apply(lambda x: ';'.join(x.dropna().astype(str)), axis=1)
            # 删除重复的Authors列
            df = df.loc[:, ~df.columns.duplicated()]
    
    # 合并关键词和扩展关键词
    if 'KeywordsPlus' in df.columns and 'Keywords' in df.columns:
        df['Keywords'] = df['Keywords'].fillna('') + ';' + df['KeywordsPlus'].fillna('')
        df = df.drop(columns=['KeywordsPlus'])
    elif 'KeywordsPlus' in df.columns:
        df = df.rename(columns={'KeywordsPlus': 'Keywords'})
    
    # 合并被引次数和总被引次数
    if 'TotalTimesCited' in df.columns and 'TimesCited' in df.columns:
        # 如果TimesCited为空，使用TotalTimesCited
        df['TimesCited'] = df['TimesCited'].fillna(df['TotalTimesCited'])
        df = df.drop(columns=['TotalTimesCited'])
    elif 'TotalTimesCited' in df.columns:
        df = df.rename(columns={'TotalTimesCited': 'TimesCited'})
    
    # 处理年份数据
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df = df.dropna(subset=['Year'])
    
    # 处理引用数据
    if 'TimesCited' in df.columns:
        df['TimesCited'] = pd.to_numeric(df['TimesCited'], errors='coerce').fillna(0)
    
    # 检查必要的列是否存在
    required_columns = ['Authors', 'Source', 'Year']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.warning(f"文件缺少必要字段: {', '.join(missing_columns)}，请检查导出格式")
        # 显示可用的列名供用户参考
        st.info(f"当前可用的列名: {', '.join(df.columns.tolist())}")
    
    return df

def safe_get_column(df, possible_names, default_value=""):
    """安全获取列数据"""
    for name in possible_names:
        if name in df.columns:
            return df[name]
    return pd.Series([default_value] * len(df))

def create_download_button(data, filename, file_type="csv"):
    """创建下载按钮"""
    if file_type == "csv":
        csv = data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">📥 下载 {filename}.csv</a>'
    elif file_type == "png":
        # 对于图表，需要先保存为图片
        return None
    return href

# ==================== 论文分析功能模块 ====================

def analyze_overview_statistics(df):
    """总体信息概览分析"""
    st.subheader("📊 Overall Information Overview")
    
    # 基本统计信息
    total_articles = len(df)
    total_authors = len(set([author for authors in safe_get_column(df, ['Authors']) for author in str(authors).split(';') if author.strip()]))
    total_sources = safe_get_column(df, ['Source']).nunique()
    total_keywords = len(set([kw for keywords in safe_get_column(df, ['Keywords']) for kw in str(keywords).split(';') if kw.strip()]))
    
    # 国际合作比例
    international_collab = 0
    if 'Address' in df.columns:
        addresses = safe_get_column(df, ['Address'])
        for addr in addresses:
            if pd.notna(addr) and len(str(addr).split(';')) > 1:
                countries = set()
                for country_addr in str(addr).split(';'):
                    if '[' in country_addr and ']' in country_addr:
                        country = country_addr.split('[')[-1].split(']')[0].strip()
                        countries.add(country)
                if len(countries) > 1:
                    international_collab += 1
    
    international_ratio = (international_collab / total_articles * 100) if total_articles > 0 else 0
    
    # 平均作者数
    avg_authors = 0
    if 'Authors' in df.columns:
        author_counts = []
        for authors in safe_get_column(df, ['Authors']):
            if pd.notna(authors):
                author_count = len([a for a in str(authors).split(';') if a.strip()])
                author_counts.append(author_count)
        avg_authors = np.mean(author_counts) if author_counts else 0
    
    # 显示统计信息
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Articles", f"{total_articles:,}")
    with col2:
        st.metric("Total Authors", f"{total_authors:,}")
    with col3:
        st.metric("Total Sources", f"{total_sources:,}")
    with col4:
        st.metric("Total Keywords", f"{total_keywords:,}")
    
    col5, col6 = st.columns(2)
    with col5:
        st.metric("International Collaboration", f"{international_ratio:.1f}%")
    with col6:
        st.metric("Average Authors per Article", f"{avg_authors:.1f}")
    
    # 年度发文量折线图
    if 'Year' in df.columns:
        st.subheader("📈 Annual Publication Trends")
        year_counts = df['Year'].value_counts().sort_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=year_counts.index,
            y=year_counts.values,
            mode='lines+markers',
            name='Publications',
            line=dict(color='#B5A8CA', width=3),
            marker=dict(size=8, color='#C0D6EA')
        ))
        
        fig.update_layout(
            title="Annual Publication Trends",
            xaxis_title="Year",
            yaxis_title="Number of Publications",
            template="plotly_white",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 导出按钮
        if st.button("📥 Export Annual Trends Data"):
            csv = year_counts.reset_index()
            csv.columns = ['Year', 'Publications']
            st.download_button(
                label="Download CSV",
                data=csv.to_csv(index=False),
                file_name="annual_trends.csv",
                mime="text/csv"
            )

def analyze_authors(df):
    """作者分析"""
    st.subheader("👥 Author Analysis")
    
    if 'Authors' not in df.columns:
        st.warning("未找到作者信息列")
        return
    
    # 添加筛选选项
    st.markdown("### 🔧 筛选选项")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_publications = st.number_input(
            "最小发表数量", 
            min_value=1, 
            value=1, 
            help="只显示发表数量大于等于此值的作者"
        )
    
    with col2:
        min_citations = st.number_input(
            "最小被引次数", 
            min_value=0, 
            value=0, 
            help="只显示总被引次数大于等于此值的作者"
        )
    
    with col3:
        top_n_authors = st.number_input(
            "显示前N位作者", 
            min_value=5, 
            max_value=50, 
            value=15, 
            help="在图表中显示前N位作者"
        )
    
    # 处理作者数据
    all_authors = []
    for authors in safe_get_column(df, ['Authors']):
        if pd.notna(authors):
            for author in str(authors).split(';'):
                author = author.strip()
                if author:
                    all_authors.append(author)
    
    if not all_authors:
        st.warning("暂无作者数据")
        return
    
    # 作者发文量统计
    author_counts = pd.Series(all_authors).value_counts()
    
    # 应用发表数量筛选
    filtered_author_counts = author_counts[author_counts >= min_publications]
    
    # 普赖斯定律计算核心作者
    total_authors = len(filtered_author_counts)
    price_threshold = 0.749 * np.sqrt(filtered_author_counts.max()) if filtered_author_counts.max() > 0 else 0
    core_authors = filtered_author_counts[filtered_author_counts >= price_threshold]
    
    st.subheader("🔬 Core Authors (Price's Law)")
    st.info(f"普赖斯定律阈值: {price_threshold:.1f} 篇")
    
    # 显示核心作者
    if not core_authors.empty:
        core_df = core_authors.reset_index()
        core_df.columns = ['Author', 'Publications']
        core_df['Rank'] = range(1, len(core_df) + 1)
        
        st.dataframe(core_df, use_container_width=True)
        
        # 导出按钮
        if st.button("📥 Export Core Authors", key="core_authors_export"):
            st.download_button(
                label="Download CSV",
                data=core_df.to_csv(index=False),
                file_name="core_authors.csv",
                mime="text/csv"
            )
    else:
        st.warning("未找到核心作者")
    
    # 高被引作者
    st.subheader(f"⭐ Highly Cited Authors (Top {top_n_authors})")
    if 'TimesCited' in df.columns:
        # 计算每个作者的总被引次数
        author_citations = defaultdict(int)
        for idx, row in df.iterrows():
            if pd.notna(row.get('Authors')) and pd.notna(row.get('TimesCited')):
                citations = int(row['TimesCited']) if str(row['TimesCited']).isdigit() else 0
                for author in str(row['Authors']).split(';'):
                    author = author.strip()
                    if author:
                        author_citations[author] += citations
        
        # 应用被引次数筛选
        filtered_author_citations = {author: citations for author, citations in author_citations.items() 
                                   if citations >= min_citations}
        
        # 排序并显示前N位
        top_cited = sorted(filtered_author_citations.items(), key=lambda x: x[1], reverse=True)[:top_n_authors]
        if top_cited:
            cited_df = pd.DataFrame(top_cited, columns=['Author', 'Total Citations'])
            cited_df['Rank'] = range(1, len(cited_df) + 1)
            
            st.dataframe(cited_df, use_container_width=True)
            
            # 导出按钮
            if st.button("📥 Export Highly Cited Authors", key="cited_authors_export"):
                st.download_button(
                    label="Download CSV",
                    data=cited_df.to_csv(index=False),
                    file_name="highly_cited_authors.csv",
                    mime="text/csv"
                )
    else:
        st.warning("未找到引用数据，请检查TimesCited列是否存在")
    
    # 作者合作网络图
    st.subheader("🕸️ Author Collaboration Network")
    if len(all_authors) > 1:
        # 创建合作网络
        G = nx.Graph()
        
        # 只添加满足筛选条件的作者作为节点
        filtered_authors = set([author for author in all_authors 
                               if author_counts.get(author, 0) >= min_publications])
        
        if len(filtered_authors) < 2:
            st.warning(f"满足筛选条件的作者数量不足（需要至少2位，当前{len(filtered_authors)}位），无法绘制合作网络图")
            return
        
        # 添加节点
        for author in filtered_authors:
            G.add_node(author)
        
        # 添加边（同一篇文章的作者之间建立连接）
        for authors in safe_get_column(df, ['Authors']):
            if pd.notna(authors):
                author_list = [a.strip() for a in str(authors).split(';') if a.strip()]
                for i in range(len(author_list)):
                    for j in range(i+1, len(author_list)):
                        if G.has_edge(author_list[i], author_list[j]):
                            G[author_list[i]][author_list[j]]['weight'] += 1
                        else:
                            G.add_edge(author_list[i], author_list[j], weight=1)
        
        if G.number_of_edges() > 0:
            # 使用spring布局
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            # 创建网络图
            edge_trace = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                weight = G[edge[0]][edge[1]]['weight']
                edge_trace.append(go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=weight*0.5, color='#888'),
                    hoverinfo='none'
                ))
            
            # 节点大小基于发文量
            node_sizes = [author_counts[node] * 10 for node in G.nodes()]
            
            node_trace = go.Scatter(
                x=[pos[node][0] for node in G.nodes()],
                y=[pos[node][1] for node in G.nodes()],
                mode='markers+text',
                text=[node[:15] + '...' if len(node) > 15 else node for node in G.nodes()],
                textposition="middle center",
                hoverinfo='text',
                marker=dict(
                    size=node_sizes,
                    color='#B5A8CA',
                    line=dict(width=2, color='#C0D6EA')
                )
            )
            
            fig = go.Figure(data=edge_trace + [node_trace])
            fig.update_layout(
                title="Author Collaboration Network",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("作者合作网络数据不足")
    
    # 被引耦合网络图
    st.subheader("🔗 Citation Coupling Network")
    if 'References' in df.columns and len(all_authors) > 1:
        # 创建被引耦合网络
        G_coupling = nx.Graph()
        
        # 为每个作者收集其引用的文献
        author_refs = defaultdict(set)
        for idx, row in df.iterrows():
            if pd.notna(row.get('Authors')) and pd.notna(row.get('References')):
                for author in str(row['Authors']).split(';'):
                    author = author.strip()
                    if author:
                        for ref in str(row['References']).split(';'):
                            ref = ref.strip()
                            if ref:
                                author_refs[author].add(ref)
        
        # 计算作者间的引用耦合强度
        authors_list = list(author_refs.keys())
        for i in range(len(authors_list)):
            for j in range(i+1, len(authors_list)):
                author1, author2 = authors_list[i], authors_list[j]
                refs1, refs2 = author_refs[author1], author_refs[author2]
                
                # 计算共同引用的文献数量
                common_refs = len(refs1.intersection(refs2))
                if common_refs > 0:
                    G_coupling.add_edge(author1, author2, weight=common_refs)
        
        if G_coupling.number_of_edges() > 0:
            # 使用spring布局
            pos = nx.spring_layout(G_coupling, k=1, iterations=50)
            
            # 创建网络图
            edge_trace = []
            for edge in G_coupling.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                weight = G_coupling[edge[0]][edge[1]]['weight']
                edge_trace.append(go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=weight*0.3, color='#FF6B6B'),
                    hoverinfo='none'
                ))
            
            node_trace = go.Scatter(
                x=[pos[node][0] for node in G_coupling.nodes()],
                y=[pos[node][1] for node in G_coupling.nodes()],
                mode='markers+text',
                text=[node[:15] + '...' if len(node) > 15 else node for node in G_coupling.nodes()],
                textposition="middle center",
                hoverinfo='text',
                marker=dict(
                    size=20,
                    color='#FF6B6B',
                    line=dict(width=2, color='#FF8E8E')
                )
            )
            
            fig = go.Figure(data=edge_trace + [node_trace])
            fig.update_layout(
                title="Citation Coupling Network",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("被引耦合网络数据不足")
    else:
        st.warning("需要参考文献数据来构建被引耦合网络")

def analyze_countries(df):
    """国家与地区分析"""
    st.subheader("🌍 Country and Region Analysis")
    
    if 'Address' not in df.columns:
        st.warning("未找到地址信息列")
        return
    
    # 添加筛选选项
    st.markdown("### 🔧 筛选选项")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_publications_country = st.number_input(
            "最小发文数量", 
            min_value=1, 
            value=1, 
            help="只显示发文数量大于等于此值的国家",
            key="country_min_pub"
        )
    
    with col2:
        min_citations_country = st.number_input(
            "最小被引次数", 
            min_value=0, 
            value=0, 
            help="只显示总被引次数大于等于此值的国家",
            key="country_min_cit"
        )
    
    with col3:
        top_n_countries = st.number_input(
            "显示前N个国家", 
            min_value=5, 
            max_value=30, 
            value=10, 
            help="在图表中显示前N个国家",
            key="country_top_n"
        )
    
    # 提取国家信息
    countries = []
    for addr in safe_get_column(df, ['Address']):
        if pd.notna(addr):
            for country_addr in str(addr).split(';'):
                if '[' in country_addr and ']' in country_addr:
                    country = country_addr.split('[')[-1].split(']')[0].strip()
                    if country:
                        countries.append(country)
    
    if not countries:
        st.warning("未找到国家信息")
        return
    
    # 国家发文量统计
    country_counts = pd.Series(countries).value_counts()
    
    # 国家引用量统计
    country_citations = defaultdict(int)
    for idx, row in df.iterrows():
        if pd.notna(row.get('Address')) and pd.notna(row.get('TimesCited')):
            citations = int(row['TimesCited']) if str(row['TimesCited']).isdigit() else 0
            for country_addr in str(row['Address']).split(';'):
                if '[' in country_addr and ']' in country_addr:
                    country = country_addr.split('[')[-1].split(']')[0].strip()
                    if country:
                        country_citations[country] += citations
    
    # 应用筛选条件
    filtered_countries = []
    for country in country_counts.index:
        pub_count = country_counts[country]
        cit_count = country_citations.get(country, 0)
        if pub_count >= min_publications_country and cit_count >= min_citations_country:
            filtered_countries.append(country)
    
    if not filtered_countries:
        st.warning(f"没有国家满足筛选条件（发文数量≥{min_publications_country}，被引次数≥{min_citations_country}）")
        return
    
    # 显示国家统计表格
    st.subheader("📊 Country Statistics")
    filtered_country_counts = country_counts[filtered_countries]
    country_stats = pd.DataFrame({
        'Country': filtered_country_counts.index,
        'Publications': filtered_country_counts.values,
        'Citations': [country_citations.get(country, 0) for country in filtered_country_counts.index]
    })
    country_stats['Citations per Paper'] = country_stats['Citations'] / country_stats['Publications']
    country_stats = country_stats.sort_values('Publications', ascending=False)
    country_stats['Rank'] = range(1, len(country_stats) + 1)
    
    st.dataframe(country_stats.head(top_n_countries), use_container_width=True)
    
    # 导出按钮
    if st.button("📥 Export Country Statistics", key="country_stats_export"):
        st.download_button(
            label="Download CSV",
            data=country_stats.to_csv(index=False),
            file_name="country_statistics.csv",
            mime="text/csv"
        )
    
    # 国家合作地图
    st.subheader("🗺️ Country Collaboration Map")
    if len(filtered_countries) > 1:
        # 创建国家合作网络
        G_country = nx.Graph()
        
        # 只添加满足筛选条件的国家作为节点
        for country in filtered_countries:
            G_country.add_node(country)
        
        # 添加边（同一篇文章的国家之间建立连接）
        for addr in safe_get_column(df, ['Address']):
            if pd.notna(addr):
                country_list = []
                for country_addr in str(addr).split(';'):
                    if '[' in country_addr and ']' in country_addr:
                        country = country_addr.split('[')[-1].split(']')[0].strip()
                        if country:
                            country_list.append(country)
                
                for i in range(len(country_list)):
                    for j in range(i+1, len(country_list)):
                        if G_country.has_edge(country_list[i], country_list[j]):
                            G_country[country_list[i]][country_list[j]]['weight'] += 1
                        else:
                            G_country.add_edge(country_list[i], country_list[j], weight=1)
        
        if G_country.number_of_edges() > 0:
            # 使用spring布局
            pos = nx.spring_layout(G_country, k=1, iterations=50)
            
            # 创建网络图
            edge_trace = []
            for edge in G_country.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                weight = G_country[edge[0]][edge[1]]['weight']
                edge_trace.append(go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=weight*0.5, color='#4ECDC4'),
                    hoverinfo='none'
                ))
            
            # 节点大小基于发文量
            node_sizes = [country_counts[node] * 15 for node in G_country.nodes()]
            
            node_trace = go.Scatter(
                x=[pos[node][0] for node in G_country.nodes()],
                y=[pos[node][1] for node in G_country.nodes()],
                mode='markers+text',
                text=list(G_country.nodes()),
                textposition="middle center",
                hoverinfo='text',
                marker=dict(
                    size=node_sizes,
                    color='#4ECDC4',
                    line=dict(width=2, color='#45B7D1')
                )
            )
            
            fig = go.Figure(data=edge_trace + [node_trace])
            fig.update_layout(
                title="Country Collaboration Network",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("国家合作网络数据不足")
    
    # 年度发文趋势（主要国家）
    st.subheader("📈 Annual Publication Trends by Country")
    if 'Year' in df.columns:
        # 选择发文量前5的国家
        top_countries = country_counts.head(5).index.tolist()
        
        # 按年份和国家统计
        yearly_country_data = defaultdict(lambda: defaultdict(int))
        for idx, row in df.iterrows():
            if pd.notna(row.get('Year')) and pd.notna(row.get('Address')):
                year = int(row['Year'])
                for country_addr in str(row['Address']).split(';'):
                    if '[' in country_addr and ']' in country_addr:
                        country = country_addr.split('[')[-1].split(']')[0].strip()
                        if country in top_countries:
                            yearly_country_data[year][country] += 1
        
        # 创建折线图
        fig = go.Figure()
        colors = ['#B5A8CA', '#C0D6EA', '#E0BBD0', '#FF6B6B', '#4ECDC4']
        
        for i, country in enumerate(top_countries):
            years = sorted(yearly_country_data.keys())
            counts = [yearly_country_data[year].get(country, 0) for year in years]
            
            fig.add_trace(go.Scatter(
                x=years,
                y=counts,
                mode='lines+markers',
                name=country,
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title="Annual Publication Trends by Top Countries",
            xaxis_title="Year",
            yaxis_title="Number of Publications",
            template="plotly_white",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 导出按钮
        if st.button("📥 Export Country Trends", key="country_trends_export"):
            # 准备导出数据
            export_data = []
            for country in top_countries:
                years = sorted(yearly_country_data.keys())
                for year in years:
                    count = yearly_country_data[year].get(country, 0)
                    export_data.append({'Country': country, 'Year': year, 'Publications': count})
            
            export_df = pd.DataFrame(export_data)
            st.download_button(
                label="Download CSV",
                data=export_df.to_csv(index=False),
                file_name="country_trends.csv",
                mime="text/csv"
            )

def analyze_institutions(df):
    """机构分析"""
    st.subheader("🏛️ Institution Analysis")
    
    if 'Address' not in df.columns:
        st.warning("未找到地址信息列")
        return
    
    # 添加筛选选项
    st.markdown("### 🔧 筛选选项")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_publications_institution = st.number_input(
            "最小发文数量", 
            min_value=1, 
            value=1, 
            help="只显示发文数量大于等于此值的机构",
            key="institution_min_pub"
        )
    
    with col2:
        min_citations_institution = st.number_input(
            "最小被引次数", 
            min_value=0, 
            value=0, 
            help="只显示总被引次数大于等于此值的机构",
            key="institution_min_cit"
        )
    
    with col3:
        top_n_institutions = st.number_input(
            "显示前N个机构", 
            min_value=5, 
            max_value=30, 
            value=10, 
            help="在图表中显示前N个机构",
            key="institution_top_n"
        )
    
    # 提取机构信息
    institutions = []
    for addr in safe_get_column(df, ['Address']):
        if pd.notna(addr):
            for institution_addr in str(addr).split(';'):
                # 提取机构名称（在方括号前）
                if '[' in institution_addr:
                    institution = institution_addr.split('[')[0].strip()
                    if institution:
                        institutions.append(institution)
    
    if not institutions:
        st.warning("未找到机构信息")
        return
    
    # 机构发文量统计
    institution_counts = pd.Series(institutions).value_counts()
    
    # 机构引用量统计
    institution_citations = defaultdict(int)
    for idx, row in df.iterrows():
        if pd.notna(row.get('Address')) and pd.notna(row.get('TimesCited')):
            citations = int(row['TimesCited']) if str(row['TimesCited']).isdigit() else 0
            for institution_addr in str(row['Address']).split(';'):
                if '[' in institution_addr:
                    institution = institution_addr.split('[')[0].strip()
                    if institution:
                        institution_citations[institution] += citations
    
    # 应用筛选条件
    filtered_institutions = []
    for institution in institution_counts.index:
        pub_count = institution_counts[institution]
        cit_count = institution_citations.get(institution, 0)
        if pub_count >= min_publications_institution and cit_count >= min_citations_institution:
            filtered_institutions.append(institution)
    
    if not filtered_institutions:
        st.warning(f"没有机构满足筛选条件（发文数量≥{min_publications_institution}，被引次数≥{min_citations_institution}）")
        return
    
    # 显示机构统计表格
    st.subheader("📊 Top Institutions by Publications")
    filtered_institution_counts = institution_counts[filtered_institutions]
    institution_stats = pd.DataFrame({
        'Institution': filtered_institution_counts.index,
        'Publications': filtered_institution_counts.values,
        'Citations': [institution_citations.get(institution, 0) for institution in filtered_institution_counts.index]
    })
    institution_stats['Citations per Paper'] = institution_stats['Citations'] / institution_stats['Publications']
    institution_stats = institution_stats.sort_values('Publications', ascending=False)
    institution_stats['Rank'] = range(1, len(institution_stats) + 1)
    
    st.dataframe(institution_stats.head(top_n_institutions), use_container_width=True)
    
    # 导出按钮
    if st.button("📥 Export Institution Statistics", key="institution_stats_export"):
        st.download_button(
            label="Download CSV",
            data=institution_stats.to_csv(index=False),
            file_name="institution_statistics.csv",
            mime="text/csv"
        )
    
    # 机构合作网络图
    st.subheader("🕸️ Institution Collaboration Network")
    if len(filtered_institutions) > 1:
        # 创建机构合作网络
        G = nx.Graph()
        
        # 只添加满足筛选条件的机构作为节点
        for institution in filtered_institutions:
            G.add_node(institution)
        
        # 添加边（同一篇文章的机构之间建立连接）
        for addr in safe_get_column(df, ['Address']):
            if pd.notna(addr):
                institution_list = []
                for institution_addr in str(addr).split(';'):
                    if '[' in institution_addr:
                        institution = institution_addr.split('[')[0].strip()
                        if institution:
                            institution_list.append(institution)
                
                for i in range(len(institution_list)):
                    for j in range(i+1, len(institution_list)):
                        if G.has_edge(institution_list[i], institution_list[j]):
                            G[institution_list[i]][institution_list[j]]['weight'] += 1
                        else:
                            G.add_edge(institution_list[i], institution_list[j], weight=1)
        
        if G.number_of_edges() > 0:
            # 使用spring布局
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            # 创建网络图
            edge_trace = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                weight = G[edge[0]][edge[1]]['weight']
                edge_trace.append(go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=weight*0.3, color='#888'),
                    hoverinfo='none'
                ))
            
            # 节点大小基于发文量
            node_sizes = [institution_counts[node] * 10 for node in G.nodes()]
            
            node_trace = go.Scatter(
                x=[pos[node][0] for node in G.nodes()],
                y=[pos[node][1] for node in G.nodes()],
                mode='markers+text',
                text=[node[:20] + '...' if len(node) > 20 else node for node in G.nodes()],
                textposition="middle center",
                hoverinfo='text',
                marker=dict(
                    size=node_sizes,
                    color='#B5A8CA',
                    line=dict(width=2, color='#C0D6EA')
                )
            )
            
            fig = go.Figure(data=edge_trace + [node_trace])
            fig.update_layout(
                title="Institution Collaboration Network",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("机构合作网络数据不足")
    
    # 年度产出变化
    st.subheader("📈 Annual Output Changes by Institution")
    if 'Year' in df.columns:
        # 选择发文量前10的机构
        top_institutions = institution_counts.head(10).index.tolist()
        
        # 按年份和机构统计
        yearly_institution_data = defaultdict(lambda: defaultdict(int))
        for idx, row in df.iterrows():
            if pd.notna(row.get('Year')) and pd.notna(row.get('Address')):
                year = int(row['Year'])
                for institution_addr in str(row['Address']).split(';'):
                    if '[' in institution_addr:
                        institution = institution_addr.split('[')[0].strip()
                        if institution in top_institutions:
                            yearly_institution_data[year][institution] += 1
        
        # 创建折线图
        fig = go.Figure()
        colors = ['#B5A8CA', '#C0D6EA', '#E0BBD0', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#A8E6CF', '#FFD3A5']
        
        for i, institution in enumerate(top_institutions):
            years = sorted(yearly_institution_data.keys())
            counts = [yearly_institution_data[year].get(institution, 0) for year in years]
            
            fig.add_trace(go.Scatter(
                x=years,
                y=counts,
                mode='lines+markers',
                name=institution[:30] + '...' if len(institution) > 30 else institution,
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title="Annual Output Changes by Top Institutions",
            xaxis_title="Year",
            yaxis_title="Number of Publications",
            template="plotly_white",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 导出按钮
        if st.button("📥 Export Institution Trends", key="institution_trends_export"):
            # 准备导出数据
            export_data = []
            for institution in top_institutions:
                years = sorted(yearly_institution_data.keys())
                for year in years:
                    count = yearly_institution_data[year].get(institution, 0)
                    export_data.append({'Institution': institution, 'Year': year, 'Publications': count})
            
            export_df = pd.DataFrame(export_data)
            st.download_button(
                label="Download CSV",
                data=export_df.to_csv(index=False),
                file_name="institution_trends.csv",
                mime="text/csv"
            )

def analyze_cited_references(df):
    """被引文献分析"""
    st.subheader("📚 Cited References Analysis")
    
    if 'References' not in df.columns:
        st.warning("未找到参考文献列")
        return
    
    # 统计被引文献
    all_refs = []
    for refs in safe_get_column(df, ['References']):
        if pd.notna(refs):
            for ref in str(refs).split(';'):
                ref = ref.strip()
                if ref:
                    all_refs.append(ref)
    
    if not all_refs:
        st.warning("暂无参考文献数据")
        return
    
    # 被引文献统计
    ref_counts = pd.Series(all_refs).value_counts()
    
    # 显示高被引文献表格
    st.subheader("⭐ Highly Cited References")
    ref_stats = pd.DataFrame({
        'Reference': ref_counts.index,
        'Citation Count': ref_counts.values
    })
    ref_stats['Rank'] = range(1, len(ref_stats) + 1)
    
    st.dataframe(ref_stats.head(20), use_container_width=True)
    
    # 导出按钮
    if st.button("📥 Export Cited References", key="cited_refs_export"):
        st.download_button(
            label="Download CSV",
            data=ref_stats.to_csv(index=False),
            file_name="cited_references.csv",
            mime="text/csv"
        )
    
    # 共被引网络图
    st.subheader("🕸️ Co-citation Network")
    if len(all_refs) > 1:
        # 选择高频被引文献
        top_refs = ref_counts.head(30).index.tolist()
        
        # 创建共被引网络
        G_cocitation = nx.Graph()
        
        # 添加节点
        for ref in top_refs:
            G_cocitation.add_node(ref)
        
        # 添加边（同一篇文章引用的文献之间建立连接）
        for refs in safe_get_column(df, ['References']):
            if pd.notna(refs):
                ref_list = []
                for ref in str(refs).split(';'):
                    ref = ref.strip()
                    if ref in top_refs:
                        ref_list.append(ref)
                
                for i in range(len(ref_list)):
                    for j in range(i+1, len(ref_list)):
                        if G_cocitation.has_edge(ref_list[i], ref_list[j]):
                            G_cocitation[ref_list[i]][ref_list[j]]['weight'] += 1
                        else:
                            G_cocitation.add_edge(ref_list[i], ref_list[j], weight=1)
        
        if G_cocitation.number_of_edges() > 0:
            # 使用spring布局
            pos = nx.spring_layout(G_cocitation, k=1, iterations=50)
            
            # 创建网络图
            edge_trace = []
            for edge in G_cocitation.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                weight = G_cocitation[edge[0]][edge[1]]['weight']
                edge_trace.append(go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=weight*0.3, color='#E0BBD0'),
                    hoverinfo='none'
                ))
            
            # 节点大小基于被引次数
            node_sizes = [ref_counts[node] * 5 for node in G_cocitation.nodes()]
            
            node_trace = go.Scatter(
                x=[pos[node][0] for node in G_cocitation.nodes()],
                y=[pos[node][1] for node in G_cocitation.nodes()],
                mode='markers+text',
                text=[node[:30] + '...' if len(node) > 30 else node for node in G_cocitation.nodes()],
                textposition="middle center",
                hoverinfo='text',
                marker=dict(
                    size=node_sizes,
                    color='#E0BBD0',
                    line=dict(width=2, color='#FFB6C1')
                )
            )
            
            fig = go.Figure(data=edge_trace + [node_trace])
            fig.update_layout(
                title="Co-citation Network",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("共被引网络数据不足")

def analyze_keywords(df):
    """关键词共现分析"""
    st.subheader("🔑 Keywords Co-occurrence Analysis")
    
    if 'Keywords' not in df.columns:
        st.warning("未找到关键词列")
        return
    
    # 添加筛选选项
    st.markdown("### 🔧 筛选选项")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_keyword_frequency = st.number_input(
            "最小关键词频次", 
            min_value=1, 
            value=2, 
            help="只显示出现频次大于等于此值的关键词",
            key="keyword_min_freq"
        )
    
    with col2:
        min_cooccurrence = st.number_input(
            "最小共现次数", 
            min_value=1, 
            value=1, 
            help="只显示共现次数大于等于此值的关键词对",
            key="keyword_min_cooc"
        )
    
    with col3:
        top_n_keywords = st.number_input(
            "显示前N个关键词", 
            min_value=10, 
            max_value=100, 
            value=30, 
            help="在图表中显示前N个关键词",
            key="keyword_top_n"
        )
    
    # 提取关键词
    all_keywords = []
    for keywords in safe_get_column(df, ['Keywords']):
        if pd.notna(keywords):
            for kw in str(keywords).split(';'):
                kw = kw.strip().lower()
                if kw and len(kw) > 2:  # 过滤太短的关键词
                    all_keywords.append(kw)
    
    if not all_keywords:
        st.warning("暂无关键词数据")
        return
    
    # 关键词频率统计
    kw_counts = pd.Series(all_keywords).value_counts()
    
    # 应用频次筛选
    filtered_kw_counts = kw_counts[kw_counts >= min_keyword_frequency]
    
    if filtered_kw_counts.empty:
        st.warning(f"没有关键词满足频次筛选条件（≥{min_keyword_frequency}次）")
        return
    
    # 显示热点关键词表格
    st.subheader("🔥 Hot Keywords Frequency")
    kw_stats = pd.DataFrame({
        'Keyword': filtered_kw_counts.index,
        'Frequency': filtered_kw_counts.values
    })
    kw_stats = kw_stats.sort_values('Frequency', ascending=False)
    kw_stats['Rank'] = range(1, len(kw_stats) + 1)
    
    st.dataframe(kw_stats.head(top_n_keywords), use_container_width=True)
    
    # 导出按钮
    if st.button("📥 Export Keywords", key="keywords_export"):
        st.download_button(
            label="Download CSV",
            data=kw_stats.to_csv(index=False),
            file_name="keywords_frequency.csv",
            mime="text/csv"
        )
    
    # 关键词共现网络图
    st.subheader("🕸️ Keywords Co-occurrence Network")
    if len(filtered_kw_counts) > 1:
        # 选择高频关键词
        top_keywords = filtered_kw_counts.head(top_n_keywords).index.tolist()
        
        # 创建共现网络
        G = nx.Graph()
        
        # 添加节点
        for kw in top_keywords:
            G.add_node(kw)
        
        # 添加边（同一篇文章的关键词之间建立连接）
        for keywords in safe_get_column(df, ['Keywords']):
            if pd.notna(keywords):
                kw_list = []
                for kw in str(keywords).split(';'):
                    kw = kw.strip().lower()
                    if kw in top_keywords:
                        kw_list.append(kw)
                
                for i in range(len(kw_list)):
                    for j in range(i+1, len(kw_list)):
                        if G.has_edge(kw_list[i], kw_list[j]):
                            G[kw_list[i]][kw_list[j]]['weight'] += 1
                        else:
                            G.add_edge(kw_list[i], kw_list[j], weight=1)
        
        # 应用共现次数筛选
        edges_to_remove = []
        for edge in G.edges():
            if G[edge[0]][edge[1]]['weight'] < min_cooccurrence:
                edges_to_remove.append(edge)
        
        for edge in edges_to_remove:
            G.remove_edge(edge[0], edge[1])
        
        if G.number_of_edges() > 0:
            # 使用spring布局
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            # 创建网络图
            edge_trace = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                weight = G[edge[0]][edge[1]]['weight']
                edge_trace.append(go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=weight*0.5, color='#888'),
                    hoverinfo='none'
                ))
            
            # 节点大小基于频率
            node_sizes = [filtered_kw_counts[node] * 10 for node in G.nodes()]
            
            node_trace = go.Scatter(
                x=[pos[node][0] for node in G.nodes()],
                y=[pos[node][1] for node in G.nodes()],
                mode='markers+text',
                text=list(G.nodes()),
                textposition="middle center",
                hoverinfo='text',
                marker=dict(
                    size=node_sizes,
                    color='#B5A8CA',
                    line=dict(width=2, color='#C0D6EA')
                )
            )
            
            fig = go.Figure(data=edge_trace + [node_trace])
            fig.update_layout(
                title="Keywords Co-occurrence Network",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("关键词共现网络数据不足")

def analyze_trends(df):
    """研究趋势与热点分析"""
    st.subheader("📈 Research Trends and Hot Topics Analysis")
    
    if 'Year' not in df.columns or 'Keywords' not in df.columns:
        st.warning("需要年份和关键词数据进行分析")
        return
    
    # 按年份分析关键词趋势
    yearly_keywords = defaultdict(list)
    for idx, row in df.iterrows():
        if pd.notna(row.get('Year')) and pd.notna(row.get('Keywords')):
            year = int(row['Year'])
            for kw in str(row['Keywords']).split(';'):
                kw = kw.strip().lower()
                if kw and len(kw) > 2:
                    yearly_keywords[year].append(kw)
    
    if not yearly_keywords:
        st.warning("暂无趋势数据")
        return
    
    # 计算每个关键词的年度频率
    kw_yearly_freq = defaultdict(lambda: defaultdict(int))
    for year, keywords in yearly_keywords.items():
        for kw in keywords:
            kw_yearly_freq[kw][year] += 1
    
    # 选择高频关键词进行趋势分析
    all_keywords = []
    for keywords in yearly_keywords.values():
        all_keywords.extend(keywords)
    
    kw_counts = pd.Series(all_keywords).value_counts()
    top_keywords = kw_counts.head(10).index.tolist()
    
    # 创建趋势图
    st.subheader("📊 Keyword Trends Over Time")
    fig = go.Figure()
    colors = ['#B5A8CA', '#C0D6EA', '#E0BBD0', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#A8E6CF', '#FFD3A5']
    
    for i, kw in enumerate(top_keywords):
        years = sorted(kw_yearly_freq[kw].keys())
        freqs = [kw_yearly_freq[kw][year] for year in years]
        
        fig.add_trace(go.Scatter(
            x=years,
            y=freqs,
            mode='lines+markers',
            name=kw,
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title="Top Keywords Trends Over Time",
        xaxis_title="Year",
        yaxis_title="Frequency",
        template="plotly_white",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 突现词分析（简化版）
    st.subheader("🚀 Burst Keywords Analysis")
    
    # 计算关键词的突现强度（简化版）
    burst_keywords = []
    for kw in top_keywords:
        years = sorted(kw_yearly_freq[kw].keys())
        if len(years) >= 3:
            # 计算增长趋势
            freqs = [kw_yearly_freq[kw][year] for year in years]
            if len(freqs) >= 3:
                # 计算最近几年的平均频率与早期几年的平均频率的比值
                early_avg = np.mean(freqs[:len(freqs)//2])
                recent_avg = np.mean(freqs[len(freqs)//2:])
                if early_avg > 0:
                    burst_strength = recent_avg / early_avg
                    if burst_strength > 1.5:  # 突现强度阈值
                        burst_keywords.append({
                            'Keyword': kw,
                            'Burst Strength': burst_strength,
                            'Early Avg': early_avg,
                            'Recent Avg': recent_avg
                        })
    
    if burst_keywords:
        burst_df = pd.DataFrame(burst_keywords)
        burst_df = burst_df.sort_values('Burst Strength', ascending=False)
        burst_df['Rank'] = range(1, len(burst_df) + 1)
        
        st.dataframe(burst_df, use_container_width=True)
        
        # 导出按钮
        if st.button("📥 Export Burst Keywords", key="burst_keywords_export"):
            st.download_button(
                label="Download CSV",
                data=burst_df.to_csv(index=False),
                file_name="burst_keywords.csv",
                mime="text/csv"
            )
    else:
        st.warning("未发现明显的突现关键词")
    
    # 主题演化趋势
    st.subheader("📊 Topic Evolution Trends")
    if len(yearly_keywords) > 0:
        # 按时间段分析主题演化
        all_years = sorted(yearly_keywords.keys())
        if len(all_years) >= 4:
            # 将年份分为几个时间段
            time_periods = []
            period_size = len(all_years) // 3
            for i in range(0, len(all_years), period_size):
                period_years = all_years[i:i+period_size]
                if period_years:
                    time_periods.append(period_years)
            
            # 分析每个时间段的热门关键词
            period_topics = {}
            for i, period in enumerate(time_periods):
                period_keywords = []
                for year in period:
                    period_keywords.extend(yearly_keywords[year])
                
                if period_keywords:
                    period_kw_counts = pd.Series(period_keywords).value_counts()
                    period_topics[f"Period {i+1} ({min(period)}-{max(period)})"] = period_kw_counts.head(5)
            
            # 创建主题演化表格
            if period_topics:
                st.subheader("📈 Topic Evolution by Time Periods")
                
                # 创建演化数据表格
                evolution_data = []
                for period, topics in period_topics.items():
                    for rank, (topic, freq) in enumerate(topics.items(), 1):
                        evolution_data.append({
                            'Time Period': period,
                            'Rank': rank,
                            'Topic': topic,
                            'Frequency': freq
                        })
                
                evolution_df = pd.DataFrame(evolution_data)
                st.dataframe(evolution_df, use_container_width=True)
                
                # 导出按钮
                if st.button("📥 Export Topic Evolution", key="topic_evolution_export"):
                    st.download_button(
                        label="Download CSV",
                        data=evolution_df.to_csv(index=False),
                        file_name="topic_evolution.csv",
                        mime="text/csv"
                    )
                
                # 创建主题演化可视化
                st.subheader("📊 Topic Evolution Visualization")
                fig = go.Figure()
                
                # 为每个时间段创建柱状图
                for i, (period, topics) in enumerate(period_topics.items()):
                    fig.add_trace(go.Bar(
                        name=period,
                        x=list(topics.index),
                        y=list(topics.values),
                        text=list(topics.values),
                        textposition='auto',
                    ))
                
                fig.update_layout(
                    title="Topic Evolution Across Time Periods",
                    xaxis_title="Keywords",
                    yaxis_title="Frequency",
                    barmode='group',
                    template="plotly_white",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("无法分析主题演化趋势")
        else:
            st.warning("数据时间跨度不足，无法进行主题演化分析")
    else:
        st.warning("暂无主题演化数据")

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
                st.info(f"🎉{df_name} 成果保存至：{ file_name } 文件！")
                st.snow()

st.set_page_config(
    page_title="King of the Universe",
    layout="wide",
    page_icon="🐰",
)


# 奈克赛斯奥特曼开场动画
def show_ultraman_intro():
    """显示奈克赛斯奥特曼开场动画"""
    import streamlit.components.v1 as components
    
    intro_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body, html {
                margin: 0;
                padding: 0;
                overflow: hidden;
                background: linear-gradient(135deg, #000428 0%, #004e92 100%);
            }
            .ultraman-intro {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, #000428 0%, #004e92 100%);
                z-index: 9999;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                overflow: hidden;
            }
            .stars {
                position: absolute;
                width: 100%;
                height: 100%;
                background-image: 
                    radial-gradient(2px 2px at 20px 30px, #eee, transparent),
                    radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.8), transparent),
                    radial-gradient(1px 1px at 90px 40px, #fff, transparent),
                    radial-gradient(1px 1px at 130px 80px, rgba(255,255,255,0.6), transparent),
                    radial-gradient(2px 2px at 160px 30px, #fff, transparent);
                background-repeat: repeat;
                background-size: 200px 100px;
                animation: twinkle 4s ease-in-out infinite alternate;
            }
            .ultraman-title {
                font-family: 'Arial Black', sans-serif;
                font-size: 5rem;
                font-weight: 900;
                color: #00ffff;
                text-shadow: 
                    0 0 15px #00ffff,
                    0 0 30px #00ffff,
                    0 0 45px #00ffff,
                    0 0 60px #00ffff;
                margin: 30px 0;
                text-align: center;
                letter-spacing: 5px;
                animation: titleGlow 2s ease-in-out infinite alternate;
                opacity: 0;
                animation: titleFadeIn 1s ease-out 2s forwards, titleGlow 2s ease-in-out 3s infinite alternate;
            }
            .ultraman-subtitle {
                font-size: 4rem;
                color: #ffffff;
                margin: 10px 0;
                text-align: center;
                opacity: 0;
                animation: fadeInUp 1s ease-out 2.5s both;
                text-shadow: 0 0 20px #ffffff, 0 0 40px #ffffff, 0 0 60px #ffffff;
            }
            .ultraman-icon {
                width: 300px;
                height: 300px;
                margin: 30px 0;
                opacity: 0;
                animation: iconPulse 2s ease-in-out infinite;
                animation: iconFadeIn 1s ease-out 1.5s forwards, iconPulse 2s ease-in-out 2.5s infinite;
                filter: drop-shadow(0 0 30px #00ffff) drop-shadow(0 0 60px #00ffff);
            }
            .energy-ring {
                position: absolute;
                border: 3px solid #00ffff;
                border-radius: 50%;
                opacity: 0.6;
                animation: energyRotate 3s linear infinite;
            }
            .energy-ring:nth-child(2) {
                border-color: #ff6f61;
                animation: energyRotate 2s linear infinite reverse;
            }
            .energy-ring:nth-child(3) {
                border-color: #00ffff;
                animation: energyRotate 2.5s linear infinite;
            }
            .loading-bar {
                width: 300px;
                height: 4px;
                background: rgba(255,255,255,0.2);
                border-radius: 2px;
                margin: 30px 0;
                overflow: hidden;
                opacity: 0;
                animation: fadeInUp 1s ease-out 3s both;
            }
            .loading-progress {
                height: 100%;
                background: linear-gradient(90deg, #00ffff, #ff6f61, #00ffff);
                background-size: 200% 100%;
                border-radius: 2px;
                animation: loadingProgress 3s ease-in-out 3.5s, gradientShift 2s ease-in-out infinite;
            }
            .ultraman-text {
                color: #ffffff;
                font-size: 2.5rem;
                text-align: center;
                margin: 10px 0;
                opacity: 0;
                animation: fadeInUp 1s ease-out 4s both;
                text-shadow: 0 0 20px #ffffff, 0 0 40px #ffffff, 0 0 60px #ffffff;
            }
            @keyframes twinkle {
                0%, 100% { opacity: 0.3; }
                50% { opacity: 1; }
            }
            @keyframes titleGlow {
                0%, 100% { 
                    text-shadow: 
                        0 0 10px #00ffff,
                        0 0 20px #00ffff,
                        0 0 30px #00ffff,
                        0 0 40px #00ffff;
                }
                50% { 
                    text-shadow: 
                        0 0 20px #00ffff,
                        0 0 30px #00ffff,
                        0 0 40px #00ffff,
                        0 0 50px #00ffff;
                }
            }
            @keyframes titleFadeIn {
                from { opacity: 0; transform: translateY(30px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes iconFadeIn {
                from { opacity: 0; transform: scale(0.5); }
                to { opacity: 1; transform: scale(1); }
            }
            @keyframes iconPulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            @keyframes energyRotate {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            @keyframes loadingProgress {
                from { width: 0%; }
                to { width: 100%; }
            }
            @keyframes gradientShift {
                0%, 100% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
            }
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .hide-intro {
                animation: fadeOut 1s ease-in-out forwards;
            }
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
        </style>
    </head>
    <body>
        <div class="ultraman-intro" id="ultraman-intro">
            <div class="stars"></div>
            <div class="energy-ring" style="width: 600px; height: 600px; animation-delay: 0s;"></div>
            <div class="energy-ring" style="width: 500px; height: 500px; animation-delay: 0.5s; border-color: #ff6f61;"></div>
            <div class="energy-ring" style="width: 400px; height: 400px; animation-delay: 1s; border-color: #00ffff;"></div>
            
            <div class="ultraman-logo">
                <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIwIiBoZWlnaHQ9IjEyMCIgdmlld0JveD0iMCAwIDEyMCAxMjAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMjAiIGhlaWdodD0iMTIwIiBmaWxsPSIjMDA0NDQ0Ii8+CjxjaXJjbGUgY3g9IjYwIiBjeT0iNjAiIHI9IjUwIiBmaWxsPSIjMDBmZmZmIiBvcGFjaXR5PSIwLjgiLz4KPGNpcmNsZSBjeD0iNjAiIGN5PSI2MCIgcj0iMzAiIGZpbGw9IiNmZmZmZmYiLz4KPHN2ZyB4PSI0NSIgeT0iNDUiIHdpZHRoPSIzMCIgaGVpZ2h0PSIzMCIgdmlld0JveD0iMCAwIDMwIDMwIiBmaWxsPSJub25lIj4KPHBhdGggZD0iTTE1IDVMMjAgMTBMMTUgMTVMMTAgMTBMMTUgNVoiIGZpbGw9IiMwMDAwMDAiLz4KPC9zdmc+Cjwvc3ZnPgo=" 
                     alt="Ultraman" class="ultraman-icon" />
            </div>
            
            <h1 class="ultraman-title">NE`XUS ULTRA</h1>
            <p class="ultraman-subtitle">Respected King of the Universe</p>
            <p class="ultraman-text">Welcome back to Nebula M78</p>
            
            <div class="loading-bar">
                <div class="loading-progress"></div>
            </div>
            
            <p class="ultraman-text">Initializing System...</p>
        </div>
        
        <script>
        // 7秒后隐藏动画
        setTimeout(function() {
            const intro = document.getElementById('ultraman-intro');
            if (intro) {
                intro.classList.add('hide-intro');
                setTimeout(function() {
                    if (intro && intro.parentNode) {
                        intro.parentNode.removeChild(intro);
                    }
                }, 1000);
            }
        }, 7000);
        </script>
    </body>
    </html>
    """
    
    components.html(intro_html, height=1200, width=1400)

# 检查是否需要显示开场动画
if 'ultraman_intro_shown' not in st.session_state:
    st.session_state.ultraman_intro_shown = True
    
    # 创建专门的动画页面
    st.markdown("""
    <style>
    .main > div {
        padding-top: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 显示奥特曼开场动画
    show_ultraman_intro()
    
    # 使用Python实现自动跳转
    import time
    time.sleep(10)  # 动画时长(7秒) + 3秒缓冲
    st.rerun()
    
    # 阻止显示其他内容
    st.stop()

# 加载增强版CSS样式
enhanced_css_file = os.path.join(current_dir, 'static/css/enhanced_style.css')
if os.path.exists(enhanced_css_file):
    st.markdown('<style>' + open(enhanced_css_file).read() + '</style>', unsafe_allow_html=True)
else:
    st.markdown('<style>' + open(css_file).read() + '</style>', unsafe_allow_html=True)
# 初始化session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "💗 Home"

with st.sidebar:
    st.markdown("## 🚀 NEXUS ULTRA 系统")
    st.markdown("---")
    
    # 主页介绍按钮
    if st.button("💗 Home", key="home", use_container_width=True):
        st.session_state.current_page = "💗 Home"
        st.rerun()
    
    # WOS文件解析按钮
    if st.button("📊 WOS文件解析", key="wos_parse", use_container_width=True):
        st.session_state.current_page = "📊 WOS文件解析"
        st.rerun()
    
    st.markdown("---")
    
    # 背景音乐选择
    st.markdown("### 🎵 背景音乐")
    music_choice = st.radio("选择音乐", ["🎧 音乐1", "🎧 音乐2" ], index=1, horizontal=True)
    
    if music_choice == "🎧 音乐1":
        audio_file = library_dir + "1.mp3"
    elif music_choice == "🎧 音乐2":
        audio_file = library_dir + "2.mp3"
    
    # 检查音频文件是否存在
    if os.path.exists(audio_file):
        st.audio(audio_file, format='mp3', loop=True, autoplay=False)
    else:
        st.warning("音频文件不存在")

# with st.sidebar:
#     page= option_menu(menu_title="导航栏",      options=["WOS文件解析", "文献数据库分析", '耦合关系网络'],
#                            icons=["bar - chart", "analytics", "input"],
#                            menu_icon="list - ul",
#                            default_index=0,
#                            orientation="vertical",
#                            styles={
#                                "container": {"padding": "10px", "background - color": "#f0f0f0"},
#                                "icon": {"color": "blue", "font - size": "50pxr"},
#                                "nav - link": {"font - size": "40px", "text - align": "left", "margin": "0px",
#                                               "--hover - color": "#ddd"},
#                                "nav - link - selected": {"background - color": "#007bff", "color": "white"}
#                            })


# 根据session state显示不同页面
page = st.session_state.current_page

if page == "💗 Home":
    # 使用奥特曼6.png作为主页图片，与其他页面保持一致的标题样式
    ultraman_6_path = os.path.join(library_dir, "奥特曼6.png")
    set_page_title_with_image(image_path=ultraman_6_path, title="NEXUS ULTRA 系统", image_width=400, image_height=400)
    
    # 高级感功能模块介绍
    st.markdown("""
    <div style="text-align: center; margin-bottom: 50px;">
        <h2 style="color: #2C3E50; font-size: 2.2rem; font-weight: 300; margin-bottom: 15px; letter-spacing: 1px;">系统功能模块</h2>
        <div style="width: 80px; height: 2px; background: linear-gradient(90deg, #C0D6EA 0%, #B5A8CA 100%); margin: 0 auto; border-radius: 1px;"></div>
    </div>
    """, unsafe_allow_html=True)

    # 创建2x2网格布局展示四个不同颜色爱心的功能 - 高级感设计
    col1, col2 = st.columns(2)
    
    with col1:
        # 红色爱心 - 文献计量分析
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255, 182, 193, 0.1) 0%, rgba(255, 192, 203, 0.1) 100%); padding: 30px 25px; border-radius: 20px; margin-bottom: 25px; border: 1px solid rgba(255, 182, 193, 0.3); backdrop-filter: blur(10px); transition: all 0.3s ease; box-shadow: 0 8px 32px rgba(255, 182, 193, 0.2);">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 2.5rem; margin-bottom: 15px;">❤️</div>
                <h3 style="color: #2C3E50; font-size: 1.3rem; font-weight: 500; margin-bottom: 20px; letter-spacing: 0.5px;">文献计量分析</h3>
            </div>
            <div style="color: #5A4B6B; font-size: 0.95rem; line-height: 1.8;">
                <div style="margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #FFB6C1; border-radius: 50%; margin-right: 12px;"></span>
                    WOS文件解析与数据清洗
                </div>
                <div style="margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #FFB6C1; border-radius: 50%; margin-right: 12px;"></span>
                    作者合作网络分析
                </div>
                <div style="margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #FFB6C1; border-radius: 50%; margin-right: 12px;"></span>
                    关键词共现与趋势分析
                </div>
                <div style="display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #FFB6C1; border-radius: 50%; margin-right: 12px;"></span>
                    交互式可视化仪表板
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 蓝色爱心 - 研究报告生成器
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(173, 216, 230, 0.1) 0%, rgba(135, 206, 235, 0.1) 100%); padding: 30px 25px; border-radius: 20px; margin-bottom: 25px; border: 1px solid rgba(173, 216, 230, 0.3); backdrop-filter: blur(10px); transition: all 0.3s ease; box-shadow: 0 8px 32px rgba(173, 216, 230, 0.2);">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 2.5rem; margin-bottom: 15px;">💙</div>
                <h3 style="color: #2C3E50; font-size: 1.3rem; font-weight: 500; margin-bottom: 20px; letter-spacing: 0.5px;">研究报告生成器</h3>
            </div>
            <div style="color: #5A4B6B; font-size: 0.95rem; line-height: 1.8;">
                <div style="margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #ADD8E6; border-radius: 50%; margin-right: 12px;"></span>
                    基于R-Bibliometrix分析
                </div>
                <div style="margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #ADD8E6; border-radius: 50%; margin-right: 12px;"></span>
                    符合JCP期刊要求
                </div>
                <div style="margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #ADD8E6; border-radius: 50%; margin-right: 12px;"></span>
                    自动生成学术论文初稿
                </div>
                <div style="display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #ADD8E6; border-radius: 50%; margin-right: 12px;"></span>
                    一键导出完整报告
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # 绿色爱心 - WOS字段文档
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(144, 238, 144, 0.1) 0%, rgba(152, 251, 152, 0.1) 100%); padding: 30px 25px; border-radius: 20px; margin-bottom: 25px; border: 1px solid rgba(144, 238, 144, 0.3); backdrop-filter: blur(10px); transition: all 0.3s ease; box-shadow: 0 8px 32px rgba(144, 238, 144, 0.2);">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 2.5rem; margin-bottom: 15px;">💚</div>
                <h3 style="color: #2C3E50; font-size: 1.3rem; font-weight: 500; margin-bottom: 20px; letter-spacing: 0.5px;">WOS字段文档</h3>
            </div>
            <div style="color: #5A4B6B; font-size: 0.95rem; line-height: 1.8;">
                <div style="margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #90EE90; border-radius: 50%; margin-right: 12px;"></span>
                    48个标准字段说明
                </div>
                <div style="margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #90EE90; border-radius: 50%; margin-right: 12px;"></span>
                    分类展示与查找
                </div>
                <div style="margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #90EE90; border-radius: 50%; margin-right: 12px;"></span>
                    使用指南与示例
                </div>
                <div style="display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #90EE90; border-radius: 50%; margin-right: 12px;"></span>
                    常见问题解答
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 紫色爱心 - 高级功能
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(221, 160, 221, 0.1) 0%, rgba(238, 130, 238, 0.1) 100%); padding: 30px 25px; border-radius: 20px; margin-bottom: 25px; border: 1px solid rgba(221, 160, 221, 0.3); backdrop-filter: blur(10px); transition: all 0.3s ease; box-shadow: 0 8px 32px rgba(221, 160, 221, 0.2);">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 2.5rem; margin-bottom: 15px;">💜</div>
                <h3 style="color: #2C3E50; font-size: 1.3rem; font-weight: 500; margin-bottom: 20px; letter-spacing: 0.5px;">高级功能</h3>
            </div>
            <div style="color: #5A4B6B; font-size: 0.95rem; line-height: 1.8;">
                <div style="margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #DDA0DD; border-radius: 50%; margin-right: 12px;"></span>
                    动态网络可视化
                </div>
                <div style="margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #DDA0DD; border-radius: 50%; margin-right: 12px;"></span>
                    多维度数据分析
                </div>
                <div style="margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #DDA0DD; border-radius: 50%; margin-right: 12px;"></span>
                    智能数据导出
                </div>
                <div style="display: flex; align-items: center;">
                    <span style="width: 6px; height: 6px; background: #DDA0DD; border-radius: 50%; margin-right: 12px;"></span>
                    自定义分析报告
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 专业脚注
    st.markdown("""
    <div style="text-align: center; margin-top: 60px; padding: 30px; background: linear-gradient(135deg, rgba(192, 214, 234, 0.05) 0%, rgba(181, 168, 202, 0.05) 100%); border-radius: 20px; border: 1px solid rgba(181, 168, 202, 0.15);">
        <p style="color: #6B5B7B; font-size: 1.1rem; font-weight: 500; margin: 0; letter-spacing: 0.5px;">
            🐰HBD， Best wishes for what you want ｜ Vivian🐭
        </p>
    </div>
    """, unsafe_allow_html=True)

# elif page == "WOS file parsing":
#     # 使用奥特曼1.png
#     ultraman_1_path = os.path.join(library_dir, "奥特曼1.png")
#     set_page_title_with_image(image_path=ultraman_1_path, title="WOS File Parsing", image_width=400, image_height=400)
#     
#     # 添加功能介绍
#     st.markdown("""
#     <div style="background: linear-gradient(135deg, #C0D6EA 0%, #B5A8CA 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px; color: #4A3C5C;">
#         <h3 style="color: #4A3C5C; margin: 0 0 10px 0;">📁 第一步：WOS文件解析</h3>
#         <p style="margin: 0; font-size: 16px; color: #5A4B6B;">上传从Web of Science导出的.txt文件，系统将自动解析文献数据，提取作者、标题、期刊、引用等关键信息，为后续分析做准备。</p>
#     </div>
#     """, unsafe_allow_html=True)
# 
#     df,file_exists=process_wos_page_upload()
#     if file_exists:
#         selected_df=process_wos_page_download(df)
#         Save_Form_to_Csv(df_name=" Filtered columns ", df=selected_df, autotext="Selected_Database")

# elif page == "Analysis of literature databases":
#     # 使用奥特曼2.png
#     ultraman_2_path = os.path.join(library_dir, "奥特曼2.png")
#     set_page_title_with_image(image_path=ultraman_2_path, title="Analysis of Literature Databases", image_width=400, image_height=400)
#     
#     # 添加功能介绍
#     st.markdown("""
#     <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px; color: white;">
#         <h3 style="color: white; margin: 0 0 10px 0;">📊 第二步：文献数据库分析</h3>
#         <p style="margin: 0; font-size: 16px;">基于解析后的文献数据，进行全面的文献计量分析，包括发文趋势、作者合作、期刊分析、引用统计等，生成详细的统计报告和可视化图表。</p>
#     </div>
#     """, unsafe_allow_html=True)
# 
#     process_database_page(a=1)

# elif page == "coupled network of relationships":
#     # 使用奥特曼3.png
#     ultraman_3_path = os.path.join(library_dir, "奥特曼3.png")
#     set_page_title_with_image(image_path=ultraman_3_path, title="Coupled Network of Relationships", image_width=400, image_height=400)
#     
#     # 添加功能介绍
#     st.markdown("""
#     <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px; color: white;">
#         <h3 style="color: white; margin: 0 0 10px 0;">🔗 第三步：耦合关系网络</h3>
#         <p style="margin: 0; font-size: 16px;">分析作者之间的合作关系，构建耦合关系网络图，识别核心作者群体和合作模式，为研究团队分析提供可视化支持。</p>
#     </div>
#     """, unsafe_allow_html=True)
# 
#     st.subheader("Upload CSV File")
#     uploaded_file = st_file_uploader("Upload parsed file: csv format", type=["csv"], label_visibility='collapsed')
#     if uploaded_file is not None:
#         # 读取 CSV 文件
#         rawdf = pd.read_csv(uploaded_file)
# 
#         # 显示原始数据
#         st.subheader("Raw Data")
#         st.dataframe(rawdf)
# 
#         # 检查是否包含"作者"字段
#         if "作者" not in rawdf.columns:
#             st.error("上传的文件必须包含 '作者' 字段！")
#         else:
#             # 处理作者数据
#             edges_df = process_author_data(rawdf)
# 
#             # 生成节点数据
#             all_authors = set(edges_df["source"]).union(set(edges_df["target"]))
#             nodes = [{"name": author, "x": i, "y": i} for i, author in enumerate(all_authors)]
# 
#             # 生成边数据
#             edges = [
#                 {
#                     "source": next(node for node in nodes if node["name"] == row["source"]),
#                     "target": next(node for node in nodes if node["name"] == row["target"]),
#                     "weight": row["weight"]
#                 }
#                 for _, row in edges_df.iterrows()
#             ]
# 
#             # 绘制网络图
#             st.subheader("Author Coupled Network Diagram")
#             fig = draw_author_network(nodes, edges)
#             st.plotly_chart(fig, use_container_width=True)
# 
#             # 显示合作关系数据
#             st.subheader("Partnership data")
#             st.dataframe(edges_df)

elif page == "📊 WOS文件解析":
    # 使用奥特曼5.png
    ultraman_5_path = os.path.join(library_dir, "奥特曼5.png")
    set_page_title_with_image(image_path=ultraman_5_path, title="WOS文件解析", image_width=400, image_height=400)
    
    # 添加功能介绍
    st.markdown("""
    <div style="background: linear-gradient(135deg, #C0D6EA 0%, #B5A8CA 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px; color: #4A3C5C;">
        <h3 style="color: #4A3C5C; margin: 0 0 10px 0;">📊 WOS文件解析</h3>
        <p style="margin: 0; font-size: 16px; color: #5A4B6B;">上传Web of Science导出的文件，系统将自动解析文献数据，提取作者、标题、期刊、引用等关键信息，为后续分析做准备。支持.txt、.csv、.bib格式。</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 文件上传
    st.subheader("📁 数据上传")
    uploaded_file = st_file_uploader("上传文献数据文件", type=["txt", "csv", "bib"], label_visibility='collapsed')
    
    if uploaded_file is not None:
        # 显示文件信息
        st.info(f"📁 {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        
        # 加载数据
        with st.spinner("🔄 正在解析文件..."):
            df = load_data(uploaded_file)
        
        if df is not None and not df.empty:
            # 显示数据概览
            st.subheader("📊 数据概览")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总文献数", len(df))
            with col2:
                st.metric("总作者数", len(set([author for authors in safe_get_column(df, ['Authors']) if pd.notna(authors) for author in str(authors).split(';')])))
            with col3:
                st.metric("总期刊数", len(set(safe_get_column(df, ['Source']).dropna())))
            with col4:
                times_cited_col = safe_get_column(df, ['TimesCited'])
                if not times_cited_col.empty and times_cited_col.iloc[0] != "":
                    total_citations = pd.to_numeric(times_cited_col, errors='coerce').sum()
                    st.metric("总被引次数", f"{total_citations:,.0f}")
                else:
                    st.metric("总被引次数", "N/A")
            
            # 显示数据预览
            st.subheader("📋 数据预览")
            st.dataframe(df.head(10), use_container_width=True)
            
            # 分析选项
            st.subheader("🔍 分析选项")
            analysis_type = st.selectbox(
                "选择分析类型",
                ["总体信息概览", "作者分析", "国家地区分析", "机构分析", "被引文献分析", "关键词共现分析", "研究趋势分析"],
                key="analysis_type"
            )
            
            if analysis_type == "总体信息概览":
                analyze_overview_statistics(df)
            elif analysis_type == "作者分析":
                analyze_authors(df)
            elif analysis_type == "国家地区分析":
                analyze_countries(df)
            elif analysis_type == "机构分析":
                analyze_institutions(df)
            elif analysis_type == "被引文献分析":
                analyze_cited_references(df)
            elif analysis_type == "关键词共现分析":
                analyze_keywords(df)
            elif analysis_type == "研究趋势分析":
                analyze_trends(df)
        else:
            st.error("❌ 数据加载失败，请检查文件格式")
    
    else:
        st.info("👆 请上传文件")


# 运行应用程序
if __name__ == "__main__":
    uploaded_file = None
