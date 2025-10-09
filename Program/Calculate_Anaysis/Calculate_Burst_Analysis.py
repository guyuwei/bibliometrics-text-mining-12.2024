"""
Kleinberg's Burst Detection Algorithm Implementation
用于文献计量分析中的关键词突现检测
"""

import pandas as pd
import numpy as np
import streamlit as st
from collections import defaultdict, Counter
import math
from scipy import stats
from datetime import datetime

class BurstDetectionAnalyzer:
    """
    基于Kleinberg算法的突现检测分析器
    用于识别研究领域中的突现主题和趋势
    """
    
    def __init__(self):
        self.burst_threshold = 1.5  # 突现强度阈值
        self.min_frequency = 3      # 最小频率要求
        
    def calculate_keyword_burst(self, keywords, years, time_window=1):
        """
        计算关键词突现分析
        
        参数:
        - keywords: 关键词列表
        - years: 对应的年份列表  
        - time_window: 时间窗口大小
        
        返回:
        - 突现关键词列表，包含突现强度和时间段
        """
        if not keywords or not years or len(keywords) != len(years):
            return []
        
        try:
            # 按年份分组关键词
            keyword_by_year = self._group_keywords_by_year(keywords, years)
            
            # 计算每个关键词的突现强度
            burst_results = []
            unique_keywords = set(keywords)
            
            for keyword in unique_keywords:
                if keywords.count(keyword) >= self.min_frequency:
                    burst_data = self._calculate_single_keyword_burst(
                        keyword, keyword_by_year
                    )
                    if burst_data and burst_data['burst_strength'] >= self.burst_threshold:
                        burst_results.append(burst_data)
            
            # 按突现强度排序
            burst_results.sort(key=lambda x: x['burst_strength'], reverse=True)
            
            return burst_results[:50]  # 返回前50个突现关键词
            
        except Exception as e:
            st.warning(f"突现分析计算失败: {str(e)}")
            return []
    
    def _group_keywords_by_year(self, keywords, years):
        """按年份分组关键词"""
        keyword_by_year = defaultdict(list)
        
        for keyword, year in zip(keywords, years):
            if pd.notna(keyword) and pd.notna(year):
                try:
                    year_int = int(float(year))
                    if 1900 <= year_int <= 2030:  # 合理年份范围
                        keyword_by_year[year_int].append(str(keyword).lower().strip())
                except (ValueError, TypeError):
                    continue
        
        return keyword_by_year
    
    def _calculate_single_keyword_burst(self, keyword, keyword_by_year):
        """计算单个关键词的突现强度"""
        try:
            years_sorted = sorted(keyword_by_year.keys())
            if len(years_sorted) < 2:
                return None
            
            # 计算每年的关键词频率
            yearly_counts = []
            for year in years_sorted:
                count = keyword_by_year[year].count(keyword.lower())
                yearly_counts.append(count)
            
            # 计算突现强度
            burst_strength, burst_periods = self._kleinberg_burst_detection(
                yearly_counts, years_sorted
            )
            
            if burst_strength >= self.burst_threshold and burst_periods:
                return {
                    'keyword': keyword,
                    'burst_strength': round(burst_strength, 2),
                    'burst_periods': burst_periods,
                    'burst_years': [years_sorted[i] for i in burst_periods],
                    'total_frequency': sum(yearly_counts),
                    'max_frequency': max(yearly_counts),
                    'years_active': len([c for c in yearly_counts if c > 0])
                }
            
            return None
            
        except Exception as e:
            return None
    
    def _kleinberg_burst_detection(self, counts, years):
        """
        简化的Kleinberg突现检测算法
        
        参数:
        - counts: 每年的频率计数
        - years: 对应的年份
        
        返回:
        - burst_strength: 突现强度
        - burst_periods: 突现时期的索引
        """
        if len(counts) < 2 or sum(counts) == 0:
            return 0, []
        
        try:
            # 计算基准频率（平均频率）
            baseline_rate = sum(counts) / len(counts)
            if baseline_rate == 0:
                return 0, []
            
            # 寻找突现期
            burst_periods = []
            max_burst_strength = 0
            
            # 使用滑动窗口检测突现
            window_size = min(3, len(counts))  # 窗口大小
            
            for i in range(len(counts) - window_size + 1):
                window_counts = counts[i:i + window_size]
                window_rate = sum(window_counts) / len(window_counts)
                
                # 计算突现强度
                if baseline_rate > 0:
                    burst_strength = window_rate / baseline_rate
                    
                    # 如果突现强度超过阈值，记录突现期
                    if burst_strength > self.burst_threshold:
                        burst_periods.extend(range(i, i + window_size))
                        max_burst_strength = max(max_burst_strength, burst_strength)
            
            # 去重并排序突现期
            burst_periods = sorted(list(set(burst_periods)))
            
            return max_burst_strength, burst_periods
            
        except Exception as e:
            return 0, []
    
    def calculate_temporal_burst_analysis(self, df):
        """
        计算时间序列突现分析
        
        参数:
        - df: 包含关键词和年份信息的数据框
        
        返回:
        - 时间序列突现分析结果
        """
        try:
            # 提取关键词和年份
            keywords, years = self._extract_keywords_and_years(df)
            
            if not keywords or not years:
                return {'error': '无法提取关键词或年份信息'}
            
            # 计算突现分析
            burst_results = self.calculate_keyword_burst(keywords, years)
            
            # 生成时间序列统计
            temporal_stats = self._generate_temporal_statistics(keywords, years)
            
            return {
                'burst_keywords': burst_results,
                'temporal_stats': temporal_stats,
                'total_keywords': len(set(keywords)),
                'time_span': f"{min(years)}-{max(years)}" if years else "N/A",
                'burst_keywords_count': len(burst_results)
            }
            
        except Exception as e:
            return {'error': f'时间序列分析失败: {str(e)}'}
    
    def _extract_keywords_and_years(self, df):
        """从数据框中安全提取关键词和年份"""
        keywords = []
        years = []
        
        # 尝试提取关键词
        keyword_columns = ['DE', 'Keywords', 'Keyword', 'ID', '关键词', '主题词']
        keyword_col = None
        
        for col in keyword_columns:
            if col in df.columns:
                keyword_col = col
                break
        
        if keyword_col:
            for kws in df[keyword_col].dropna():
                if isinstance(kws, str) and kws.strip():
                    # 尝试不同分隔符
                    separators = [';', ',', '|', '\n']
                    for sep in separators:
                        if sep in kws:
                            kw_list = [kw.strip().lower() for kw in kws.split(sep) if kw.strip()]
                            keywords.extend(kw_list)
                            break
                    else:
                        keywords.append(kws.strip().lower())
        
        # 尝试提取年份
        year_columns = ['PY', 'Year', 'Publication Year', '出版年', '年份']
        year_col = None
        
        for col in year_columns:
            if col in df.columns:
                year_col = col
                break
        
        if year_col:
            for year in df[year_col].dropna():
                try:
                    year_int = int(float(str(year)))
                    if 1900 <= year_int <= 2030:
                        years.append(year_int)
                except (ValueError, TypeError):
                    continue
        
        # 确保关键词和年份数量匹配
        if len(keywords) > len(years):
            # 如果关键词多于年份，重复年份
            years = (years * (len(keywords) // len(years) + 1))[:len(keywords)]
        elif len(years) > len(keywords):
            # 如果年份多于关键词，截断年份
            years = years[:len(keywords)]
        
        return keywords, years
    
    def _generate_temporal_statistics(self, keywords, years):
        """生成时间统计信息"""
        if not keywords or not years:
            return {}
        
        try:
            # 按年份统计关键词数量
            year_keyword_counts = defaultdict(int)
            unique_keywords_by_year = defaultdict(set)
            
            for keyword, year in zip(keywords, years):
                year_keyword_counts[year] += 1
                unique_keywords_by_year[year].add(keyword)
            
            # 计算统计指标
            years_sorted = sorted(year_keyword_counts.keys())
            
            stats = {
                'time_span': len(years_sorted),
                'start_year': min(years_sorted) if years_sorted else None,
                'end_year': max(years_sorted) if years_sorted else None,
                'peak_year': max(year_keyword_counts, key=year_keyword_counts.get) if year_keyword_counts else None,
                'peak_keyword_count': max(year_keyword_counts.values()) if year_keyword_counts else 0,
                'average_keywords_per_year': sum(year_keyword_counts.values()) / len(year_keyword_counts) if year_keyword_counts else 0,
                'keyword_diversity_trend': self._calculate_diversity_trend(unique_keywords_by_year),
                'growth_pattern': self._analyze_growth_pattern(year_keyword_counts)
            }
            
            return stats
            
        except Exception as e:
            return {'error': f'统计计算失败: {str(e)}'}
    
    def _calculate_diversity_trend(self, unique_keywords_by_year):
        """计算关键词多样性趋势"""
        try:
            years_sorted = sorted(unique_keywords_by_year.keys())
            diversity_scores = []
            
            for year in years_sorted:
                unique_count = len(unique_keywords_by_year[year])
                diversity_scores.append(unique_count)
            
            if len(diversity_scores) > 1:
                # 计算趋势斜率
                x = np.arange(len(diversity_scores))
                slope, _, r_value, _, _ = stats.linregress(x, diversity_scores)
                
                if r_value ** 2 > 0.5:  # R² > 0.5 表示有显著趋势
                    if slope > 0:
                        return 'increasing'
                    else:
                        return 'decreasing'
                else:
                    return 'stable'
            
            return 'insufficient_data'
            
        except Exception:
            return 'unknown'
    
    def _analyze_growth_pattern(self, year_keyword_counts):
        """分析增长模式"""
        try:
            years_sorted = sorted(year_keyword_counts.keys())
            counts = [year_keyword_counts[year] for year in years_sorted]
            
            if len(counts) < 3:
                return 'insufficient_data'
            
            # 线性回归分析
            x = np.arange(len(counts))
            slope, _, r_value, _, _ = stats.linregress(x, counts)
            
            if r_value ** 2 > 0.7:  # 强线性关系
                if slope > 0:
                    return 'linear_growth'
                else:
                    return 'linear_decline'
            
            # 检查指数增长
            try:
                log_counts = np.log(np.array(counts) + 1)
                slope_log, _, r_value_log, _, _ = stats.linregress(x, log_counts)
                
                if r_value_log ** 2 > 0.7:
                    return 'exponential_growth'
            except:
                pass
            
            return 'irregular'
            
        except Exception:
            return 'unknown'
    
    def generate_burst_report(self, df, research_field="Research Field"):
        """生成突现分析报告"""
        try:
            # 执行突现分析
            analysis_results = self.calculate_temporal_burst_analysis(df)
            
            if 'error' in analysis_results:
                return f"**Burst Analysis Report - {research_field}**\n\nError: {analysis_results['error']}"
            
            burst_keywords = analysis_results.get('burst_keywords', [])
            temporal_stats = analysis_results.get('temporal_stats', {})
            
            # 生成报告
            report = f"""
**Keyword Burst Analysis Report - {research_field}**
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Executive Summary

This report presents the results of keyword burst detection analysis using Kleinberg's algorithm to identify emerging themes and research trends in {research_field}.

**Key Findings:**
- **Total Keywords Analyzed**: {analysis_results.get('total_keywords', 0):,}
- **Time Span**: {analysis_results.get('time_span', 'N/A')}
- **Burst Keywords Detected**: {analysis_results.get('burst_keywords_count', 0)}
- **Peak Activity Year**: {temporal_stats.get('peak_year', 'N/A')}

## Temporal Analysis

**Research Activity Pattern:**
- **Start Year**: {temporal_stats.get('start_year', 'N/A')}
- **End Year**: {temporal_stats.get('end_year', 'N/A')}
- **Peak Year**: {temporal_stats.get('peak_year', 'N/A')} ({temporal_stats.get('peak_keyword_count', 0)} keywords)
- **Average Keywords/Year**: {temporal_stats.get('average_keywords_per_year', 0):.1f}
- **Keyword Diversity Trend**: {temporal_stats.get('keyword_diversity_trend', 'unknown').replace('_', ' ').title()}
- **Growth Pattern**: {temporal_stats.get('growth_pattern', 'unknown').replace('_', ' ').title()}

## Top Emerging Keywords

{self._format_burst_keywords_for_report(burst_keywords[:20])}

## Interpretation

The burst analysis reveals {'significant thematic evolution' if len(burst_keywords) > 15 else 'moderate thematic development' if len(burst_keywords) > 5 else 'stable research focus'} in {research_field} research. 

**Key Observations:**
1. **Temporal Dynamics**: The {temporal_stats.get('growth_pattern', 'unknown').replace('_', ' ')} pattern suggests {'rapid field expansion' if 'growth' in temporal_stats.get('growth_pattern', '') else 'stable field development'}
2. **Thematic Diversity**: {temporal_stats.get('keyword_diversity_trend', 'unknown').replace('_', ' ').title()} diversity indicates {'expanding research scope' if temporal_stats.get('keyword_diversity_trend') == 'increasing' else 'focused research agenda' if temporal_stats.get('keyword_diversity_trend') == 'decreasing' else 'consistent thematic focus'}
3. **Research Intensity**: Peak activity in {temporal_stats.get('peak_year', 'N/A')} reflects key developments in the field

## Recommendations

Based on the burst analysis findings:

1. **Emerging Opportunities**: Focus on high-burst keywords for cutting-edge research
2. **Temporal Patterns**: Consider cyclical trends for research planning
3. **Thematic Integration**: Explore connections between burst keywords
4. **Future Monitoring**: Continue tracking keyword evolution patterns

---
*Note: Burst strength > 2.0 indicates strong emergence; > 3.0 indicates very strong emergence*
            """
            
            return report
            
        except Exception as e:
            return f"**Burst Analysis Report Generation Failed**\n\nError: {str(e)}"
    
    def _format_burst_keywords_for_report(self, burst_keywords):
        """为报告格式化突现关键词"""
        if not burst_keywords:
            return "No significant burst keywords detected."
        
        formatted_list = []
        for i, kw_data in enumerate(burst_keywords, 1):
            burst_years_str = ', '.join(map(str, kw_data['burst_years'][:3]))
            strength_level = 'Very High' if kw_data['burst_strength'] > 3.0 else 'High' if kw_data['burst_strength'] > 2.0 else 'Moderate'
            
            formatted_list.append(
                f"{i}. **{kw_data['keyword'].title()}**\n"
                f"   - Burst Strength: {kw_data['burst_strength']} ({strength_level})\n"
                f"   - Burst Period: {burst_years_str}\n"
                f"   - Total Frequency: {kw_data['total_frequency']}\n"
                f"   - Active Years: {kw_data['years_active']}"
            )
        
        return '\n\n'.join(formatted_list)

def calculate_burst_analysis(df, research_field="Research Field"):
    """便捷函数：执行突现分析"""
    analyzer = BurstDetectionAnalyzer()
    return analyzer.calculate_temporal_burst_analysis(df)

def generate_burst_report(df, research_field="Research Field"):
    """便捷函数：生成突现分析报告"""
    analyzer = BurstDetectionAnalyzer()
    return analyzer.generate_burst_report(df, research_field)

def detect_keyword_bursts(df):
    """便捷函数：检测关键词突现"""
    analyzer = BurstDetectionAnalyzer()
    return analyzer.calculate_temporal_burst_analysis(df)
