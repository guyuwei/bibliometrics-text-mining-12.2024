"""
数据验证模块
用于验证输入数据的完整性和格式正确性
"""

import pandas as pd
import streamlit as st
from typing import Dict, List, Tuple, Optional
import re

class DataValidator:
    """数据验证器类"""
    
    def __init__(self):
        self.required_columns = {
            'basic': ['Authors', 'Titles'],
            'publication': ['出版年', 'PY', 'Year', 'Publication Year'],
            'citation': ['核心合集的被引频次计数', 'Times Cited', 'Cited Reference Count', 'TC', 'Z9'],
            'keyword': ['关键词', 'DE', 'Keywords', 'Keyword', 'ID', '主题词', '作者关键词'],
            'source': ['期刊名称', 'Source', 'Journal', 'Publication Name', '出版物名称', 'SO', 'J9'],
            'country': ['国家', 'Country', 'C1', '作者地址', 'Address', 'Addresses'],
            'author_detail': ['作者', 'Authors', 'Author Names']
        }
        
        self.column_aliases = {
            'Authors': ['作者', 'Author', 'Author Names'],
            'Titles': ['标题', 'Title', 'Article Title', '文献标题', 'TI', 'Document Title'],
            '出版年': ['PY', 'Year', 'Publication Year', '年份'],
            '核心合集的被引频次计数': ['Times Cited', 'Cited Reference Count', '被引频次', 'TC', 'Z9'],
            '关键词': ['DE', 'Keywords', 'Keyword', 'ID', '主题词', '作者关键词'],
            '期刊名称': ['Source', 'Journal', 'Publication Name', '出版物名称', 'SO', 'J9'],
            '国家': ['Country', 'C1', '作者地址', 'Address', 'Addresses']
        }
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict:
        """
        验证DataFrame的完整性和格式
        
        参数:
        - df: 要验证的DataFrame
        
        返回:
        - 验证结果字典
        """
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'missing_columns': {},
            'data_quality': {},
            'suggestions': []
        }
        
        if df is None or df.empty:
            validation_result['is_valid'] = False
            validation_result['errors'].append("数据框为空或未定义")
            return validation_result
        
        # 检查基本列
        basic_validation = self._check_basic_columns(df)
        validation_result.update(basic_validation)
        
        # 检查数据质量
        quality_validation = self._check_data_quality(df)
        validation_result['data_quality'] = quality_validation
        
        # 检查缺失列
        missing_columns = self._check_missing_columns(df)
        validation_result['missing_columns'] = missing_columns
        
        # 生成建议
        suggestions = self._generate_suggestions(df, missing_columns)
        validation_result['suggestions'] = suggestions
        
        return validation_result
    
    def _check_basic_columns(self, df: pd.DataFrame) -> Dict:
        """检查基本必需列"""
        result = {'is_valid': True, 'warnings': [], 'errors': []}
        
        # 检查是否有任何作者列
        author_columns = self._find_columns(df, self.required_columns['basic'][0])
        if not author_columns:
            result['is_valid'] = False
            result['errors'].append("缺少作者信息列")
        
        # 检查是否有任何标题列
        title_columns = self._find_columns(df, self.required_columns['basic'][1])
        if not title_columns:
            result['is_valid'] = False
            result['errors'].append("缺少标题信息列")
        
        return result
    
    def _check_data_quality(self, df: pd.DataFrame) -> Dict:
        """检查数据质量"""
        quality = {
            'total_records': len(df),
            'empty_records': 0,
            'duplicate_records': 0,
            'data_completeness': 0,
            'column_completeness': {}
        }
        
        # 计算空记录
        quality['empty_records'] = df.isnull().all(axis=1).sum()
        
        # 计算重复记录
        quality['duplicate_records'] = df.duplicated().sum()
        
        # 计算数据完整性
        total_cells = df.size
        non_null_cells = df.count().sum()
        quality['data_completeness'] = (non_null_cells / total_cells * 100) if total_cells > 0 else 0
        
        # 计算每列完整性
        for col in df.columns:
            non_null_count = df[col].count()
            quality['column_completeness'][col] = (non_null_count / len(df) * 100) if len(df) > 0 else 0
        
        return quality
    
    def _check_missing_columns(self, df: pd.DataFrame) -> Dict:
        """检查缺失的功能列"""
        missing = {}
        
        for category, columns in self.required_columns.items():
            if category == 'basic':
                continue
                
            found_columns = []
            for col in columns:
                if col in df.columns:
                    found_columns.append(col)
            
            if not found_columns:
                missing[category] = columns
        
        return missing
    
    def _find_columns(self, df: pd.DataFrame, target_column: str) -> List[str]:
        """查找可能的列名"""
        found_columns = []
        
        # 直接匹配
        if target_column in df.columns:
            found_columns.append(target_column)
        
        # 别名匹配
        if target_column in self.column_aliases:
            for alias in self.column_aliases[target_column]:
                if alias in df.columns:
                    found_columns.append(alias)
        
        return found_columns
    
    def _generate_suggestions(self, df: pd.DataFrame, missing_columns: Dict) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if missing_columns:
            suggestions.append("建议添加以下列以启用完整功能：")
            for category, columns in missing_columns.items():
                suggestions.append(f"  - {category}: {', '.join(columns[:3])}{'...' if len(columns) > 3 else ''}")
        
        # 数据质量建议
        quality = self._check_data_quality(df)
        if quality['data_completeness'] < 80:
            suggestions.append(f"数据完整性较低 ({quality['data_completeness']:.1f}%)，建议检查数据源")
        
        if quality['duplicate_records'] > 0:
            suggestions.append(f"发现 {quality['duplicate_records']} 条重复记录，建议清理数据")
        
        return suggestions
    
    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化列名"""
        df_standardized = df.copy()
        
        # 创建列名映射
        column_mapping = {}
        for standard_name, aliases in self.column_aliases.items():
            for alias in aliases:
                if alias in df_standardized.columns:
                    column_mapping[alias] = standard_name
                    break
        
        # 重命名列
        df_standardized = df_standardized.rename(columns=column_mapping)
        
        return df_standardized
    
    def validate_calculation_input(self, df: pd.DataFrame, calculation_type: str) -> Tuple[bool, str]:
        """
        验证特定计算类型的输入数据
        
        参数:
        - df: 数据框
        - calculation_type: 计算类型 ('author', 'publication', 'citation', 'keyword', 'source')
        
        返回:
        - (是否有效, 错误信息)
        """
        if df is None or df.empty:
            return False, "数据框为空"
        
        required_cols = {
            'author': ['Authors'],
            'publication': ['出版年'],
            'citation': ['核心合集的被引频次计数'],
            'keyword': ['作者关键词'],
            'source': ['出版物名称']
        }
        
        if calculation_type not in required_cols:
            return False, f"未知的计算类型: {calculation_type}"
        
        missing_cols = []
        for col in required_cols[calculation_type]:
            if col not in df.columns:
                missing_cols.append(col)
        
        if missing_cols:
            return False, f"缺少必需列: {', '.join(missing_cols)}"
        
        return True, ""

def validate_and_display_data_info(df: pd.DataFrame, calculation_type: str = None) -> bool:
    """
    验证数据（静默验证，不显示信息）
    
    参数:
    - df: 数据框
    - calculation_type: 计算类型
    
    返回:
    - 是否验证通过
    """
    validator = DataValidator()
    validation_result = validator.validate_dataframe(df)
    
    # 静默验证，不显示任何信息
    # 如果有缺失列，返回False但继续处理
    if validation_result['missing_columns']:
        return False
    
    return True
