"""
System Validation and Testing Module
系统验证和测试模块
用于验证增强版文献计量分析系统的功能完整性
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import traceback
from collections import Counter
import random

# 添加模块路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SystemValidator:
    """系统验证器"""
    
    def __init__(self):
        self.test_results = {}
        self.sample_data = None
        
    def generate_sample_data(self, n_articles=100):
        """生成样本测试数据"""
        try:
            # 模拟作者数据
            authors = [f"Author_{i}" for i in range(1, 51)]
            
            # 模拟期刊数据
            journals = [
                "Journal of Cleaner Production",
                "Applied Energy",
                "Energy Policy",
                "Renewable Energy",
                "Energy and Buildings",
                "Environmental Science & Technology",
                "Science of the Total Environment",
                "Sustainability"
            ]
            
            # 模拟关键词
            keywords = [
                "sustainability", "renewable energy", "climate change", "carbon footprint",
                "energy efficiency", "green technology", "environmental impact",
                "circular economy", "life cycle assessment", "sustainable development",
                "clean energy", "environmental policy", "carbon emissions",
                "green innovation", "sustainable manufacturing"
            ]
            
            # 模拟国家
            countries = ["USA", "China", "UK", "Germany", "Japan", "France", "Canada", "Australia"]
            
            # 生成数据
            data = []
            base_year = 2010
            
            for i in range(n_articles):
                # 随机选择年份，近年来更多文章
                year_weights = [1, 1, 2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
                year = base_year + np.random.choice(range(15), p=np.array(year_weights)/sum(year_weights))
                
                # 随机选择作者（1-5个）
                n_authors = np.random.randint(1, 6)
                article_authors = np.random.choice(authors, size=n_authors, replace=False)
                
                # 随机选择关键词（3-8个）
                n_keywords = np.random.randint(3, 9)
                article_keywords = np.random.choice(keywords, size=n_keywords, replace=False)
                
                # 随机引用次数（遵循幂律分布）
                citations = max(0, int(np.random.pareto(1) * 5))
                
                # 创建记录
                record = {
                    'TI': f"Research Article {i+1}: A Study on {article_keywords[0].title()}",
                    'AU': '; '.join(article_authors),
                    'PY': year,
                    'SO': np.random.choice(journals),
                    'DE': '; '.join(article_keywords),
                    'TC': citations,
                    'C1': f"{np.random.choice(countries)}, University of Research",
                    'AB': f"This study investigates {article_keywords[0]} and its implications for {article_keywords[1]}. The research provides insights into sustainable development practices.",
                    'DT': 'Article'
                }
                
                data.append(record)
            
            self.sample_data = pd.DataFrame(data)
            return True
            
        except Exception as e:
            st.error(f"样本数据生成失败: {str(e)}")
            return False
    
    def test_enhanced_report_generator(self):
        """测试增强版报告生成器"""
        test_name = "Enhanced Report Generator"
        
        try:
            from Enhanced_Report_Generator import EnhancedBibliometricReportGenerator
            
            # 创建报告生成器
            generator = EnhancedBibliometricReportGenerator(self.sample_data, "Test Research Field")
            
            # 测试基本功能
            tests = {
                "Data Extraction": self._test_data_extraction(generator),
                "Advanced Metrics": self._test_advanced_metrics(generator),
                "Abstract Generation": self._test_abstract_generation(generator),
                "Methodology Generation": self._test_methodology_generation(generator),
                "Results Generation": self._test_results_generation(generator),
                "Full Report Generation": self._test_full_report_generation(generator)
            }
            
            self.test_results[test_name] = tests
            return all(tests.values())
            
        except Exception as e:
            self.test_results[test_name] = {"Error": str(e)}
            return False
    
    def test_burst_analysis(self):
        """测试突现分析模块"""
        test_name = "Burst Analysis"
        
        try:
            from Calculate_Burst_Analysis import BurstDetectionAnalyzer
            
            analyzer = BurstDetectionAnalyzer()
            
            # 提取关键词和年份
            keywords = []
            years = []
            
            for _, row in self.sample_data.iterrows():
                if pd.notna(row['DE']):
                    kws = [kw.strip().lower() for kw in str(row['DE']).split(';')]
                    keywords.extend(kws)
                    years.extend([row['PY']] * len(kws))
            
            tests = {
                "Data Processing": len(keywords) > 0 and len(years) > 0,
                "Burst Detection": self._test_burst_detection(analyzer, keywords, years),
                "Report Generation": self._test_burst_report(analyzer)
            }
            
            self.test_results[test_name] = tests
            return all(tests.values())
            
        except Exception as e:
            self.test_results[test_name] = {"Error": str(e)}
            return False
    
    def test_comparative_analysis(self):
        """测试对比分析模块"""
        test_name = "Comparative Analysis"
        
        try:
            from Comparative_Analysis import ComparativeBibliometricAnalyzer
            
            # 创建两个数据子集
            df1 = self.sample_data.iloc[:50]
            df2 = self.sample_data.iloc[50:]
            
            analyzer = ComparativeBibliometricAnalyzer(df1, "Field A", df2, "Field B")
            
            tests = {
                "Initialization": analyzer.comparative_metrics is not None,
                "Metrics Calculation": self._test_comparative_metrics(analyzer),
                "Visualization": self._test_comparative_visualization(analyzer),
                "Report Generation": self._test_comparative_report(analyzer)
            }
            
            self.test_results[test_name] = tests
            return all(tests.values())
            
        except Exception as e:
            self.test_results[test_name] = {"Error": str(e)}
            return False
    
    def test_calculation_modules(self):
        """测试计算模块"""
        test_name = "Calculation Modules"
        
        try:
            tests = {
                "Advanced Analysis": self._test_advanced_analysis_module(),
                "Author Analysis": self._test_author_analysis_module(),
                "Publication Analysis": self._test_publication_analysis_module(),
                "Keywords Analysis": self._test_keywords_analysis_module()
            }
            
            self.test_results[test_name] = tests
            return all(tests.values())
            
        except Exception as e:
            self.test_results[test_name] = {"Error": str(e)}
            return False
    
    def _test_data_extraction(self, generator):
        """测试数据提取"""
        try:
            return (len(generator.years) > 0 and 
                   len(generator.authors) > 0 and 
                   len(generator.keywords) > 0 and
                   len(generator.journals) > 0)
        except:
            return False
    
    def _test_advanced_metrics(self, generator):
        """测试高级指标计算"""
        try:
            return (hasattr(generator, 'annual_data') and
                   hasattr(generator, 'core_authors_data') and
                   hasattr(generator, 'h_index_data') and
                   hasattr(generator, 'collaboration_data') and
                   hasattr(generator, 'burst_keywords'))
        except:
            return False
    
    def _test_abstract_generation(self, generator):
        """测试摘要生成"""
        try:
            abstract = generator.generate_jcp_style_abstract()
            return isinstance(abstract, str) and len(abstract) > 100
        except:
            return False
    
    def _test_methodology_generation(self, generator):
        """测试方法论生成"""
        try:
            methodology = generator.generate_jcp_methodology()
            return isinstance(methodology, str) and "methodology" in methodology.lower()
        except:
            return False
    
    def _test_results_generation(self, generator):
        """测试结果生成"""
        try:
            results = generator.generate_jcp_results()
            return isinstance(results, str) and "results" in results.lower()
        except:
            return False
    
    def _test_full_report_generation(self, generator):
        """测试完整报告生成"""
        try:
            report = generator.generate_full_jcp_report()
            return isinstance(report, str) and len(report) > 1000
        except:
            return False
    
    def _test_burst_detection(self, analyzer, keywords, years):
        """测试突现检测"""
        try:
            burst_results = analyzer.calculate_keyword_burst(keywords, years)
            return isinstance(burst_results, list)
        except:
            return False
    
    def _test_burst_report(self, analyzer):
        """测试突现报告"""
        try:
            report = analyzer.generate_burst_report(self.sample_data, "Test Field")
            return isinstance(report, str) and len(report) > 100
        except:
            return False
    
    def _test_comparative_metrics(self, analyzer):
        """测试对比指标"""
        try:
            metrics = analyzer.comparative_metrics
            return ('field1' in metrics and 
                   'field2' in metrics and 
                   'comparison' in metrics)
        except:
            return False
    
    def _test_comparative_visualization(self, analyzer):
        """测试对比可视化"""
        try:
            fig = analyzer.generate_comparative_visualizations()
            return fig is not None
        except:
            return False
    
    def _test_comparative_report(self, analyzer):
        """测试对比报告"""
        try:
            report = analyzer.generate_comparative_report()
            return isinstance(report, str) and len(report) > 500
        except:
            return False
    
    def _test_advanced_analysis_module(self):
        """测试高级分析模块"""
        try:
            from Calculate_Anaysis.Calculate_Advanced import AdvancedAnalysis
            analyzer = AdvancedAnalysis()
            return hasattr(analyzer, 'calculate_h_index')
        except:
            return False
    
    def _test_author_analysis_module(self):
        """测试作者分析模块"""
        try:
            from Calculate_Anaysis.Calculate_Author import calculate_number_of_authors_publication
            return callable(calculate_number_of_authors_publication)
        except:
            return False
    
    def _test_publication_analysis_module(self):
        """测试发文分析模块"""
        try:
            from Calculate_Anaysis.Calculate_Publication import calculate_publications_per_year
            return callable(calculate_publications_per_year)
        except:
            return False
    
    def _test_keywords_analysis_module(self):
        """测试关键词分析模块"""
        try:
            from Calculate_Anaysis.Calculate_Keywords import calculate_number_of_keywords
            return callable(calculate_number_of_keywords)
        except:
            return False
    
    def run_full_validation(self):
        """运行完整系统验证"""
        st.header("🧪 System Validation & Testing")
        st.markdown("**Comprehensive Testing of Enhanced Bibliometric Analysis System**")
        
        # 生成测试数据
        st.markdown("### 📊 Generating Test Data")
        with st.spinner("🔄 Creating sample dataset..."):
            if self.generate_sample_data(100):
                st.success(f"✅ Generated {len(self.sample_data)} sample articles")
                
                # 显示样本数据预览
                with st.expander("🔍 Sample Data Preview", expanded=False):
                    st.dataframe(self.sample_data.head())
            else:
                st.error("❌ Failed to generate sample data")
                return
        
        # 运行测试
        st.markdown("### 🔬 Running System Tests")
        
        test_functions = [
            ("Enhanced Report Generator", self.test_enhanced_report_generator),
            ("Burst Analysis Module", self.test_burst_analysis),
            ("Comparative Analysis", self.test_comparative_analysis),
            ("Calculation Modules", self.test_calculation_modules)
        ]
        
        overall_success = True
        
        for test_name, test_func in test_functions:
            with st.spinner(f"🧪 Testing {test_name}..."):
                try:
                    success = test_func()
                    if success:
                        st.success(f"✅ {test_name}: PASSED")
                    else:
                        st.error(f"❌ {test_name}: FAILED")
                        overall_success = False
                except Exception as e:
                    st.error(f"❌ {test_name}: ERROR - {str(e)}")
                    overall_success = False
        
        # 显示详细测试结果
        st.markdown("### 📋 Detailed Test Results")
        
        for module_name, tests in self.test_results.items():
            with st.expander(f"📊 {module_name} Test Details", expanded=False):
                if isinstance(tests, dict):
                    for test_name, result in tests.items():
                        status = "✅ PASS" if result else "❌ FAIL"
                        st.markdown(f"- **{test_name}**: {status}")
                else:
                    st.markdown(f"- **Overall**: {'✅ PASS' if tests else '❌ FAIL'}")
        
        # 总体结果
        st.markdown("---")
        if overall_success:
            st.success("🎉 **All tests passed!** Your enhanced bibliometric analysis system is working correctly.")
            st.balloons()
        else:
            st.warning("⚠️ **Some tests failed.** Please check the detailed results above.")
        
        # 系统信息
        st.markdown("### 💻 System Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Test Articles", len(self.sample_data) if self.sample_data is not None else 0)
        with col2:
            st.metric("Modules Tested", len(self.test_results))
        with col3:
            passed_tests = sum(1 for tests in self.test_results.values() 
                             if isinstance(tests, dict) and all(tests.values()) or 
                             (not isinstance(tests, dict) and tests))
            st.metric("Success Rate", f"{passed_tests}/{len(self.test_results)}")
        
        return overall_success
    
    def generate_performance_report(self):
        """生成性能报告"""
        if not self.test_results:
            st.warning("请先运行系统验证测试")
            return
        
        report = f"""
# System Validation Report - Enhanced Bibliometric Analysis Framework

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Test Dataset**: {len(self.sample_data) if self.sample_data is not None else 0} sample articles

## Test Summary

{self._format_test_summary()}

## Module Performance

{self._format_module_performance()}

## Recommendations

{self._generate_recommendations()}

---
*This report validates the functionality and performance of the enhanced bibliometric analysis system.*
        """
        
        return report
    
    def _format_test_summary(self):
        """格式化测试摘要"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for tests in self.test_results.values() 
                          if isinstance(tests, dict) and all(tests.values()) or 
                          (not isinstance(tests, dict) and tests))
        
        return f"""
- **Total Modules Tested**: {total_tests}
- **Passed Tests**: {passed_tests}
- **Success Rate**: {passed_tests/total_tests*100:.1f}%
- **Overall Status**: {'✅ SYSTEM OPERATIONAL' if passed_tests == total_tests else '⚠️ PARTIAL FUNCTIONALITY'}
        """
    
    def _format_module_performance(self):
        """格式化模块性能"""
        performance_text = []
        
        for module_name, tests in self.test_results.items():
            if isinstance(tests, dict):
                passed = sum(1 for result in tests.values() if result)
                total = len(tests)
                status = "✅ OPERATIONAL" if passed == total else "⚠️ PARTIAL" if passed > 0 else "❌ FAILED"
                performance_text.append(f"- **{module_name}**: {passed}/{total} tests passed - {status}")
            else:
                status = "✅ OPERATIONAL" if tests else "❌ FAILED"
                performance_text.append(f"- **{module_name}**: {status}")
        
        return '\n'.join(performance_text)
    
    def _generate_recommendations(self):
        """生成建议"""
        failed_modules = [name for name, tests in self.test_results.items() 
                         if isinstance(tests, dict) and not all(tests.values()) or 
                         (not isinstance(tests, dict) and not tests)]
        
        if not failed_modules:
            return """
1. **System Status**: All modules are functioning correctly
2. **Performance**: Ready for production use
3. **Maintenance**: Regular testing recommended for updates
4. **Usage**: All enhanced features are available
            """
        else:
            return f"""
1. **Failed Modules**: {', '.join(failed_modules)} require attention
2. **Action Required**: Debug and fix failing components
3. **Temporary Solution**: Use basic functionality until issues resolved
4. **Testing**: Re-run validation after fixes
            """

def create_system_validator_tab():
    """创建系统验证标签页"""
    st.header("🧪 System Validation & Testing")
    st.markdown("**Comprehensive testing suite for the enhanced bibliometric analysis framework**")
    
    validator = SystemValidator()
    
    # 选择测试模式
    test_mode = st.radio(
        "Select testing mode:",
        ["Quick Validation", "Full System Test", "Performance Analysis"],
        help="Choose the type of testing to perform"
    )
    
    if test_mode == "Quick Validation":
        st.markdown("### ⚡ Quick System Check")
        
        if st.button("🚀 Run Quick Test", type="primary"):
            with st.spinner("🔄 Running quick validation..."):
                # 生成小样本数据
                if validator.generate_sample_data(20):
                    # 运行基本测试
                    basic_tests = {
                        "Data Generation": True,
                        "Enhanced Report Generator": validator.test_enhanced_report_generator(),
                        "Calculation Modules": validator.test_calculation_modules()
                    }
                    
                    # 显示结果
                    for test_name, result in basic_tests.items():
                        if result:
                            st.success(f"✅ {test_name}: PASSED")
                        else:
                            st.error(f"❌ {test_name}: FAILED")
                    
                    overall_success = all(basic_tests.values())
                    if overall_success:
                        st.success("🎉 Quick validation passed! System is operational.")
                    else:
                        st.warning("⚠️ Some basic functions failed. Run full test for details.")
    
    elif test_mode == "Full System Test":
        st.markdown("### 🔬 Comprehensive System Testing")
        
        if st.button("🧪 Run Full Test Suite", type="primary"):
            validator.run_full_validation()
            
            # 提供报告下载
            if validator.test_results:
                report = validator.generate_performance_report()
                st.download_button(
                    label="📥 Download Validation Report",
                    data=report,
                    file_name=f"system_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
    
    else:  # Performance Analysis
        st.markdown("### 📊 Performance Analysis")
        st.info("🚧 Performance analysis feature coming soon!")
        
        # 性能分析配置
        col1, col2 = st.columns(2)
        with col1:
            test_size = st.slider("Test Dataset Size", min_value=50, max_value=1000, value=200)
        with col2:
            iterations = st.slider("Test Iterations", min_value=1, max_value=10, value=3)
        
        if st.button("📈 Run Performance Analysis", type="primary"):
            st.info("⏳ This feature will measure processing times and memory usage for different dataset sizes.")

if __name__ == "__main__":
    create_system_validator_tab()
