"""
Enhanced Visualization Module
Enhanced data visualization for literature analysis
"""
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import networkx as nx
from collections import Counter
import re
import seaborn as sns

class EnhancedVisualization:
    """Enhanced visualization class for literature analysis"""
    
    def __init__(self):
        """Initialize the visualization class"""
        self.plotly_colors = ['#B5A8CA', '#C0D6EA', '#E0BBD0']
        self.group_mapping = {1: 'SMS', 2: 'MTC', 3: 'AIVC'}
        
        # Set matplotlib parameters
        plt.rcParams['font.family'] = 'Times New Roman'
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['axes.linewidth'] = 1.2
        plt.rcParams['axes.titlesize'] = 18
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['xtick.labelsize'] = 12
        plt.rcParams['ytick.labelsize'] = 12
        plt.rcParams['legend.fontsize'] = 12
    
    def create_publication_timeline(self, df):
        """Create publication timeline visualization"""
        try:
            if '出版年' not in df.columns:
                return None
            
            # Count publications by year
            yearly_counts = df['出版年'].value_counts().sort_index()
            
            # Create timeline plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=yearly_counts.index,
                y=yearly_counts.values,
                mode='lines+markers',
                name='Publications',
                line=dict(color=self.plotly_colors[0], width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title='Publication Timeline',
                xaxis_title='Year',
                yaxis_title='Number of Publications',
                template='plotly_white',
                height=500
            )
            
            return fig
        except Exception as e:
            print(f"Error creating timeline: {e}")
            return None
    
    def create_author_network(self, df, min_collab=2):
        """Create author collaboration network"""
        try:
            if '作者' not in df.columns:
                return None
            
            # Extract author collaborations
            collaborations = []
            for authors in df['作者'].dropna():
                author_list = [author.strip() for author in str(authors).split(';')]
                if len(author_list) > 1:
                    for i in range(len(author_list)):
                        for j in range(i+1, len(author_list)):
                            collaborations.append((author_list[i], author_list[j]))
            
            if not collaborations:
                return None
            
            # Count collaborations
            collab_counts = Counter(collaborations)
            filtered_collabs = {k: v for k, v in collab_counts.items() if v >= min_collab}
            
            if not filtered_collabs:
                return None
            
            # Create network graph
            G = nx.Graph()
            for (author1, author2), weight in filtered_collabs.items():
                G.add_edge(author1, author2, weight=weight)
            
            # Get layout
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            # Create plotly network
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            node_x = []
            node_y = []
            node_text = []
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node)
            
            fig = go.Figure()
            
            # Add edges
            fig.add_trace(go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=2, color='#888'),
                hoverinfo='none',
                mode='lines',
                name='Collaborations'
            ))
            
            # Add nodes
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                textposition="middle center",
                marker=dict(size=20, color=self.plotly_colors[0]),
                name='Authors'
            ))
            
            fig.update_layout(
                title='Author Collaboration Network',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text="Author collaboration network based on co-authorship",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor="left", yanchor="bottom",
                    font=dict(color="#888", size=12)
                )],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=600
            )
            
            return fig
        except Exception as e:
            print(f"Error creating author network: {e}")
            return None
    
    def create_keyword_cloud(self, df, max_words=100):
        """Create keyword word cloud"""
        try:
            if '关键词' not in df.columns:
                return None
            
            # Extract keywords
            all_keywords = []
            for keywords in df['关键词'].dropna():
                keyword_list = [kw.strip().lower() for kw in str(keywords).split(';')]
                all_keywords.extend(keyword_list)
            
            if not all_keywords:
                return None
            
            # Create word cloud
            wordcloud = WordCloud(
                width=800, height=400,
                background_color='white',
                max_words=max_words,
                colormap='viridis',
                font_path=None  # Use default font
            ).generate(' '.join(all_keywords))
            
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title('Keyword Cloud', fontsize=16, fontweight='bold')
            
            return fig
        except Exception as e:
            print(f"Error creating keyword cloud: {e}")
            return None
    
    def create_journal_analysis(self, df):
        """Create journal analysis visualization"""
        try:
            if '出版物名称' not in df.columns:
                return None
            
            # Count publications by journal
            journal_counts = df['出版物名称'].value_counts().head(20)
            
            # Create bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=journal_counts.values,
                y=journal_counts.index,
                orientation='h',
                marker_color=self.plotly_colors[1],
                name='Publications'
            ))
            
            fig.update_layout(
                title='Top 20 Journals by Publication Count',
                xaxis_title='Number of Publications',
                yaxis_title='Journal Name',
                template='plotly_white',
                height=600
            )
            
            return fig
        except Exception as e:
            print(f"Error creating journal analysis: {e}")
            return None
    
    def create_research_trends(self, df):
        """Create research trends visualization"""
        try:
            # 检查关键词字段的多种可能名称
            keyword_column = None
            possible_keyword_columns = ['关键词', '作者关键词', 'Keywords', 'DE', '主题词']
            
            for col in possible_keyword_columns:
                if col in df.columns:
                    keyword_column = col
                    break
            
            if '出版年' not in df.columns or keyword_column is None:
                return None
            
            # Extract keywords by year
            yearly_keywords = {}
            for _, row in df.iterrows():
                year = row['出版年']
                keywords = str(row[keyword_column]).split(';')
                if year not in yearly_keywords:
                    yearly_keywords[year] = []
                yearly_keywords[year].extend([kw.strip().lower() for kw in keywords])
            
            # Get top keywords by year
            top_keywords_by_year = {}
            for year, keywords in yearly_keywords.items():
                keyword_counts = Counter(keywords)
                top_keywords_by_year[year] = dict(keyword_counts.most_common(10))
            
            # Create trend visualization
            fig = go.Figure()
            
            # Add traces for top keywords
            for i, (year, keywords) in enumerate(top_keywords_by_year.items()):
                fig.add_trace(go.Scatter(
                    x=list(keywords.keys()),
                    y=list(keywords.values()),
                    mode='markers',
                    name=f'Year {year}',
                    marker=dict(size=10, color=self.plotly_colors[i % len(self.plotly_colors)])
                ))
            
            fig.update_layout(
                title='Research Trends by Year',
                xaxis_title='Keywords',
                yaxis_title='Frequency',
                template='plotly_white',
                height=500
            )
            
            return fig
        except Exception as e:
            print(f"Error creating research trends: {e}")
            return None
    
    def create_group_analysis(self, df, group_column):
        """Create group analysis visualization"""
        try:
            if group_column not in df.columns:
                return None
            
            # Count publications by group
            group_counts = df[group_column].value_counts()
            
            # Create pie chart
            fig = go.Figure()
            fig.add_trace(go.Pie(
                labels=group_counts.index,
                values=group_counts.values,
                marker_colors=self.plotly_colors
            ))
            
            fig.update_layout(
                title=f'Group Analysis: {group_column}',
                template='plotly_white',
                height=500
            )
            
            return fig
        except Exception as e:
            print(f"Error creating group analysis: {e}")
            return None
    
    def create_country_analysis(self, df):
        """Create country analysis visualization"""
        try:
            # 尝试从多个可能的列中提取国家信息
            country_columns = ['作者地址', 'Country', 'C1', 'Addresses', '国家', 'Affiliation']
            countries = []
            
            for col in country_columns:
                if col in df.columns:
                    for address in df[col].dropna():
                        if pd.notna(address) and str(address).strip():
                            # 提取国家信息的多种方法
                            address_str = str(address)
                            
                            # 方法1: 从地址字符串的最后部分提取
                            if ',' in address_str:
                                country = address_str.split(',')[-1].strip()
                            else:
                                country = address_str.strip()
                            
                            # 清理和标准化国家名称
                            country = country.replace('[', '').replace(']', '')
                            country = re.sub(r'\d+', '', country).strip()
                            
                            if country and len(country) > 1 and len(country) < 50:
                                countries.append(country)
                    
                    if countries:  # 如果找到了国家信息，就不再尝试其他列
                        break
            
            if not countries:
                return None
            
            # 统计国家发文量
            country_counts = pd.Series(countries).value_counts().head(15)
            
            if country_counts.empty:
                return None
            
            # 创建可视化
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Top 15 Countries by Publications', 'Geographic Distribution'),
                specs=[[{"type": "bar"}, {"type": "pie"}]]
            )
            
            # 柱状图
            fig.add_trace(
                go.Bar(
                    x=country_counts.values,
                    y=country_counts.index,
                    orientation='h',
                    marker_color='#B5A8CA',
                    name='Publications'
                ),
                row=1, col=1
            )
            
            # 饼图
            fig.add_trace(
                go.Pie(
                    labels=country_counts.index,
                    values=country_counts.values,
                    marker_colors=self.plotly_colors * (len(country_counts) // len(self.plotly_colors) + 1),
                    name='Distribution'
                ),
                row=1, col=2
            )
            
            fig.update_layout(
                title='Country Analysis - Publication Distribution',
                template='plotly_white',
                height=600,
                showlegend=False
            )
            
            # 更新x轴标签
            fig.update_xaxes(title_text="Number of Publications", row=1, col=1)
            fig.update_yaxes(title_text="Country", row=1, col=1)
            
            return fig
            
        except Exception as e:
            print(f"Error creating country analysis: {e}")
            return None
    
    def create_journal_analysis(self, df):
        """Create journal analysis visualization"""
        try:
            # 尝试从多个可能的列中提取期刊信息
            journal_columns = ['出版物名称', 'Journal', 'Source', 'SO', '期刊', 'Publication']
            
            journal_data = None
            for col in journal_columns:
                if col in df.columns:
                    journal_data = df[col].dropna()
                    break
            
            if journal_data is None or journal_data.empty:
                return None
            
            # 统计期刊发文量
            journal_counts = journal_data.value_counts().head(20)
            
            if journal_counts.empty:
                return None
            
            # 创建可视化
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=journal_counts.values,
                y=journal_counts.index,
                orientation='h',
                marker_color='#C0D6EA',
                text=journal_counts.values,
                textposition='outside'
            ))
            
            fig.update_layout(
                title='Top 20 Journals by Publications',
                xaxis_title='Number of Publications',
                yaxis_title='Journal',
                template='plotly_white',
                height=800,
                margin=dict(l=200)  # 增加左边距以显示期刊名称
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating journal analysis: {e}")
            return None

def create_dashboard_summary(df):
    """Create dashboard summary"""
    try:
        if df is None or df.empty:
            return {
                '总文献数': 0,
                '总作者数': 0,
                '总期刊数': 0,
                '研究年份跨度': 'N/A',
                '数据完整性': '0%'
            }
        
        # Calculate basic statistics
        total_pubs = len(df)
        
        # 安全地计算作者数量
        unique_authors = 0
        if '作者' in df.columns:
            try:
                unique_authors = df['作者'].nunique()
            except:
                unique_authors = 0
        
        # 安全地计算期刊数量
        unique_journals = 0
        journal_columns = ['出版物名称', 'Journal', 'Source', 'SO']
        for col in journal_columns:
            if col in df.columns:
                try:
                    unique_journals = df[col].nunique()
                    break
                except:
                    continue
        
        # 安全地计算年份跨度
        year_span = 'N/A'
        year_columns = ['出版年', 'Year', 'PY', '年份']
        for col in year_columns:
            if col in df.columns:
                try:
                    years = df[col].dropna()
                    if not years.empty:
                        min_year = years.min()
                        max_year = years.max()
                        if pd.notna(min_year) and pd.notna(max_year):
                            year_span = f"{int(min_year)}-{int(max_year)}"
                    break
                except:
                    continue
        
        # 计算数据完整性
        data_completeness = 0
        try:
            if len(df) > 0 and len(df.columns) > 0:
                data_completeness = (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        except:
            data_completeness = 0
        
        return {
            '总文献数': total_pubs,
            '总作者数': unique_authors,
            '总期刊数': unique_journals,
            '研究年份跨度': year_span,
            '数据完整性': f"{data_completeness:.1f}%"
        }
        
    except Exception as e:
        import streamlit as st
        st.error(f"生成数据摘要时出错: {str(e)}")
        return {
            '总文献数': 0,
            '总作者数': 0,
            '总期刊数': 0,
            '研究年份跨度': 'N/A',
            '数据完整性': '0%'
        }