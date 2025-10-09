"""
增强的Web of Science (WOS) 文件解析器
基于WOS官方格式标准，提供完整的字段映射和数据解析功能
"""

import pandas as pd
import streamlit as st
from typing import Tuple, Optional
import re

class EnhancedWOSParser:
    """增强的WOS文件解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.valid_fields = {
            # 基本标识字段
            'FN', 'VR', 'PT', 'UT', 'AR',
            # 作者相关字段
            'AU', 'AF', 'BA', 'BF', 'CA', 'GP', 'RI', 'OI',
            # 标题和摘要
            'TI', 'AB', 'MA',
            # 期刊和出版物信息
            'SO', 'J9', 'JI', 'SN', 'EI', 'BN',
            # 出版信息
            'PY', 'PD', 'VL', 'IS', 'BP', 'EP', 'PG', 'DI', 'D2',
            # 出版商信息
            'PU', 'PI', 'PA', 'PN',
            # 关键词和主题
            'DE', 'ID', 'WC', 'SC',
            # 地址信息
            'C1', 'RP', 'EM',
            # 会议信息
            'CT', 'CY', 'CL', 'HO', 'SP',
            # 引用信息
            'CR', 'NR', 'TC', 'Z9', 'U1', 'U2',
            # 基金信息
            'FU', 'FX',
            # 其他信息
            'LA', 'DT', 'OA', 'PM', 'GA', 'SE', 'SI', 'DA', 'EA', 'EY', 'ES', 'ET', 'WE'
        }
        
        # 字段映射到中文名称
        self.field_mapping = {
            'AU': 'Authors', 'AF': 'Authors', 'TI': 'Title', 'SO': 'Source', 'PY': 'Year',
            'AB': 'Abstract', 'DE': 'Keywords', 'ID': 'KeywordsPlus', 'C1': 'Address',
            'CR': 'References', 'TC': 'TimesCited', 'Z9': 'TotalTimesCited',
            'J9': 'JournalAbbreviation', 'JI': 'JournalISO', 'VL': 'Volume', 'IS': 'Issue',
            'BP': 'BeginningPage', 'EP': 'EndingPage', 'DI': 'DOI', 'SN': 'ISSN',
            'EI': 'eISSN', 'PU': 'Publisher', 'PI': 'PublisherCity', 'PA': 'PublisherAddress',
            'RP': 'ReprintAddress', 'EM': 'EmailAddresses', 'RI': 'ResearcherID',
            'OI': 'ORCID', 'WC': 'WebOfScienceCategory', 'SC': 'SubjectCategory',
            'LA': 'Language', 'DT': 'DocumentType', 'PT': 'PublicationType',
            'UT': 'AccessionNumber', 'PM': 'PubMedID', 'AR': 'ArticleNumber',
            'PG': 'PageCount', 'PD': 'PublicationDate', 'FU': 'FundingAgency',
            'FX': 'FundingText', 'U1': 'UsageCount180', 'U2': 'UsageCountSince2013',
            'CT': 'ConferenceTitle', 'CY': 'ConferenceDate', 'CL': 'ConferenceLocation',
            'HO': 'ConferenceHost', 'BN': 'ISBN', 'BA': 'BookAuthors', 'BE': 'Editors',
            'TA': 'BookTitle', 'DA': 'DateAdded', 'OA': 'OpenAccess', 'HC': 'HighlyCited',
            'HP': 'HotPaper', 'GA': 'DocumentDeliveryNumber', 'SE': 'Series',
            'SI': 'SpecialIssue', 'WE': 'WebOfScienceEdition'
        }
    
    def parse_wos_file(self, file_content: str) -> Tuple[str, str, pd.DataFrame]:
        """
        解析WOS文件内容
        
        Args:
            file_content: WOS文件内容字符串
            
        Returns:
            Tuple[str, str, pd.DataFrame]: (文件名, 版本, 数据框)
        """
        try:
            # 解析文件头和版本信息
            filename = "Unknown"
            version = "Unknown"
            
            lines = file_content.split('\n')
            for line in lines[:10]:  # 只检查前10行
                if line.startswith('FN '):
                    filename = line[3:].strip()
                elif line.startswith('VR '):
                    version = line[3:].strip()
            
            # 解析记录
            records = []
            current_record = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 检查记录分隔符
                if line == 'ER':
                    if current_record:
                        records.append(current_record)
                        current_record = {}
                    continue
                elif line == 'EF':
                    if current_record:
                        records.append(current_record)
                    break
                
                # 解析字段
                if len(line) >= 3 and line[2] == ' ':
                    field_code = line[:2]
                    field_value = line[3:].strip()
                    
                    if field_code in self.valid_fields:
                        if field_code in current_record:
                            current_record[field_code] += '; ' + field_value
                        else:
                            current_record[field_code] = field_value
            
            if not records:
                st.warning("未找到有效的文献记录")
                return filename, version, pd.DataFrame()
            
            # 转换为DataFrame
            df = pd.DataFrame(records)
            
            # 重命名列
            for old_col, new_col in self.field_mapping.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            # 合并相同功能的列
            if 'AF' in df.columns and 'Authors' in df.columns:
                df['Authors'] = df['Authors'].fillna('') + ';' + df['AF'].fillna('')
                df = df.drop(columns=['AF'])
            elif 'AF' in df.columns:
                df = df.rename(columns={'AF': 'Authors'})
            
            # 处理重复的Authors列
            if df.columns.duplicated().any():
                authors_cols = [col for col in df.columns if col == 'Authors']
                if len(authors_cols) > 1:
                    df['Authors'] = df[authors_cols].apply(lambda x: ';'.join(x.dropna().astype(str)), axis=1)
                    df = df.loc[:, ~df.columns.duplicated()]
            
            # 数据类型转换
            if 'Year' in df.columns:
                df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
                df = df.dropna(subset=['Year'])
            
            if 'TimesCited' in df.columns:
                df['TimesCited'] = pd.to_numeric(df['TimesCited'], errors='coerce').fillna(0)
            
            return filename, version, df
            
        except Exception as e:
            st.error(f"WOS文件解析失败: {str(e)}")
            return filename, version, pd.DataFrame()

def load_wos_file_enhanced(uploaded_file) -> pd.DataFrame:
    """
    使用增强解析器加载WOS文件
    
    Args:
        uploaded_file: Streamlit上传的文件对象
        
    Returns:
        pd.DataFrame: 解析后的数据框
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
        
        # 使用增强解析器
        parser = EnhancedWOSParser()
        filename, version, df = parser.parse_wos_file(data)
        
        if not df.empty:
            st.info(f"✅ 成功解析 {len(df)} 条文献记录")
            st.info(f"📋 识别到字段: {', '.join(df.columns.tolist())}")
        
        return df
        
    except Exception as e:
        st.error(f"增强WOS文件解析失败: {str(e)}")
        return pd.DataFrame()

def get_wos_field_documentation() -> dict:
    """
    获取WOS字段文档
    
    Returns:
        dict: 字段文档字典
    """
    return {
        'basic_fields': {
            'FN': '文件名',
            'VR': '版本号',
            'PT': '出版物类型',
            'UT': '入藏号',
            'AR': '文章编号'
        },
        'author_fields': {
            'AU': '作者',
            'AF': '作者全名',
            'BA': '书籍作者',
            'BF': '书籍作者全名',
            'CA': '团体作者',
            'GP': '团体作者全名',
            'RI': '研究员ID',
            'OI': 'ORCID标识符'
        },
        'content_fields': {
            'TI': '文献标题',
            'AB': '摘要',
            'MA': '会议摘要'
        },
        'journal_fields': {
            'SO': '期刊名称',
            'J9': '期刊缩写',
            'JI': 'ISO期刊缩写',
            'SN': 'ISSN',
            'EI': 'eISSN',
            'BN': 'ISBN'
        },
        'publication_fields': {
            'PY': '出版年',
            'PD': '发表日期',
            'VL': '卷',
            'IS': '期',
            'BP': '起始页',
            'EP': '结束页',
            'PG': '页数',
            'DI': 'DOI',
            'D2': '书籍DOI'
        },
        'publisher_fields': {
            'PU': '出版商',
            'PI': '出版商城市',
            'PA': '出版商地址',
            'PN': '部分号'
        },
        'subject_fields': {
            'DE': '关键词',
            'ID': '扩展关键词',
            'WC': 'Web of Science分类',
            'SC': '学科分类'
        },
        'address_fields': {
            'C1': '作者地址',
            'RP': '重印地址',
            'EM': '邮箱地址'
        },
        'conference_fields': {
            'CT': '会议标题',
            'CY': '会议日期',
            'CL': '会议地点',
            'HO': '会议主办方',
            'SP': '会议赞助商'
        },
        'citation_fields': {
            'CR': '参考文献',
            'NR': '参考文献数量',
            'TC': '被引次数',
            'Z9': '总被引次数',
            'U1': '180天使用次数',
            'U2': '2013年以来使用次数'
        },
        'funding_fields': {
            'FU': '资助机构',
            'FX': '资助文本'
        },
        'other_fields': {
            'LA': '语言',
            'DT': '文档类型',
            'OA': '开放获取',
            'PM': 'PubMed ID',
            'GA': '文档传递号',
            'SE': '系列',
            'SI': '特刊',
            'DA': '添加日期',
            'EA': '提前访问日期',
            'EY': '提前访问年',
            'ES': '提前访问月',
            'ET': '提前访问日',
            'WE': 'Web of Science版本'
        }
    }

