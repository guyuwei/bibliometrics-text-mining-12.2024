import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import networkx as nx
from collections import Counter
import re

class ResearchReportGenerator:
    """研究报告生成器 - 基于R-Bibliometrix和VOSviewer的文献计量分析报告"""
    
    def __init__(self, df):
        self.df = df
        self.total_articles = len(df)
        self.years = self._extract_years()
        self.authors = self._extract_authors()
        self.countries = self._extract_countries()
        self.journals = self._extract_journals()
        self.keywords = self._extract_keywords()
        
    def _extract_years(self):
        """提取发表年份"""
        if 'PY' in self.df.columns:
            return self.df['PY'].dropna().astype(int).tolist()
        return []
    
    def _extract_authors(self):
        """提取作者信息"""
        if 'AU' in self.df.columns:
            all_authors = []
            for authors in self.df['AU'].dropna():
                if isinstance(authors, str):
                    all_authors.extend([author.strip() for author in authors.split(';')])
            return all_authors
        return []
    
    def _extract_countries(self):
        """提取国家信息"""
        if 'C1' in self.df.columns:
            countries = []
            for address in self.df['C1'].dropna():
                if isinstance(address, str):
                    # 简单的国家提取逻辑
                    country_patterns = [
                        r'USA', r'United States', r'China', r'Japan', r'Germany', 
                        r'UK', r'United Kingdom', r'France', r'Canada', r'Australia',
                        r'Taiwan', r'Korea', r'India', r'Brazil', r'Italy'
                    ]
                    for pattern in country_patterns:
                        if re.search(pattern, address, re.IGNORECASE):
                            countries.append(pattern)
            return countries
        return []
    
    def _extract_journals(self):
        """提取期刊信息"""
        if 'SO' in self.df.columns:
            return self.df['SO'].dropna().tolist()
        return []
    
    def _extract_keywords(self):
        """提取关键词"""
        if 'DE' in self.df.columns:
            all_keywords = []
            for keywords in self.df['DE'].dropna():
                if isinstance(keywords, str):
                    all_keywords.extend([kw.strip() for kw in keywords.split(';')])
            return all_keywords
        return []
    
    def generate_abstract(self):
        """生成摘要"""
        abstract = f"""
        **Abstract**
        
        This study presents a comprehensive bibliometric analysis of [研究领域] research using R-Bibliometrix and VOSviewer. 
        A total of {self.total_articles} articles published between {min(self.years) if self.years else 'N/A'} and {max(self.years) if self.years else 'N/A'} 
        were analyzed to identify research trends, collaboration patterns, and thematic clusters. 
        
        The analysis reveals [计算结果] publications, with [计算结果] countries contributing to the field. 
        The most productive authors include [计算结果], and the leading journals are [计算结果]. 
        Keyword analysis identified [计算结果] main research clusters, with [计算结果] being the most frequently used terms.
        
        The findings provide valuable insights into the current state and future directions of [研究领域] research, 
        offering guidance for researchers and policymakers in this field.
        """
        return abstract
    
    def generate_introduction(self):
        """生成引言"""
        introduction = f"""
        ## 1. Introduction
        
        [研究领域] has emerged as a significant area of research in recent decades, with increasing attention 
        from scholars worldwide. The field has witnessed substantial growth, as evidenced by the [计算结果] 
        publications analyzed in this study, spanning from {min(self.years) if self.years else 'N/A'} to {max(self.years) if self.years else 'N/A'}.
        
        Bibliometric analysis has become an essential tool for understanding research landscapes, 
        identifying collaboration patterns, and mapping knowledge structures (Chen & Song, 2019). 
        The application of R-Bibliometrix and VOSviewer provides comprehensive insights into 
        publication trends, author networks, and thematic evolution (Aria & Cuccurullo, 2017).
        
        This study aims to provide a systematic analysis of [研究领域] research by examining:
        - Publication trends and temporal patterns
        - Author collaboration networks
        - Geographic distribution of research
        - Journal analysis and impact assessment
        - Keyword co-occurrence and thematic clusters
        
        The findings will contribute to understanding the current state of [研究领域] research 
        and identify future research directions.
        """
        return introduction
    
    def generate_methodology(self):
        """生成方法论"""
        methodology = f"""
        ## 2. Methodology
        
        ### 2.1 Data Collection
        The dataset comprises {self.total_articles} articles retrieved from Web of Science (WoS) database. 
        The search strategy employed specific keywords related to [研究领域], ensuring comprehensive coverage 
        of the research domain.
        
        ### 2.2 Bibliometric Analysis Tools
        - **R-Bibliometrix**: Used for comprehensive bibliometric analysis and data processing
        - **VOSviewer**: Employed for network visualization and clustering analysis
        - **Python libraries**: Pandas, NetworkX, and Plotly for additional analysis
        
        ### 2.3 Analysis Framework
        The analysis follows a systematic approach:
        1. **Descriptive Analysis**: Publication trends, author productivity, journal analysis
        2. **Network Analysis**: Collaboration patterns, co-authorship networks
        3. **Content Analysis**: Keyword co-occurrence, thematic clusters
        4. **Geographic Analysis**: Country-wise research distribution
        
        ### 2.4 Statistical Methods
        Various bibliometric indicators were calculated:
        - Publication counts and growth rates
        - Author productivity metrics (h-index, g-index)
        - Journal impact factors and citation analysis
        - Network density and centrality measures
        """
        return methodology
    
    def generate_results(self):
        """生成结果部分"""
        # 计算统计数据
        year_counts = Counter(self.years) if self.years else {}
        author_counts = Counter(self.authors) if self.authors else {}
        journal_counts = Counter(self.journals) if self.journals else {}
        keyword_counts = Counter(self.keywords) if self.keywords else {}
        
        results = f"""
        ## 3. Results
        
        ### 3.1 Publication Trends
        The analysis reveals [计算结果] publications over the study period, with an average of 
        [计算结果] publications per year. The publication trend shows [计算结果] growth pattern, 
        with peak activity in [计算结果] year.
        
        ### 3.2 Author Productivity
        A total of [计算结果] unique authors contributed to the field, with the most productive 
        authors being [计算结果]. The h-index analysis shows [计算结果] as the leading researcher 
        with an h-index of [计算结果].
        
        ### 3.3 Geographic Distribution
        Research contributions span [计算结果] countries, with [计算结果] being the most 
        productive country, contributing [计算结果] publications. The geographic distribution 
        reveals [计算结果] regional concentration patterns.
        
        ### 3.4 Journal Analysis
        Publications appeared in [计算结果] journals, with [计算结果] being the most 
        prominent journal, publishing [计算结果] articles. The journal impact analysis 
        shows [计算结果] as the highest impact journal in the field.
        
        ### 3.5 Keyword Analysis
        The keyword analysis identified [计算结果] unique terms, with [计算结果] being 
        the most frequently used keywords. The co-occurrence network reveals [计算结果] 
        main thematic clusters.
        """
        return results
    
    def generate_discussion(self):
        """生成讨论部分"""
        discussion = f"""
        ## 4. Discussion
        
        ### 4.1 Research Trends and Patterns
        The bibliometric analysis reveals several key trends in [研究领域] research. 
        The [计算结果] publications demonstrate the growing interest in this field, 
        with [计算结果] showing the highest activity period.
        
        ### 4.2 Collaboration Networks
        The author collaboration analysis indicates [计算结果] collaboration patterns, 
        with [计算结果] forming the core research network. The network density of 
        [计算结果] suggests [计算结果] level of collaboration among researchers.
        
        ### 4.3 Geographic Concentration
        The geographic analysis shows [计算结果] concentration of research activity, 
        with [计算结果] countries dominating the field. This pattern reflects 
        [计算结果] factors influencing research development.
        
        ### 4.4 Thematic Evolution
        The keyword analysis reveals [计算结果] main research themes, with 
        [计算结果] emerging as dominant topics. The thematic evolution shows 
        [计算结果] shift in research focus over time.
        
        ### 4.5 Implications for Future Research
        The findings suggest several directions for future research:
        - [计算结果] areas requiring further investigation
        - [计算结果] emerging research themes
        - [计算结果] collaboration opportunities
        - [计算结果] methodological improvements
        """
        return discussion
    
    def generate_conclusion(self):
        """生成结论"""
        conclusion = f"""
        ## 5. Conclusion
        
        This bibliometric analysis provides a comprehensive overview of [研究领域] research, 
        revealing [计算结果] key findings:
        
        1. **Publication Growth**: The field has experienced [计算结果] growth, with 
           [计算结果] publications analyzed, indicating increasing research interest.
        
        2. **Research Networks**: The collaboration analysis shows [计算结果] research 
           networks, with [计算结果] being the most influential researchers.
        
        3. **Geographic Distribution**: Research activity is concentrated in [计算结果] 
           regions, with [计算结果] countries leading in publication output.
        
        4. **Thematic Clusters**: The keyword analysis identified [计算结果] main 
           research themes, reflecting the multidisciplinary nature of the field.
        
        5. **Future Directions**: The analysis suggests [计算结果] areas for future 
           research, including [计算结果] emerging topics and [计算结果] methodological 
           approaches.
        
        The findings contribute to understanding the current state of [研究领域] research 
        and provide guidance for researchers, policymakers, and funding agencies. 
        Future studies should focus on [计算结果] to advance the field further.
        """
        return conclusion
    
    def generate_references(self):
        """生成参考文献"""
        references = """
        ## References
        
        Aria, M., & Cuccurullo, C. (2017). bibliometrix: An R-tool for comprehensive science mapping analysis. Journal of Informetrics, 11(4), 959-975.
        
        Chen, C., & Song, M. (2019). Visualizing a field of research: A methodology of systematic scientometric reviews. PLoS ONE, 14(10), e0223994.
        
        Van Eck, N. J., & Waltman, L. (2010). Software survey: VOSviewer, a computer program for bibliometric mapping. Scientometrics, 84(2), 523-538.
        
        Zupic, I., & Čater, T. (2015). Bibliometric methods in management and organization. Organizational Research Methods, 18(3), 429-472.
        
        [Additional references will be added based on the specific research domain and cited works in the analyzed publications]
        """
        return references
    
    def generate_full_report(self):
        """生成完整报告"""
        report = f"""
        # Research Trends and Patterns in [研究领域]: A Bibliometric Analysis Using R-Bibliometrix and VOSviewer
        
        **Authors**: [Author Names]  
        **Affiliation**: [Institution]  
        **Date**: {datetime.now().strftime('%Y-%m-%d')}  
        **Total Articles Analyzed**: {self.total_articles}
        
        ---
        
        {self.generate_abstract()}
        
        {self.generate_introduction()}
        
        {self.generate_methodology()}
        
        {self.generate_results()}
        
        {self.generate_discussion()}
        
        {self.generate_conclusion()}
        
        {self.generate_references()}
        """
        return report

def create_report_generator_tab():
    """创建报告生成标签页"""
    st.subheader("📝 研究报告生成器")
    st.markdown("基于R-Bibliometrix和VOSviewer的文献计量分析报告生成")
    
    # 检查是否有数据
    if 'df' not in st.session_state or st.session_state.df.empty:
        st.warning("请先上传并处理WOS文件数据")
        return
    
    df = st.session_state.df
    
    # 创建报告生成器
    report_gen = ResearchReportGenerator(df)
    
    # 报告配置
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 报告配置")
        research_field = st.text_input("研究领域", value="台湾南岛语研究", help="请输入您的研究领域")
        author_names = st.text_input("作者姓名", value="[作者姓名]", help="请输入作者姓名")
        institution = st.text_input("机构", value="[机构名称]", help="请输入机构名称")
    
    with col2:
        st.markdown("### 数据统计")
        st.metric("总文献数", len(df))
        st.metric("年份范围", f"{min(report_gen.years) if report_gen.years else 'N/A'}-{max(report_gen.years) if report_gen.years else 'N/A'}")
        st.metric("作者数量", len(set(report_gen.authors)))
        st.metric("期刊数量", len(set(report_gen.journals)))
    
    # 生成报告
    if st.button("🚀 生成研究报告", type="primary"):
        with st.spinner("正在生成报告..."):
            # 更新研究领域
            report_gen.research_field = research_field
            report_gen.author_names = author_names
            report_gen.institution = institution
            
            # 生成完整报告
            full_report = report_gen.generate_full_report()
            
            # 显示报告
            st.markdown("---")
            st.markdown("## 📄 生成的研究报告")
            st.markdown(full_report)
            
            # 提供下载
            st.download_button(
                label="📥 下载报告 (Markdown格式)",
                data=full_report,
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
            
            st.success("✅ 报告生成完成！")
