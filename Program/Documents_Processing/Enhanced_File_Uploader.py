"""
增强的文件上传处理器
支持WOS、CSV、BIB等多种文件格式
"""

import pandas as pd
import streamlit as st
import bibtexparser
from typing import Optional, Tuple
import io

def load_bib_file(uploaded_file) -> pd.DataFrame:
    """
    加载和解析BIB文件
    
    Args:
        uploaded_file: Streamlit上传的文件对象
        
    Returns:
        pd.DataFrame: 解析后的数据框
    """
    try:
        # 读取BIB文件内容
        bib_content = uploaded_file.read().decode('utf-8')
        
        # 解析BIB文件
        bib_database = bibtexparser.loads(bib_content)
        
        if not bib_database.entries:
            st.warning("BIB文件中没有找到有效的文献条目")
            return pd.DataFrame()
        
        # 转换为DataFrame
        entries_list = []
        for entry in bib_database.entries:
            # 标准化字段名
            standardized_entry = {}
            for field, value in entry.items():
                # 移除BibTeX的大括号
                clean_value = value.strip('{}')
                standardized_entry[field] = clean_value
            
            entries_list.append(standardized_entry)
        
        df = pd.DataFrame(entries_list)
        
        if df.empty:
            st.warning("BIB文件解析成功，但未找到有效的文献数据")
            return pd.DataFrame()
        
        # 标准化列名映射
        column_mapping = {
            'title': '文献标题',
            'author': '作者',
            'journal': '期刊名称',
            'year': '出版年',
            'volume': '卷',
            'number': '期',
            'pages': '页码',
            'doi': 'DOI',
            'abstract': '摘要',
            'keywords': '关键词',
            'publisher': '出版商',
            'booktitle': '书名',
            'editor': '编辑',
            'series': '丛书',
            'address': '地址',
            'url': 'URL',
            'isbn': 'ISBN',
            'issn': 'ISSN',
            'note': '备注',
            'type': '文献类型',
            'ENTRYTYPE': '文献类型'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 处理作者字段（多个作者用分号分隔）
        if '作者' in df.columns:
            df['作者'] = df['作者'].astype(str).str.replace(' and ', '; ')
        
        # 处理年份字段
        if '出版年' in df.columns:
            df['出版年'] = pd.to_numeric(df['出版年'], errors='coerce')
        
        # 处理页码字段
        if '页码' in df.columns:
            df['页码'] = df['页码'].astype(str)
        
        # 显示解析结果
        st.success(f"✅ BIB文件解析成功！")
        st.info(f"📁 文件名: {uploaded_file.name}")
        st.info(f"📚 解析到 {len(df)} 条文献记录")
        
        # 显示字段统计
        if not df.empty:
            field_stats = {
                '字段名': list(df.columns),
                '非空记录数': [df[col].notna().sum() for col in df.columns],
                '数据类型': [str(df[col].dtype) for col in df.columns]
            }
            field_df = pd.DataFrame(field_stats)
            st.dataframe(field_df, use_container_width=True)
        
        return df
        
    except Exception as e:
        st.error(f"解析BIB文件时出错: {str(e)}")
        return pd.DataFrame()

def load_csv_file(uploaded_file) -> pd.DataFrame:
    """
    加载CSV文件
    
    Args:
        uploaded_file: Streamlit上传的文件对象
        
    Returns:
        pd.DataFrame: 解析后的数据框
    """
    try:
        # 尝试多种编码方式读取CSV文件
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'gbk']
        df = None
        
        for encoding in encodings:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(io.StringIO(uploaded_file.read().decode(encoding)))
                break
            except (UnicodeDecodeError, pd.errors.EmptyDataError):
                continue
        
        if df is None:
            st.error("无法读取CSV文件：不支持的文件编码格式")
            return pd.DataFrame()
        
        if df.empty:
            st.warning("CSV文件为空")
            return pd.DataFrame()
        
        st.success(f"✅ CSV文件加载成功！")
        st.info(f"📁 文件名: {uploaded_file.name}")
        st.info(f"📚 解析到 {len(df)} 条记录")
        
        return df
        
    except Exception as e:
        st.error(f"加载CSV文件时出错: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_file_universal(uploaded_file) -> pd.DataFrame:
    """
    通用文件加载函数，支持多种格式
    
    Args:
        uploaded_file: Streamlit上传的文件对象
        
    Returns:
        pd.DataFrame: 解析后的数据框
    """
    if uploaded_file is None:
        return pd.DataFrame()
    
    file_extension = uploaded_file.name.lower().split('.')[-1]
    
    try:
        if file_extension == 'txt':
            # 使用增强的WOS解析器
            try:
                from .Uploading_Files import Load_TXT_Enhanced
                return Load_TXT_Enhanced(uploaded_file)
            except ImportError:
                from .Uploading_Files import Load_TXT
                return Load_TXT(uploaded_file)
                
        elif file_extension == 'csv':
            return load_csv_file(uploaded_file)
            
        elif file_extension == 'bib':
            return load_bib_file(uploaded_file)
            
        else:
            st.error(f"不支持的文件格式: .{file_extension}")
            st.info("支持的文件格式: .txt (WOS), .csv, .bib")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"处理文件时出错: {str(e)}")
        return pd.DataFrame()

def create_enhanced_file_uploader(label: str, supported_types: list, key: str = None) -> Optional[object]:
    """
    创建增强的文件上传器
    
    Args:
        label: 上传器标签
        supported_types: 支持的文件类型列表
        key: 组件key
        
    Returns:
        文件上传器对象
    """
    # 文件类型说明
    type_descriptions = {
        'txt': 'WOS导出文件 (.txt)',
        'csv': 'CSV数据文件 (.csv)', 
        'bib': 'BibTeX文献文件 (.bib)'
    }
    
    # 创建类型说明文本
    type_text = " | ".join([type_descriptions.get(t, t) for t in supported_types])
    
    st.markdown(f"""
    <div style="margin-bottom: 10px;">
        <p style="color: #5A4B6B; font-size: 0.9rem; margin: 0;">💡 支持的文件格式: {type_text}</p>
    </div>
    """, unsafe_allow_html=True)
    
    return st.file_uploader(
        label,
        type=supported_types,
        key=key,
        help=f"支持的文件格式: {', '.join(supported_types)}"
    )

def validate_file_format(uploaded_file) -> Tuple[bool, str]:
    """
    验证上传文件的格式
    
    Args:
        uploaded_file: 上传的文件对象
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if uploaded_file is None:
        return False, "请选择文件"
    
    file_extension = uploaded_file.name.lower().split('.')[-1]
    supported_types = ['txt', 'csv', 'bib']
    
    if file_extension not in supported_types:
        return False, f"不支持的文件格式: .{file_extension}。支持格式: {', '.join(supported_types)}"
    
    return True, "文件格式有效"
