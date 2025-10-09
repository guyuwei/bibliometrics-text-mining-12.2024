import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import re
from datetime import datetime

from PIL.ImageOps import expand
from pandas.io.common import file_exists
from streamlit import session_state
from streamlit_option_menu import option_menu
import math
import numpy as np
import sys
import os

current_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.dirname(current_dir).replace("/Program","")
library_dir=project_root+ '/library/web_sources/'
picture_path=project_root+ '/output/picture'
csv_path= project_root+'/output/'

# sys.path.append(project_root)  # 添加项目根目录
#
# sys.path.append(os.path.join(project_root, 'Calculate_Anaysis'))
# sys.path.append(os.path.join(project_root, 'Documents_Processing'))
# sys.path.append(os.path.join(project_root, 'Result_Visualization'))
from Calculate_Anaysis.Calculate_Author import calculate_core_author_publication,calculate_number_of_authors_publication
from Calculate_Anaysis.Calculate_Country import calculate_collaboration_countries
from Calculate_Anaysis.Calculate_Publication import calculate_publications_per_year
from Calculate_Anaysis.Calculate_Sources import calculate_number_of_sources
from Calculate_Anaysis.Calculate_Keywords import calculate_number_of_keywords
from Calculate_Anaysis.Calculate_Reference import calculate_number_of_total_references_cited,filter_references_by_authors,extract_each_article_author_refauthor
from Calculate_Anaysis.Calculate_Citiation import calculate_number_of_total_Timescitedcount
from Calculate_Anaysis.Calculate_Year import exact_targetarticles_within_yearspan,calculate_age
from Result_Visualization.Descriptive_Statistics import Form_Information_Description,shift_edited_df_into_list
from Result_Visualization.Publications_and_Authors import draw_author_density_visualiaztion,draw_author_overlay_visualiaztion,draw_author_network_visualiaztion
from Documents_Processing.Uploading_Files import Load_TXT,Load_CSV,Load_Refine,Extract_Info_From_Refine
from Documents_Processing.Web_Format import st_header, st_subheader, st_selectbox, st_card, st_tags, st_radio, st_button, st_slider, st_checkbox, st_text_area, st_text_input, \
    st_multiselect, st_warning, st_markdown, st_latex, st_table, st_dataframe, st_sidebar_slider, st_file_uploader, st_expander,st_subsubheader,set_page_title_with_image

from Documents_Processing.Tab_Process import process_tabledescribe_tab,process_Publication_Author_Analysis_Tab,process_Publication_Author_Tab_Most_Productive,process_Overall_Information_Overview_Tab,process_Journay_Analysis_Tab,process_Country_Analysis_Tab
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

# 定义滑动条的回调函数
def slider_callback():
    session_state_year= False

def process_wos_page_upload():
    st.subheader("📁 Upload Literature Data File")
    st.markdown("**请上传文献数据文件**")
    st.info("💡 支持WOS导出文件(.txt)、CSV数据文件(.csv)、BibTeX文献文件(.bib)")
    uploaded_file = st.file_uploader(
        "选择文献数据文件", 
        type=["txt", "csv", "bib"], 
        key="wos_main_file"
    )
    
    st.markdown("---")
    st_header("📊 Upload Refine File (Optional)")
    st.markdown("**可选：上传Excel格式的数据精炼文件**")
    st.info("💡 可选的Excel格式精炼文件，用于数据增强")
    refine_file = st.file_uploader(
        "选择精炼文件", 
        type=["xlsx"],
        key="wos_refine_file"
    )

    if uploaded_file is not None:
        file_exists = True
        try:
            # 根据文件类型选择解析器
            if uploaded_file.name.endswith('.txt'):
                # 使用增强的WOS解析器
                try:
                    from .Uploading_Files import Load_TXT_Enhanced
                    df = Load_TXT_Enhanced(uploaded_file)
                except ImportError:
                    # 回退到原始解析器
                    df = Load_TXT(uploaded_file)
            elif uploaded_file.name.endswith('.csv'):
                df = Load_CSV(uploaded_file)
            elif uploaded_file.name.endswith('.bib'):
                # 使用增强的文件上传器加载BIB文件
                try:
                    from .Enhanced_File_Uploader import load_file_universal
                    df = load_file_universal(uploaded_file)
                except ImportError:
                    st.error("BIB文件解析功能不可用，请检查模块导入")
                    return pd.DataFrame(), False
            else:
                st.error("不支持的文件格式，请上传.txt、.csv或.bib文件")
                return pd.DataFrame(), False
            
            # 检查DataFrame是否有效
            if df is None or df.empty:
                st.error("文件解析失败或文件为空，请检查文件格式")
                return pd.DataFrame(), False
            
            if refine_file:
                try:
                    df_refine = Load_Refine(refine_file)
                    # 将会话状态存储refine数据
                    st.session_state['refine_data'] = Extract_Info_From_Refine(df_refine)
                except Exception as e:
                    st.warning(f"精炼文件处理失败: {str(e)}")
                    # 即使精炼文件失败，仍然返回主数据
            
            st.success(f"✅ 文件上传成功！解析到 {len(df)} 条文献记录")
            return df, file_exists
            
        except Exception as e:
            st.error(f"处理文件时出错: {str(e)}")
            return pd.DataFrame(), False
    else:
        file_exists = False
        return pd.DataFrame(), file_exists
def process_wos_page_download(df):
    st.subheader("Field Parsing Result")
    st.dataframe(df, height=500, width=2800, use_container_width=True,selection_mode=["multi-row"])
    st_subsubheader("Database Description")
    number_of_total_articles = df.shape[0]
    count_result = {}  # 数据库的info
    missing_value_columns = st.multiselect('选择需要统计的参数:', df.columns,
                                           default=df.columns[:6],label_visibility="collapsed")
    if missing_value_columns:
        for para in missing_value_columns:
            count_result[para] = {"共计": str(len(df[para].value_counts())),
                                  "缺失值": str(number_of_total_articles - len(
                                      df[para].value_counts())),
                                  "参数类型": type(df[para][0]).__name__}
        count_result = pd.DataFrame(count_result).sort_index(axis=1)
        st.dataframe(count_result,height=100,width=400,use_container_width=True)
    st_subsubheader("Selected Columns to Perform Text Minging")

    selected_columns = st.multiselect('选择列:', df.columns, default=df.columns,label_visibility="collapsed")
    selected_df = df[selected_columns]
    st_subsubheader("Please enter the saved filename of the filtered table.".title())
    return selected_df



def process_database_page(a):

    st.subheader("Upload CSV Film")
    uploaded_file = st_file_uploader("上传解析文件：csv格式", type=["csv"])
    if uploaded_file is not None:
        rawdf = Load_CSV(uploaded_file)
        st.dataframe(rawdf, height=500, width=2800,use_container_width=True)
        st.subheader("Data Analysis")
        sorted_data, years, publications_per_year = calculate_publications_per_year(rawdf)
        (start, stop) = st.slider(
                label="选择纳入统计分析的年份",  # 滑动条的标题，显示给用户提示其功能
                min_value=int(min(years)),  # 滑动条区间的最小值
                max_value=int(max(years)),  # 滑动条区间的最大值
                value=(                    int(min(years)) , int(max(years)) - 1),
                step=1,label_visibility="collapsed",on_change=slider_callback)
        df = exact_targetarticles_within_yearspan(rawdf, start, stop)  # 按照年份提取的讨论范围内的文章
        st.markdown("""
        <style>
            .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
                font-size: 20px;
            }
        </style>
        """, unsafe_allow_html=True)

        # 创建高级感标签页
        st.markdown("""
        <div style="margin-bottom: 30px;">
            <h3 style="color: #2C3E50; font-size: 1.8rem; font-weight: 400; margin-bottom: 20px; text-align: center; letter-spacing: 0.5px;">📊 数据分析模块</h3>
            <div style="width: 100px; height: 2px; background: linear-gradient(90deg, #C0D6EA 0%, #B5A8CA 100%); margin: 0 auto 30px; border-radius: 1px;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        tabs = st.tabs([
            '📈 总体信息概览',
            '👥 发文作者分析', 
            '📚 期刊影响力分析',
            '🌍 国家地区分析'
        ])
        with tabs[0]:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(192, 214, 234, 0.08) 0%, rgba(181, 168, 202, 0.08) 100%); padding: 25px; border-radius: 20px; margin-bottom: 25px; border: 1px solid rgba(181, 168, 202, 0.2); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(181, 168, 202, 0.1);">
                <h4 style="color: #2C3E50; font-size: 1.3rem; font-weight: 500; margin-bottom: 15px; letter-spacing: 0.3px;">📈 总体信息概览</h4>
                <p style="color: #5A4B6B; font-size: 0.95rem; line-height: 1.6; margin: 0;">展示文献数据库的基本统计信息，包括发文趋势、时间分布、核心指标等关键数据。</p>
            </div>
            """, unsafe_allow_html=True)
            number_of_total_unique_authors=process_Overall_Information_Overview_Tab(df,start, stop)
        with tabs[1]:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(192, 214, 234, 0.08) 0%, rgba(181, 168, 202, 0.08) 100%); padding: 25px; border-radius: 20px; margin-bottom: 25px; border: 1px solid rgba(181, 168, 202, 0.2); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(181, 168, 202, 0.1);">
                <h4 style="color: #2C3E50; font-size: 1.3rem; font-weight: 500; margin-bottom: 15px; letter-spacing: 0.3px;">👥 发文作者分析</h4>
                <p style="color: #5A4B6B; font-size: 0.95rem; line-height: 1.6; margin: 0;">深入分析作者发文情况，识别高产作者、合作网络、影响力评估等关键指标。</p>
            </div>
            """, unsafe_allow_html=True)
            number_of_total_articles=df.shape[0]
            n_max,rounded_m,most_citiations,number_of_authors_publication_df=process_Publication_Author_Analysis_Tab(df,number_of_total_unique_authors,number_of_total_articles)
            process_Publication_Author_Tab_Most_Productive(n_max, rounded_m, most_citiations, number_of_authors_publication_df)
        with tabs[2]:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(192, 214, 234, 0.08) 0%, rgba(181, 168, 202, 0.08) 100%); padding: 25px; border-radius: 20px; margin-bottom: 25px; border: 1px solid rgba(181, 168, 202, 0.2); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(181, 168, 202, 0.1);">
                <h4 style="color: #2C3E50; font-size: 1.3rem; font-weight: 500; margin-bottom: 15px; letter-spacing: 0.3px;">📚 期刊影响力分析</h4>
                <p style="color: #5A4B6B; font-size: 0.95rem; line-height: 1.6; margin: 0;">评估期刊的学术影响力，分析发文分布、引用情况、期刊排名等核心指标。</p>
            </div>
            """, unsafe_allow_html=True)
            process_Journay_Analysis_Tab(df)
        with tabs[3]:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(192, 214, 234, 0.08) 0%, rgba(181, 168, 202, 0.08) 100%); padding: 25px; border-radius: 20px; margin-bottom: 25px; border: 1px solid rgba(181, 168, 202, 0.2); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(181, 168, 202, 0.1);">
                <h4 style="color: #2C3E50; font-size: 1.3rem; font-weight: 500; margin-bottom: 15px; letter-spacing: 0.3px;">🌍 国家地区分析</h4>
                <p style="color: #5A4B6B; font-size: 0.95rem; line-height: 1.6; margin: 0;">分析研究的地理分布，识别主要研究国家、国际合作模式、地区影响力等关键信息。</p>
            </div>
            """, unsafe_allow_html=True)
            process_Country_Analysis_Tab(df)

