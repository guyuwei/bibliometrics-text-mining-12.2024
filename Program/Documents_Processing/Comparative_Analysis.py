"""
Comparative Bibliometric Analysis Framework
用于多个研究领域的对比分析
支持双领域对比和多维度指标比较
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import re
import math
from scipy import stats

from Documents_Processing.Enhanced_Report_Generator import EnhancedBibliometricReportGenerator
from Calculate_Anaysis.Calculate_Burst_Analysis import BurstDetectionAnalyzer

class ComparativeBibliometricAnalyzer:
    """
    双领域对比分析器
    支持两个研究领域的全面对比分析
    """
    
    def __init__(self, df1, field1_name, df2=None, field2_name=None):
        """
        初始化对比分析器
        
        参数:
        - df1: 第一个数据集
        - field1_name: 第一个研究领域名称
        - df2: 第二个数据集（可选，用于双领域对比）
        - field2_name: 第二个研究领域名称（可选）
        """
        self.df1 = df1
        self.field1_name = field1_name
        self.df2 = df2 if df2 is not None else df1
        self.field2_name = field2_name if field2_name else f"{field1_name}_subset"
        
        # 创建报告生成器
        self.generator1 = EnhancedBibliometricReportGenerator(df1, field1_name)
        self.generator2 = EnhancedBibliometricReportGenerator(self.df2, self.field2_name)
        
        # 创建突现分析器
        self.burst_analyzer = BurstDetectionAnalyzer()
        
        # 计算对比指标
        self.comparative_metrics = self._calculate_comparative_metrics()
    
    def _calculate_comparative_metrics(self):
        """计算对比指标"""
        try:
            metrics = {
                'field1': {
                    'name': self.field1_name,
                    'publications': self.generator1.total_articles,
                    'growth_rate': self.generator1.annual_data.get('growth_rate', 0),
                    'trend': self.generator1.annual_data.get('trend', 'unknown'),
                    'authors': len(set(self.generator1.authors)),
                    'core_authors': self.generator1.core_authors_data.get('core_authors_actual', 0),
                    'price_law': self.generator1.core_authors_data.get('price_law_satisfied', False),
                    'core_percentage': self.generator1.core_authors_data.get('core_percentage', 0),
                    'h_index_max': self.generator1.h_index_data.get('max_author_h_index', 0),
                    'countries': self.generator1.collaboration_data.get('unique_countries', 0),
                    'collaboration_rate': self.generator1.collaboration_data.get('international_collaboration_rate', 0),
                    'burst_keywords': len(self.generator1.burst_keywords),
                    'time_span': len(set(self.generator1.years)) if self.generator1.years else 0,
                    'keywords': len(set(self.generator1.keywords)),
                    'journals': len(set(self.generator1.journals))
                },
                'field2': {
                    'name': self.field2_name,
                    'publications': self.generator2.total_articles,
                    'growth_rate': self.generator2.annual_data.get('growth_rate', 0),
                    'trend': self.generator2.annual_data.get('trend', 'unknown'),
                    'authors': len(set(self.generator2.authors)),
                    'core_authors': self.generator2.core_authors_data.get('core_authors_actual', 0),
                    'price_law': self.generator2.core_authors_data.get('price_law_satisfied', False),
                    'core_percentage': self.generator2.core_authors_data.get('core_percentage', 0),
                    'h_index_max': self.generator2.h_index_data.get('max_author_h_index', 0),
                    'countries': self.generator2.collaboration_data.get('unique_countries', 0),
                    'collaboration_rate': self.generator2.collaboration_data.get('international_collaboration_rate', 0),
                    'burst_keywords': len(self.generator2.burst_keywords),
                    'time_span': len(set(self.generator2.years)) if self.generator2.years else 0,
                    'keywords': len(set(self.generator2.keywords)),
                    'journals': len(set(self.generator2.journals))
                }
            }
            
            # 计算对比比率
            metrics['comparison'] = self._calculate_comparison_ratios(metrics['field1'], metrics['field2'])
            
            return metrics
            
        except Exception as e:
            st.error(f"对比指标计算失败: {str(e)}")
            return {}
    
    def _calculate_comparison_ratios(self, field1_metrics, field2_metrics):
        """计算对比比率"""
        comparison = {}
        
        for key in ['publications', 'growth_rate', 'authors', 'core_authors', 
                   'core_percentage', 'h_index_max', 'countries', 'collaboration_rate',
                   'burst_keywords', 'time_span', 'keywords', 'journals']:
            
            val1 = field1_metrics.get(key, 0)
            val2 = field2_metrics.get(key, 0)
            
            if val2 != 0:
                ratio = val1 / val2
                comparison[f'{key}_ratio'] = round(ratio, 2)
                comparison[f'{key}_advantage'] = self.field1_name if ratio > 1 else self.field2_name
                comparison[f'{key}_difference'] = abs(val1 - val2)
            else:
                comparison[f'{key}_ratio'] = float('inf') if val1 > 0 else 1
                comparison[f'{key}_advantage'] = self.field1_name if val1 > 0 else 'Equal'
                comparison[f'{key}_difference'] = val1
        
        return comparison
    
    def generate_comparative_visualizations(self):
        """生成对比可视化图表"""
        try:
            metrics = self.comparative_metrics
            
            if not metrics:
                return None
            
            # 创建子图
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[
                    'Publications & Growth Rate',
                    'Author Metrics Comparison',
                    'International Collaboration',
                    'Research Diversity'
                ],
                specs=[[{"secondary_y": True}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "radar"}]]
            )
            
            # 图1: 发文量和增长率对比
            fig.add_trace(
                go.Bar(
                    name='Publications',
                    x=[metrics['field1']['name'], metrics['field2']['name']],
                    y=[metrics['field1']['publications'], metrics['field2']['publications']],
                    yaxis='y',
                    marker_color=['#3498db', '#e74c3c']
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    name='Growth Rate (%)',
                    x=[metrics['field1']['name'], metrics['field2']['name']],
                    y=[metrics['field1']['growth_rate'], metrics['field2']['growth_rate']],
                    yaxis='y2',
                    mode='lines+markers',
                    line=dict(color='orange', width=3),
                    marker=dict(size=10)
                ),
                row=1, col=1, secondary_y=True
            )
            
            # 图2: 作者指标对比
            author_metrics = ['authors', 'core_authors', 'h_index_max']
            field1_values = [metrics['field1'][metric] for metric in author_metrics]
            field2_values = [metrics['field2'][metric] for metric in author_metrics]
            
            fig.add_trace(
                go.Bar(
                    name=metrics['field1']['name'],
                    x=['Total Authors', 'Core Authors', 'Max H-Index'],
                    y=field1_values,
                    marker_color='#3498db'
                ),
                row=1, col=2
            )
            
            fig.add_trace(
                go.Bar(
                    name=metrics['field2']['name'],
                    x=['Total Authors', 'Core Authors', 'Max H-Index'],
                    y=field2_values,
                    marker_color='#e74c3c'
                ),
                row=1, col=2
            )
            
            # 图3: 国际合作散点图
            fig.add_trace(
                go.Scatter(
                    x=[metrics['field1']['countries'], metrics['field2']['countries']],
                    y=[metrics['field1']['collaboration_rate'], metrics['field2']['collaboration_rate']],
                    mode='markers+text',
                    text=[metrics['field1']['name'], metrics['field2']['name']],
                    textposition="top center",
                    marker=dict(size=[20, 20], color=['#3498db', '#e74c3c']),
                    name='Collaboration Pattern'
                ),
                row=2, col=1
            )
            
            # 图4: 雷达图 - 研究多样性
            categories = ['Publications', 'Authors', 'Countries', 'Keywords', 'Journals', 'Burst Terms']
            
            # 标准化数据 (0-100 scale)
            field1_radar = [
                min(100, metrics['field1']['publications'] / 10),
                min(100, metrics['field1']['authors'] / 5),
                min(100, metrics['field1']['countries'] * 4),
                min(100, metrics['field1']['keywords'] / 20),
                min(100, metrics['field1']['journals'] * 2),
                min(100, metrics['field1']['burst_keywords'] * 5)
            ]
            
            field2_radar = [
                min(100, metrics['field2']['publications'] / 10),
                min(100, metrics['field2']['authors'] / 5),
                min(100, metrics['field2']['countries'] * 4),
                min(100, metrics['field2']['keywords'] / 20),
                min(100, metrics['field2']['journals'] * 2),
                min(100, metrics['field2']['burst_keywords'] * 5)
            ]
            
            fig.add_trace(
                go.Scatterpolar(
                    r=field1_radar,
                    theta=categories,
                    fill='toself',
                    name=metrics['field1']['name'],
                    line_color='#3498db'
                ),
                row=2, col=2
            )
            
            fig.add_trace(
                go.Scatterpolar(
                    r=field2_radar,
                    theta=categories,
                    fill='toself',
                    name=metrics['field2']['name'],
                    line_color='#e74c3c'
                ),
                row=2, col=2
            )
            
            # 更新布局
            fig.update_layout(
                title_text=f"Comparative Analysis: {metrics['field1']['name']} vs {metrics['field2']['name']}",
                showlegend=True,
                height=800,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            st.error(f"可视化生成失败: {str(e)}")
            return None
    
    def generate_comparative_report(self):
        """生成对比分析报告"""
        try:
            metrics = self.comparative_metrics
            comparison = metrics.get('comparison', {})
            
            report = f"""
# Comparative Bibliometric Analysis: {metrics['field1']['name']} vs {metrics['field2']['name']}

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Executive Summary

This comparative analysis examines the bibliometric characteristics of two research domains: **{metrics['field1']['name']}** and **{metrics['field2']['name']}**. The analysis reveals distinct patterns in publication productivity, collaboration networks, and thematic evolution.

## Key Comparative Findings

### 📊 Publication Metrics Comparison

| Metric | {metrics['field1']['name']} | {metrics['field2']['name']} | Ratio | Advantage |
|--------|------------|------------|-------|-----------|
| **Total Publications** | {metrics['field1']['publications']:,} | {metrics['field2']['publications']:,} | {comparison.get('publications_ratio', 1):.2f} | {comparison.get('publications_advantage', 'Equal')} |
| **Annual Growth Rate** | {metrics['field1']['growth_rate']:.2f}% | {metrics['field2']['growth_rate']:.2f}% | {comparison.get('growth_rate_ratio', 1):.2f} | {comparison.get('growth_rate_advantage', 'Equal')} |
| **Growth Pattern** | {metrics['field1']['trend'].replace('_', ' ').title()} | {metrics['field2']['trend'].replace('_', ' ').title()} | - | {'Field 1' if metrics['field1']['trend'] == 'exponential' else 'Field 2' if metrics['field2']['trend'] == 'exponential' else 'Similar'} |

### 👥 Author & Collaboration Analysis

| Metric | {metrics['field1']['name']} | {metrics['field2']['name']} | Ratio | Advantage |
|--------|------------|------------|-------|-----------|
| **Total Authors** | {metrics['field1']['authors']:,} | {metrics['field2']['authors']:,} | {comparison.get('authors_ratio', 1):.2f} | {comparison.get('authors_advantage', 'Equal')} |
| **Core Authors** | {metrics['field1']['core_authors']} | {metrics['field2']['core_authors']} | {comparison.get('core_authors_ratio', 1):.2f} | {comparison.get('core_authors_advantage', 'Equal')} |
| **Price's Law** | {'✓ Validated' if metrics['field1']['price_law'] else '✗ Not Met'} | {'✓ Validated' if metrics['field2']['price_law'] else '✗ Not Met'} | - | {'Field 1' if metrics['field1']['price_law'] and not metrics['field2']['price_law'] else 'Field 2' if metrics['field2']['price_law'] and not metrics['field1']['price_law'] else 'Equal'} |
| **Core Output %** | {metrics['field1']['core_percentage']:.1f}% | {metrics['field2']['core_percentage']:.1f}% | {comparison.get('core_percentage_ratio', 1):.2f} | {comparison.get('core_percentage_advantage', 'Equal')} |
| **Max H-Index** | {metrics['field1']['h_index_max']} | {metrics['field2']['h_index_max']} | {comparison.get('h_index_max_ratio', 1):.2f} | {comparison.get('h_index_max_advantage', 'Equal')} |

### 🌍 Geographic & Collaboration Patterns

| Metric | {metrics['field1']['name']} | {metrics['field2']['name']} | Ratio | Advantage |
|--------|------------|------------|-------|-----------|
| **Contributing Countries** | {metrics['field1']['countries']} | {metrics['field2']['countries']} | {comparison.get('countries_ratio', 1):.2f} | {comparison.get('countries_advantage', 'Equal')} |
| **Collaboration Rate** | {metrics['field1']['collaboration_rate']:.1f}% | {metrics['field2']['collaboration_rate']:.1f}% | {comparison.get('collaboration_rate_ratio', 1):.2f} | {comparison.get('collaboration_rate_advantage', 'Equal')} |
| **Global Reach** | {'High' if metrics['field1']['countries'] > 20 else 'Medium' if metrics['field1']['countries'] > 10 else 'Limited'} | {'High' if metrics['field2']['countries'] > 20 else 'Medium' if metrics['field2']['countries'] > 10 else 'Limited'} | - | {'Field 1' if metrics['field1']['countries'] > metrics['field2']['countries'] else 'Field 2' if metrics['field2']['countries'] > metrics['field1']['countries'] else 'Equal'} |

### 🔍 Research Diversity & Innovation

| Metric | {metrics['field1']['name']} | {metrics['field2']['name']} | Ratio | Advantage |
|--------|------------|------------|-------|-----------|
| **Unique Keywords** | {metrics['field1']['keywords']:,} | {metrics['field2']['keywords']:,} | {comparison.get('keywords_ratio', 1):.2f} | {comparison.get('keywords_advantage', 'Equal')} |
| **Publication Venues** | {metrics['field1']['journals']} | {metrics['field2']['journals']} | {comparison.get('journals_ratio', 1):.2f} | {comparison.get('journals_advantage', 'Equal')} |
| **Burst Keywords** | {metrics['field1']['burst_keywords']} | {metrics['field2']['burst_keywords']} | {comparison.get('burst_keywords_ratio', 1):.2f} | {comparison.get('burst_keywords_advantage', 'Equal')} |
| **Research Span** | {metrics['field1']['time_span']} years | {metrics['field2']['time_span']} years | {comparison.get('time_span_ratio', 1):.2f} | {comparison.get('time_span_advantage', 'Equal')} |

## Detailed Analysis

### 🚀 Field Maturity Assessment

**{metrics['field1']['name']}:**
- **Maturity Level**: {'Mature' if metrics['field1']['publications'] > 500 else 'Developing' if metrics['field1']['publications'] > 100 else 'Emerging'}
- **Growth Dynamics**: {metrics['field1']['trend'].replace('_', ' ').title()} pattern with {metrics['field1']['growth_rate']:.1f}% annual growth
- **Research Concentration**: {'High' if metrics['field1']['core_percentage'] > 60 else 'Medium' if metrics['field1']['core_percentage'] > 40 else 'Low'} (Price's Law: {'Validated' if metrics['field1']['price_law'] else 'Not validated'})
- **Global Integration**: {'Strong' if metrics['field1']['collaboration_rate'] > 30 else 'Moderate' if metrics['field1']['collaboration_rate'] > 15 else 'Limited'} international collaboration

**{metrics['field2']['name']}:**
- **Maturity Level**: {'Mature' if metrics['field2']['publications'] > 500 else 'Developing' if metrics['field2']['publications'] > 100 else 'Emerging'}
- **Growth Dynamics**: {metrics['field2']['trend'].replace('_', ' ').title()} pattern with {metrics['field2']['growth_rate']:.1f}% annual growth
- **Research Concentration**: {'High' if metrics['field2']['core_percentage'] > 60 else 'Medium' if metrics['field2']['core_percentage'] > 40 else 'Low'} (Price's Law: {'Validated' if metrics['field2']['price_law'] else 'Not validated'})
- **Global Integration**: {'Strong' if metrics['field2']['collaboration_rate'] > 30 else 'Moderate' if metrics['field2']['collaboration_rate'] > 15 else 'Limited'} international collaboration

### 📈 Comparative Insights

1. **Publication Volume**: {metrics['field1']['name']} {'leads with' if metrics['field1']['publications'] > metrics['field2']['publications'] else 'trails with'} {abs(metrics['field1']['publications'] - metrics['field2']['publications']):,} {'more' if metrics['field1']['publications'] > metrics['field2']['publications'] else 'fewer'} publications

2. **Growth Trajectory**: {'Both fields show similar growth patterns' if abs(metrics['field1']['growth_rate'] - metrics['field2']['growth_rate']) < 2 else f"{metrics['field1']['name'] if metrics['field1']['growth_rate'] > metrics['field2']['growth_rate'] else metrics['field2']['name']} demonstrates superior growth dynamics"}

3. **Research Community**: {comparison.get('authors_advantage', 'Both fields')} {'has a larger research community' if comparison.get('authors_advantage') != 'Equal' else 'have similar-sized research communities'}

4. **International Reach**: {comparison.get('collaboration_rate_advantage', 'Both fields')} {'shows stronger international collaboration' if comparison.get('collaboration_rate_advantage') != 'Equal' else 'demonstrate similar collaboration patterns'}

5. **Innovation Indicators**: {comparison.get('burst_keywords_advantage', 'Both fields')} {'exhibits more dynamic thematic evolution' if comparison.get('burst_keywords_advantage') != 'Equal' else 'show similar levels of thematic innovation'}

## Strategic Implications

### For {metrics['field1']['name']} Research Community:
- **Strengths**: {self._identify_field_strengths(metrics['field1'], metrics['field2'])}
- **Opportunities**: {self._identify_field_opportunities(metrics['field1'], metrics['field2'])}

### For {metrics['field2']['name']} Research Community:
- **Strengths**: {self._identify_field_strengths(metrics['field2'], metrics['field1'])}
- **Opportunities**: {self._identify_field_opportunities(metrics['field2'], metrics['field1'])}

## Recommendations

1. **Cross-Field Collaboration**: Explore synergies between {metrics['field1']['name'].lower()} and {metrics['field2']['name'].lower()} research
2. **Best Practice Transfer**: {'Field 2 can learn from Field 1' if metrics['field1']['publications'] > metrics['field2']['publications'] else 'Field 1 can learn from Field 2'}'s {'growth strategies' if abs(metrics['field1']['growth_rate'] - metrics['field2']['growth_rate']) > 5 else 'collaboration approaches'}
3. **Resource Allocation**: Focus investment on {'emerging themes' if max(metrics['field1']['burst_keywords'], metrics['field2']['burst_keywords']) > 10 else 'foundational research'}
4. **Policy Development**: Develop policies that leverage the strengths of both research domains

---

*This comparative analysis provides evidence-based insights for strategic research planning and resource allocation decisions.*
            """
            
            return report
            
        except Exception as e:
            return f"**Comparative Report Generation Failed**\n\nError: {str(e)}"
    
    def _identify_field_strengths(self, field_metrics, comparison_field):
        """识别研究领域的优势"""
        strengths = []
        
        if field_metrics['publications'] > comparison_field['publications']:
            strengths.append("larger publication volume")
        
        if field_metrics['growth_rate'] > comparison_field['growth_rate']:
            strengths.append("higher growth rate")
        
        if field_metrics['collaboration_rate'] > comparison_field['collaboration_rate']:
            strengths.append("stronger international collaboration")
        
        if field_metrics['h_index_max'] > comparison_field['h_index_max']:
            strengths.append("higher research impact")
        
        if field_metrics['burst_keywords'] > comparison_field['burst_keywords']:
            strengths.append("more dynamic thematic evolution")
        
        return ", ".join(strengths) if strengths else "stable research foundation"
    
    def _identify_field_opportunities(self, field_metrics, comparison_field):
        """识别研究领域的机会"""
        opportunities = []
        
        if field_metrics['collaboration_rate'] < comparison_field['collaboration_rate']:
            opportunities.append("enhance international collaboration")
        
        if field_metrics['countries'] < comparison_field['countries']:
            opportunities.append("expand global reach")
        
        if field_metrics['burst_keywords'] < comparison_field['burst_keywords']:
            opportunities.append("explore emerging themes")
        
        if not field_metrics['price_law'] and comparison_field['price_law']:
            opportunities.append("develop core research community")
        
        return ", ".join(opportunities) if opportunities else "maintain current trajectory"

def create_comparative_analysis_tab():
    """创建对比分析标签页"""
    st.header("📊 Comparative Bibliometric Analysis")
    st.markdown("**Multi-Field Research Domain Comparison**")
    
    # 检查是否有数据
    if 'df' not in st.session_state or st.session_state.df.empty:
        st.warning("⚠️ Please upload and process data first")
        return
    
    df = st.session_state.df
    
    # 分析模式选择
    st.markdown("### 🔬 Analysis Mode")
    analysis_mode = st.radio(
        "Choose comparison type:",
        ["Single Field Analysis", "Dual Field Comparison", "Temporal Comparison"],
        help="Select the type of comparative analysis to perform"
    )
    
    if analysis_mode == "Single Field Analysis":
        # 单一领域分析
        st.markdown("### 📋 Field Configuration")
        field_name = st.text_input("Research Field Name", value="Research Domain", help="Enter the research field name")
        
        if st.button("🚀 Generate Single Field Analysis", type="primary"):
            with st.spinner("🔄 Generating comprehensive analysis..."):
                try:
                    analyzer = ComparativeBibliometricAnalyzer(df, field_name)
                    
                    # 显示关键指标
                    metrics = analyzer.comparative_metrics['field1']
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📚 Publications", f"{metrics['publications']:,}")
                    with col2:
                        st.metric("📈 Growth Rate", f"{metrics['growth_rate']:.1f}%")
                    with col3:
                        st.metric("👥 Authors", f"{metrics['authors']:,}")
                    with col4:
                        st.metric("🌍 Countries", f"{metrics['countries']}")
                    
                    # 生成报告
                    generator = EnhancedBibliometricReportGenerator(df, field_name)
                    report = generator.generate_full_jcp_report()
                    
                    with st.expander("📄 Full Analysis Report", expanded=True):
                        st.markdown(report)
                    
                    # 下载选项
                    st.download_button(
                        label="📥 Download Analysis Report",
                        data=report,
                        file_name=f"{field_name.lower().replace(' ', '_')}_analysis_{datetime.now().strftime('%Y%m%d')}.md",
                        mime="text/markdown"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
    
    elif analysis_mode == "Dual Field Comparison":
        # 双领域对比分析
        st.markdown("### 📋 Dual Field Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            field1_name = st.text_input("Field 1 Name", value="Field A", help="Enter first research field name")
            # 这里可以添加第二个数据上传选项
            
        with col2:
            field2_name = st.text_input("Field 2 Name", value="Field B", help="Enter second research field name")
            # 暂时使用同一数据集的子集进行演示
            
        if st.button("🚀 Generate Comparative Analysis", type="primary"):
            with st.spinner("🔄 Generating comparative analysis..."):
                try:
                    # 创建两个子集用于对比（实际应用中应该是两个不同的数据集）
                    df1 = df.iloc[:len(df)//2] if len(df) > 1 else df
                    df2 = df.iloc[len(df)//2:] if len(df) > 1 else df
                    
                    analyzer = ComparativeBibliometricAnalyzer(df1, field1_name, df2, field2_name)
                    
                    # 显示对比指标
                    st.markdown("### 📊 Key Metrics Comparison")
                    metrics = analyzer.comparative_metrics
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{field1_name}**")
                        st.metric("Publications", f"{metrics['field1']['publications']:,}")
                        st.metric("Growth Rate", f"{metrics['field1']['growth_rate']:.1f}%")
                        st.metric("Authors", f"{metrics['field1']['authors']:,}")
                        st.metric("Countries", f"{metrics['field1']['countries']}")
                    
                    with col2:
                        st.markdown(f"**{field2_name}**")
                        st.metric("Publications", f"{metrics['field2']['publications']:,}")
                        st.metric("Growth Rate", f"{metrics['field2']['growth_rate']:.1f}%")
                        st.metric("Authors", f"{metrics['field2']['authors']:,}")
                        st.metric("Countries", f"{metrics['field2']['countries']}")
                    
                    # 生成可视化
                    fig = analyzer.generate_comparative_visualizations()
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # 生成对比报告
                    comparative_report = analyzer.generate_comparative_report()
                    
                    with st.expander("📄 Comparative Analysis Report", expanded=True):
                        st.markdown(comparative_report)
                    
                    # 下载选项
                    st.download_button(
                        label="📥 Download Comparative Report",
                        data=comparative_report,
                        file_name=f"comparative_analysis_{field1_name}_{field2_name}_{datetime.now().strftime('%Y%m%d')}.md",
                        mime="text/markdown"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Comparative analysis failed: {str(e)}")
    
    else:  # Temporal Comparison
        st.markdown("### 📅 Temporal Comparison")
        st.info("🚧 Temporal comparison feature coming soon! This will allow you to compare the same field across different time periods.")
        
        # 时间段选择
        col1, col2 = st.columns(2)
        with col1:
            start_year = st.number_input("Start Year", min_value=1900, max_value=2030, value=2000)
        with col2:
            end_year = st.number_input("End Year", min_value=1900, max_value=2030, value=2024)
        
        split_year = st.slider("Split Year", min_value=start_year, max_value=end_year, value=(start_year + end_year) // 2)
        
        st.markdown(f"**Period 1**: {start_year} - {split_year}")
        st.markdown(f"**Period 2**: {split_year + 1} - {end_year}")
        
        if st.button("🚀 Generate Temporal Comparison", type="primary"):
            st.info("⏳ This feature will be implemented in the next update!")

if __name__ == "__main__":
    create_comparative_analysis_tab()
