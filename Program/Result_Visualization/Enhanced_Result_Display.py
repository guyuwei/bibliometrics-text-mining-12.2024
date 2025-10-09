"""
增强的结果展示模块
改进空数据情况的处理和结果展示
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Union
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class EnhancedResultDisplay:
    """增强的结果展示类"""
    
    def __init__(self):
        self.empty_data_messages = {
            'author': "未找到作者数据，请检查数据中是否包含作者信息列",
            'publication': "未找到出版物数据，请检查数据中是否包含年份信息列",
            'citation': "未找到引用数据，请检查数据中是否包含引用信息列",
            'keyword': "未找到关键词数据，请检查数据中是否包含关键词信息列",
            'source': "未找到来源数据，请检查数据中是否包含来源信息列",
            'network': "未找到网络数据，请检查数据中是否包含合作信息",
            'general': "未找到相关数据，请检查数据格式和列名"
        }
    
    def display_calculation_result(self, result: Any, result_type: str, title: str = None) -> bool:
        """
        显示计算结果
        
        参数:
        - result: 计算结果
        - result_type: 结果类型
        - title: 显示标题
        
        返回:
        - 是否有有效结果
        """
        if title:
            st.subheader(title)
        
        # 检查结果是否为空
        if self._is_empty_result(result):
            self._display_empty_result_message(result_type)
            return False
        
        # 根据结果类型显示
        if isinstance(result, pd.DataFrame):
            return self._display_dataframe_result(result, result_type)
        elif isinstance(result, dict):
            return self._display_dict_result(result, result_type)
        elif isinstance(result, (list, tuple)):
            return self._display_list_result(result, result_type)
        elif isinstance(result, (int, float)):
            return self._display_numeric_result(result, result_type)
        else:
            st.write(result)
            return True
    
    def _is_empty_result(self, result: Any) -> bool:
        """检查结果是否为空"""
        if result is None:
            return True
        elif isinstance(result, pd.DataFrame):
            return result.empty
        elif isinstance(result, dict):
            return len(result) == 0
        elif isinstance(result, (list, tuple)):
            return len(result) == 0
        elif isinstance(result, (int, float)):
            return pd.isna(result) or result == 0
        return False
    
    def _display_empty_result_message(self, result_type: str):
        """显示空结果消息"""
        message = self.empty_data_messages.get(result_type, self.empty_data_messages['general'])
        
        st.info(f"ℹ️ {message}")
        
        # 提供解决建议
        with st.expander("💡 解决方案", expanded=False):
            st.markdown("""
            **可能的解决方案：**
            1. 检查上传的文件格式是否正确
            2. 确认文件包含必要的列名
            3. 尝试重新上传文件
            4. 检查数据是否完整
            """)
    
    def _display_dataframe_result(self, df: pd.DataFrame, result_type: str) -> bool:
        """显示DataFrame结果"""
        if df.empty:
            self._display_empty_result_message(result_type)
            return False
        
        # 显示基本信息
        st.write(f"📊 共找到 {len(df)} 条记录")
        
        # 显示表格
        st.dataframe(df, use_container_width=True)
        
        # 如果是作者数据，显示统计信息
        if result_type == 'author' and 'Authors' in df.columns:
            self._display_author_statistics(df)
        
        return True
    
    def _display_dict_result(self, result: Dict, result_type: str) -> bool:
        """显示字典结果"""
        if not result:
            self._display_empty_result_message(result_type)
            return False
        
        # 特殊处理Price定律结果
        if 'price_law_satisfied' in result:
            self._display_price_law_result(result)
            return True
        
        # 特殊处理合作分析结果
        if 'collaboration_rate' in result:
            self._display_collaboration_result(result)
            return True
        
        # 一般字典结果
        for key, value in result.items():
            if isinstance(value, (int, float)):
                st.metric(key, value)
            else:
                st.write(f"**{key}**: {value}")
        
        return True
    
    def _display_list_result(self, result: List, result_type: str) -> bool:
        """显示列表结果"""
        if not result:
            self._display_empty_result_message(result_type)
            return False
        
        # 如果是元组，可能是年份和数量
        if isinstance(result, tuple) and len(result) == 2:
            years, counts = result
            if years and counts:
                self._display_time_series_data(years, counts, result_type)
                return True
        
        # 一般列表结果
        st.write(f"📋 共找到 {len(result)} 项")
        for i, item in enumerate(result[:10], 1):  # 只显示前10项
            st.write(f"{i}. {item}")
        
        if len(result) > 10:
            st.write(f"... 还有 {len(result) - 10} 项")
        
        return True
    
    def _display_numeric_result(self, result: Union[int, float], result_type: str) -> bool:
        """显示数值结果"""
        if pd.isna(result) or result == 0:
            self._display_empty_result_message(result_type)
            return False
        
        st.metric("结果", f"{result:,}")
        return True
    
    def _display_author_statistics(self, df: pd.DataFrame):
        """显示作者统计信息"""
        if 'Authors' in df.columns:
            author_counts = df['Authors'].value_counts()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总作者数", len(author_counts))
            with col2:
                st.metric("最高产作者", author_counts.index[0] if len(author_counts) > 0 else "N/A")
            with col3:
                st.metric("最高产作者发文数", author_counts.iloc[0] if len(author_counts) > 0 else 0)
    
    def _display_price_law_result(self, result: Dict):
        """显示Price定律结果"""
        st.subheader("📈 Price定律验证结果")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "核心作者数", 
                result.get('core_authors_actual', 0),
                delta=f"预期: {result.get('core_authors_expected', 0):.1f}"
            )
        
        with col2:
            st.metric(
                "核心作者贡献率", 
                f"{result.get('core_percentage', 0):.1f}%",
                delta=f"偏差: {result.get('price_law_deviation', 0):.1f}%"
            )
        
        with col3:
            status = "✅ 满足" if result.get('price_law_satisfied', False) else "❌ 不满足"
            st.metric("Price定律", status)
        
        # 显示高产作者
        if 'top_authors' in result and result['top_authors']:
            st.subheader("🏆 高产作者排名")
            top_authors_df = pd.DataFrame(result['top_authors'][:10], columns=['作者', '发文数'])
            st.dataframe(top_authors_df, use_container_width=True)
    
    def _display_collaboration_result(self, result: Dict):
        """显示合作分析结果"""
        st.subheader("🤝 合作分析结果")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("合作率", f"{result.get('collaboration_rate', 0):.1f}%")
        
        with col2:
            st.metric("平均作者数", f"{result.get('average_authors_per_paper', 0):.1f}")
        
        with col3:
            st.metric("多作者论文", f"{result.get('multi_author_papers', 0)}篇")
    
    def _display_time_series_data(self, years: List, counts: List, result_type: str):
        """显示时间序列数据"""
        if not years or not counts:
            self._display_empty_result_message(result_type)
            return
        
        # 创建时间序列图
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years,
            y=counts,
            mode='lines+markers',
            name='数量',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title=f"{result_type} 时间趋势",
            xaxis_title="年份",
            yaxis_title="数量",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示统计信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总数量", sum(counts))
        with col2:
            st.metric("峰值年份", years[counts.index(max(counts))] if counts else "N/A")
        with col3:
            st.metric("峰值数量", max(counts) if counts else 0)
    
    def display_calculation_summary(self, results: Dict[str, Any]):
        """显示计算摘要"""
        st.subheader("📊 计算摘要")
        
        summary_data = []
        for calc_type, result in results.items():
            if self._is_empty_result(result):
                status = "❌ 无数据"
            else:
                status = "✅ 完成"
            
            summary_data.append({
                "计算类型": calc_type,
                "状态": status,
                "结果": self._get_result_summary(result)
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
    
    def _get_result_summary(self, result: Any) -> str:
        """获取结果摘要"""
        if self._is_empty_result(result):
            return "无数据"
        elif isinstance(result, pd.DataFrame):
            return f"{len(result)} 条记录"
        elif isinstance(result, dict):
            return f"{len(result)} 个指标"
        elif isinstance(result, (list, tuple)):
            return f"{len(result)} 项"
        elif isinstance(result, (int, float)):
            return f"{result:,}"
        else:
            return "已计算"

def display_enhanced_result(result: Any, result_type: str, title: str = None) -> bool:
    """便捷函数：显示增强结果"""
    displayer = EnhancedResultDisplay()
    return displayer.display_calculation_result(result, result_type, title)

