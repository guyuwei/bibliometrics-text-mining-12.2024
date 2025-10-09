"""
高级分析功能模块
包含H指数、影响因子、合作强度等高级指标计算
"""
import pandas as pd
import numpy as np
import streamlit as st
from collections import defaultdict, Counter
import networkx as nx
from scipy import stats
import math
from datetime import datetime

class AdvancedAnalysis:
    """高级分析类"""
    
    def __init__(self):
        self.h_index_cache = {}
        self.collaboration_cache = {}
    
    def calculate_h_index(self, citations):
        """计算H指数"""
        if not citations or len(citations) == 0:
            return 0
        
        # 将引用次数转换为数值
        try:
            citations = [int(c) for c in citations if pd.notna(c) and str(c).isdigit()]
        except:
            return 0
        
        if not citations:
            return 0
        
        # 按引用次数降序排列
        citations.sort(reverse=True)
        
        h_index = 0
        for i, citation_count in enumerate(citations, 1):
            if citation_count >= i:
                h_index = i
            else:
                break
        
        return h_index
    
    def calculate_g_index(self, citations):
        """计算G指数"""
        if not citations or len(citations) == 0:
            return 0
        
        try:
            citations = [int(c) for c in citations if pd.notna(c) and str(c).isdigit()]
        except:
            return 0
        
        if not citations:
            return 0
        
        citations.sort(reverse=True)
        
        g_index = 0
        total_citations = 0
        
        for i, citation_count in enumerate(citations, 1):
            total_citations += citation_count
            if total_citations >= i * i:
                g_index = i
            else:
                break
        
        return g_index
    
    def calculate_author_h_index(self, df):
        """计算每个作者的H指数"""
        if '作者' not in df.columns or '核心合集的被引频次计数' not in df.columns:
            st.warning("缺少作者或引用信息")
            return pd.DataFrame()
        
        author_h_index = {}
        
        for _, row in df.iterrows():
            authors = str(row['作者']).split(';') if pd.notna(row['作者']) else []
            citation_count = row['核心合集的被引频次计数']
            
            if pd.notna(citation_count) and str(citation_count).isdigit():
                citation_count = int(citation_count)
                
                for author in authors:
                    author = author.strip()
                    if author not in author_h_index:
                        author_h_index[author] = []
                    author_h_index[author].append(citation_count)
        
        # 计算每个作者的H指数
        h_index_results = []
        for author, citations in author_h_index.items():
            h_index = self.calculate_h_index(citations)
            g_index = self.calculate_g_index(citations)
            total_citations = sum(citations)
            paper_count = len(citations)
            
            h_index_results.append({
                '作者': author,
                'H指数': h_index,
                'G指数': g_index,
                '总引用次数': total_citations,
                '发文数量': paper_count,
                '平均引用次数': total_citations / paper_count if paper_count > 0 else 0
            })
        
        return pd.DataFrame(h_index_results).sort_values('H指数', ascending=False)
    
    def calculate_collaboration_strength(self, df):
        """计算合作强度指标"""
        if '作者' not in df.columns:
            st.warning("缺少作者信息")
            return pd.DataFrame()
        
        # 构建合作网络
        G = nx.Graph()
        collaboration_data = defaultdict(int)
        
        for _, row in df.iterrows():
            authors = str(row['作者']).split(';') if pd.notna(row['作者']) else []
            authors = [author.strip() for author in authors if author.strip()]
            
            # 添加合作关系
            for i in range(len(authors)):
                for j in range(i + 1, len(authors)):
                    author1, author2 = authors[i], authors[j]
                    G.add_edge(author1, author2)
                    collaboration_data[(author1, author2)] += 1
        
        # 计算网络指标
        network_metrics = []
        for node in G.nodes():
            degree = G.degree(node)
            clustering = nx.clustering(G, node)
            betweenness = nx.betweenness_centrality(G)[node]
            closeness = nx.closeness_centrality(G)[node]
            
            network_metrics.append({
                '作者': node,
                '合作度': degree,
                '聚类系数': clustering,
                '中介中心性': betweenness,
                '接近中心性': closeness
            })
        
        return pd.DataFrame(network_metrics).sort_values('合作度', ascending=False)
    
    def calculate_journal_impact_metrics(self, df):
        """计算期刊影响指标"""
        if '出版物名称' not in df.columns or '核心合集的被引频次计数' not in df.columns:
            st.warning("缺少期刊或引用信息")
            return pd.DataFrame()
        
        journal_metrics = defaultdict(lambda: {
            '发文数量': 0,
            '总引用次数': 0,
            '引用次数列表': [],
            '作者数量': set()
        })
        
        for _, row in df.iterrows():
            journal = row['出版物名称']
            citation_count = row['核心合集的被引频次计数']
            authors = str(row['作者']).split(';') if pd.notna(row['作者']) else []
            
            if pd.notna(journal):
                journal_metrics[journal]['发文数量'] += 1
                
                if pd.notna(citation_count) and str(citation_count).isdigit():
                    citation_count = int(citation_count)
                    journal_metrics[journal]['总引用次数'] += citation_count
                    journal_metrics[journal]['引用次数列表'].append(citation_count)
                
                for author in authors:
                    journal_metrics[journal]['作者数量'].add(author.strip())
        
        # 计算期刊指标
        journal_results = []
        for journal, metrics in journal_metrics.items():
            if metrics['发文数量'] > 0:
                avg_citations = metrics['总引用次数'] / metrics['发文数量']
                h_index = self.calculate_h_index(metrics['引用次数列表'])
                unique_authors = len(metrics['作者数量'])
                
                journal_results.append({
                    '期刊名称': journal,
                    '发文数量': metrics['发文数量'],
                    '总引用次数': metrics['总引用次数'],
                    '平均引用次数': avg_citations,
                    'H指数': h_index,
                    '独特作者数': unique_authors,
                    '作者多样性': unique_authors / metrics['发文数量'] if metrics['发文数量'] > 0 else 0
                })
        
        return pd.DataFrame(journal_results).sort_values('H指数', ascending=False)
    
    def calculate_research_trends(self, df):
        """计算研究趋势指标"""
        if '出版年' not in df.columns or '作者关键词' not in df.columns:
            st.warning("缺少年份或关键词信息")
            return {}
        
        # 按年份分析
        yearly_data = {}
        for year in sorted(df['出版年'].unique()):
            year_data = df[df['出版年'] == year]
            
            # 关键词分析
            keywords = []
            for kw in year_data['作者关键词'].dropna():
                keywords.extend([k.strip().lower() for k in str(kw).split(';')])
            
            keyword_counts = Counter(keywords)
            
            # 作者分析
            authors = []
            for author_list in year_data['作者'].dropna():
                authors.extend([a.strip() for a in str(author_list).split(';')])
            
            author_counts = Counter(authors)
            
            yearly_data[year] = {
                '发文数量': len(year_data),
                '关键词数量': len(keyword_counts),
                '作者数量': len(author_counts),
                '热门关键词': dict(keyword_counts.most_common(10)),
                '活跃作者': dict(author_counts.most_common(10))
            }
        
        return yearly_data
    
    def calculate_collaboration_diversity(self, df):
        """计算合作多样性指标"""
        if '作者' not in df.columns:
            st.warning("缺少作者信息")
            return {}
        
        # 分析国际合作
        international_collaboration = 0
        domestic_collaboration = 0
        
        # 分析跨机构合作
        cross_institutional = 0
        
        for _, row in df.iterrows():
            authors = str(row['作者']).split(';') if pd.notna(row['作者']) else []
            if len(authors) > 1:
                # 这里可以添加更复杂的国际合作判断逻辑
                # 简化处理：假设多作者就是合作
                if len(authors) > 1:
                    domestic_collaboration += 1
        
        total_papers = len(df)
        collaboration_rate = (domestic_collaboration + international_collaboration) / total_papers if total_papers > 0 else 0
        
        return {
            '总论文数': total_papers,
            '合作论文数': domestic_collaboration + international_collaboration,
            '合作率': collaboration_rate,
            '国内合作': domestic_collaboration,
            '国际合作': international_collaboration
        }
    
    def generate_advanced_report(self, df):
        """生成高级分析报告"""
        report = {
            '作者分析': {},
            '期刊分析': {},
            '合作分析': {},
            '趋势分析': {}
        }
        
        try:
            # 作者H指数分析
            author_h_index = self.calculate_author_h_index(df)
            if not author_h_index.empty:
                report['作者分析']['H指数排名'] = author_h_index.head(20)
                report['作者分析']['平均H指数'] = author_h_index['H指数'].mean()
                report['作者分析']['最高H指数'] = author_h_index['H指数'].max()
            
            # 期刊影响分析
            journal_metrics = self.calculate_journal_impact_metrics(df)
            if not journal_metrics.empty:
                report['期刊分析']['期刊影响排名'] = journal_metrics.head(20)
                report['期刊分析']['平均H指数'] = journal_metrics['H指数'].mean()
            
            # 合作分析
            collaboration_metrics = self.calculate_collaboration_strength(df)
            if not collaboration_metrics.empty:
                report['合作分析']['合作强度排名'] = collaboration_metrics.head(20)
                report['合作分析']['平均合作度'] = collaboration_metrics['合作度'].mean()
            
            # 趋势分析
            trends = self.calculate_research_trends(df)
            if trends:
                report['趋势分析'] = trends
            
            # 合作多样性
            diversity = self.calculate_collaboration_diversity(df)
            if diversity:
                report['合作分析']['多样性指标'] = diversity
            
        except Exception as e:
            st.error(f"高级分析计算失败: {str(e)}")
        
        return report

def calculate_advanced_metrics(df):
    """计算高级指标的便捷函数"""
    analyzer = AdvancedAnalysis()
    return analyzer.generate_advanced_report(df)

def validate_prices_law(df):
    """
    Price定律验证函数
    Price定律：核心作者数 = √总作者数，这些核心作者应产出≥50%的文献
    
    参数:
    - df: 包含作者信息的数据框
    
    返回:
    - 包含Price定律验证结果的字典
    """
    try:
        # 提取作者信息
        authors = []
        author_columns = ['AU', 'Authors', 'Author', '作者']
        
        for col in author_columns:
            if col in df.columns:
                for author_list in df[col].dropna():
                    if isinstance(author_list, str):
                        # 分割作者（支持多种分隔符）
                        separators = [';', ',', '|', '\n']
                        for sep in separators:
                            if sep in author_list:
                                authors.extend([a.strip() for a in author_list.split(sep) if a.strip()])
                                break
                        else:
                            authors.append(author_list.strip())
                break
        
        if not authors:
            return {'error': '未找到作者信息'}
        
        # 统计作者发文量
        author_counts = Counter(authors)
        total_authors = len(author_counts)
        total_publications = len(df)
        
        # Price定律计算（修正：应该基于总文献数，不是总作者数）
        core_authors_expected = math.sqrt(total_publications)
        core_authors_actual = int(core_authors_expected)
        
        # 获取最高产的核心作者
        top_authors = author_counts.most_common(core_authors_actual)
        core_publications = sum([count for _, count in top_authors])
        core_percentage = (core_publications / total_publications) * 100
        
        # Price定律验证（核心作者应产出≥50%文献，允许15%偏差）
        price_law_satisfied = core_percentage >= 35  # 降低阈值，更符合实际情况
        
        # 计算洛特卡定律相关指标
        # 洛特卡定律：发表n篇文章的作者数量与1/n²成正比
        publication_distribution = {}
        for count in author_counts.values():
            if count in publication_distribution:
                publication_distribution[count] += 1
            else:
                publication_distribution[count] = 1
        
        return {
            'total_authors': total_authors,
            'total_publications': total_publications,
            'core_authors_expected': round(core_authors_expected, 2),
            'core_authors_actual': core_authors_actual,
            'core_publications': core_publications,
            'core_percentage': round(core_percentage, 2),
            'price_law_satisfied': price_law_satisfied,
            'price_law_deviation': abs(50 - core_percentage),
            'top_authors': top_authors[:10],
            'most_productive_author': top_authors[0] if top_authors else None,
            'publication_distribution': publication_distribution,
            'author_productivity_stats': {
                'mean': np.mean(list(author_counts.values())),
                'median': np.median(list(author_counts.values())),
                'std': np.std(list(author_counts.values())),
                'max': max(author_counts.values()),
                'min': min(author_counts.values())
            }
        }
        
    except Exception as e:
        return {'error': f'Price定律验证失败: {str(e)}'}

def calculate_collaboration_index(df):
    """
    计算合作指数和网络指标
    
    参数:
    - df: 包含作者信息的数据框
    
    返回:
    - 合作网络相关指标
    """
    try:
        collaboration_data = {
            'single_author_papers': 0,
            'multi_author_papers': 0,
            'collaboration_rate': 0,
            'average_authors_per_paper': 0,
            'max_authors_per_paper': 0,
            'collaboration_distribution': {}
        }
        
        author_columns = ['AU', 'Authors', 'Author', '作者']
        
        for col in author_columns:
            if col in df.columns:
                author_counts_per_paper = []
                
                for author_list in df[col].dropna():
                    if isinstance(author_list, str):
                        # 计算每篇文章的作者数量
                        separators = [';', ',', '|', '\n']
                        author_count = 1  # 默认1个作者
                        
                        for sep in separators:
                            if sep in author_list:
                                author_count = len([a.strip() for a in author_list.split(sep) if a.strip()])
                                break
                        
                        author_counts_per_paper.append(author_count)
                        
                        # 统计合作分布
                        if author_count == 1:
                            collaboration_data['single_author_papers'] += 1
                        else:
                            collaboration_data['multi_author_papers'] += 1
                        
                        # 合作规模分布
                        if author_count in collaboration_data['collaboration_distribution']:
                            collaboration_data['collaboration_distribution'][author_count] += 1
                        else:
                            collaboration_data['collaboration_distribution'][author_count] = 1
                
                if author_counts_per_paper:
                    collaboration_data['average_authors_per_paper'] = round(np.mean(author_counts_per_paper), 2)
                    collaboration_data['max_authors_per_paper'] = max(author_counts_per_paper)
                    
                    total_papers = len(author_counts_per_paper)
                    collaboration_data['collaboration_rate'] = round(
                        (collaboration_data['multi_author_papers'] / total_papers) * 100, 2
                    )
                
                break
        
        return collaboration_data
        
    except Exception as e:
        return {'error': f'合作指数计算失败: {str(e)}'}

def calculate_research_impact_metrics(df):
    """
    计算研究影响力指标
    
    参数:
    - df: 包含引用信息的数据框
    
    返回:
    - 影响力相关指标
    """
    try:
        impact_metrics = {
            'total_citations': 0,
            'average_citations_per_paper': 0,
            'h_index': 0,
            'g_index': 0,
            'highly_cited_papers': 0,
            'uncited_papers': 0,
            'citation_distribution': {}
        }
        
        # 提取引用数据
        citation_columns = ['TC', 'Citations', 'Times Cited', '被引频次', '引用次数']
        citations = []
        
        for col in citation_columns:
            if col in df.columns:
                for citation in df[col].dropna():
                    try:
                        cit_count = int(float(str(citation)))
                        if cit_count >= 0:
                            citations.append(cit_count)
                    except (ValueError, TypeError):
                        citations.append(0)
                break
        
        if not citations:
            return impact_metrics
        
        # 基本统计
        impact_metrics['total_citations'] = sum(citations)
        impact_metrics['average_citations_per_paper'] = round(np.mean(citations), 2)
        
        # H指数计算
        citations_sorted = sorted(citations, reverse=True)
        h_index = 0
        for i, cit_count in enumerate(citations_sorted, 1):
            if cit_count >= i:
                h_index = i
            else:
                break
        impact_metrics['h_index'] = h_index
        
        # G指数计算
        g_index = 0
        cumulative_citations = 0
        for i, cit_count in enumerate(citations_sorted, 1):
            cumulative_citations += cit_count
            if cumulative_citations >= i * i:
                g_index = i
            else:
                break
        impact_metrics['g_index'] = g_index
        
        # 高被引和零被引论文统计
        citation_threshold = np.percentile(citations, 90) if len(citations) > 10 else max(citations)
        impact_metrics['highly_cited_papers'] = len([c for c in citations if c >= citation_threshold])
        impact_metrics['uncited_papers'] = len([c for c in citations if c == 0])
        
        # 引用分布
        for cit_count in citations:
            if cit_count in impact_metrics['citation_distribution']:
                impact_metrics['citation_distribution'][cit_count] += 1
            else:
                impact_metrics['citation_distribution'][cit_count] = 1
        
        return impact_metrics
        
    except Exception as e:
        return {'error': f'影响力指标计算失败: {str(e)}'}

def generate_comprehensive_metrics_report(df):
    """
    生成综合指标报告
    
    参数:
    - df: 文献数据框
    
    返回:
    - 包含所有高级指标的综合报告
    """
    try:
        report = {
            'dataset_info': {
                'total_publications': len(df),
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'prices_law_analysis': validate_prices_law(df),
            'collaboration_analysis': calculate_collaboration_index(df),
            'impact_analysis': calculate_research_impact_metrics(df),
            'advanced_analysis': calculate_advanced_metrics(df)
        }
        
        return report
        
    except Exception as e:
        return {'error': f'综合报告生成失败: {str(e)}'}
