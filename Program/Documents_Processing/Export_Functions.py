"""
数据导出功能模块
支持多种格式的数据导出
"""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
import base64
from datetime import datetime
import json
import zipfile
import os
from pathlib import Path

class DataExporter:
    """数据导出类"""
    
    def __init__(self):
        self.export_dir = "output"
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
    
    def export_to_csv(self, df, filename="data_export"):
        """导出数据为CSV格式"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}.csv"
            filepath = os.path.join(self.export_dir, filename)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            return filepath
        except Exception as e:
            st.error(f"CSV导出失败: {str(e)}")
            return None
    
    def export_to_excel(self, data_dict, filename="analysis_report"):
        """导出数据为Excel格式（多工作表）"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}.xlsx"
            filepath = os.path.join(self.export_dir, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for sheet_name, df in data_dict.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return filepath
        except Exception as e:
            st.error(f"Excel导出失败: {str(e)}")
            return None
    
    def export_plotly_figure(self, fig, filename="chart", format="png"):
        """导出Plotly图表"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}.{format}"
            filepath = os.path.join(self.export_dir, filename)
            
            if format == "png":
                fig.write_image(filepath, width=1200, height=800, scale=2)
            elif format == "html":
                fig.write_html(filepath)
            elif format == "pdf":
                fig.write_image(filepath, format="pdf", width=1200, height=800)
            
            return filepath
        except Exception as e:
            st.error(f"图表导出失败: {str(e)}")
            return None
    
    def create_analysis_report(self, df, analysis_results):
        """创建完整的分析报告"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_dir = os.path.join(self.export_dir, f"analysis_report_{timestamp}")
            os.makedirs(report_dir, exist_ok=True)
            
            # 导出原始数据
            df.to_csv(os.path.join(report_dir, "原始数据.csv"), index=False, encoding='utf-8-sig')
            
            # 导出分析结果
            for name, result in analysis_results.items():
                if isinstance(result, pd.DataFrame):
                    result.to_csv(os.path.join(report_dir, f"{name}.csv"), 
                                index=False, encoding='utf-8-sig')
                elif isinstance(result, dict):
                    with open(os.path.join(report_dir, f"{name}.json"), 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
            
            # 创建ZIP文件
            zip_path = f"{report_dir}.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(report_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, report_dir)
                        zipf.write(file_path, arcname)
            
            return zip_path
        except Exception as e:
            st.error(f"分析报告生成失败: {str(e)}")
            return None
    
    def generate_summary_report(self, df):
        """生成数据摘要报告"""
        summary = {
            "数据概览": {
                "总文献数": len(df),
                "数据列数": len(df.columns),
                "缺失值统计": df.isnull().sum().to_dict()
            }
        }
        
        # 添加各字段的统计信息
        for col in df.columns:
            if df[col].dtype == 'object':
                summary[f"{col}_统计"] = {
                    "唯一值数量": df[col].nunique(),
                    "最频繁值": df[col].mode().iloc[0] if not df[col].mode().empty else "无",
                    "最频繁值出现次数": df[col].value_counts().iloc[0] if not df[col].value_counts().empty else 0
                }
            else:
                summary[f"{col}_统计"] = {
                    "平均值": df[col].mean(),
                    "中位数": df[col].median(),
                    "最大值": df[col].max(),
                    "最小值": df[col].min(),
                    "标准差": df[col].std()
                }
        
        return summary

def create_download_link(file_path, link_text="下载文件"):
    """创建下载链接"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}">{link_text}</a>'
        return href
    except Exception as e:
        st.error(f"创建下载链接失败: {str(e)}")
        return None

def export_analysis_data(df, analysis_type="basic"):
    """导出分析数据的便捷函数"""
    exporter = DataExporter()
    
    if analysis_type == "basic":
        # 基础数据导出
        filepath = exporter.export_to_csv(df, "基础数据")
        if filepath:
            st.success(f"✅ 数据已导出到: {filepath}")
            return create_download_link(filepath, "📥 下载CSV文件")
    
    elif analysis_type == "comprehensive":
        # 综合分析导出
        analysis_results = {
            "作者统计": df['作者'].value_counts().head(20).reset_index() if '作者' in df.columns else pd.DataFrame(),
            "期刊统计": df['出版物名称'].value_counts().head(20).reset_index() if '出版物名称' in df.columns else pd.DataFrame(),
            "年份统计": df['出版年'].value_counts().sort_index().reset_index() if '出版年' in df.columns else pd.DataFrame()
        }
        
        zip_path = exporter.create_analysis_report(df, analysis_results)
        if zip_path:
            st.success(f"✅ 综合分析报告已生成: {zip_path}")
            return create_download_link(zip_path, "📥 下载分析报告")
    
    return None

def create_interactive_dashboard_export(df):
    """创建交互式仪表板导出"""
    try:
        # 生成HTML仪表板
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>文献分析仪表板</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; color: #333; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f0f0f0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 文献分析仪表板</h1>
                <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <h3>总文献数</h3>
                    <p>{len(df)}</p>
                </div>
                <div class="metric">
                    <h3>数据列数</h3>
                    <p>{len(df.columns)}</p>
                </div>
                <div class="metric">
                    <h3>数据质量</h3>
                    <p>{((df.count().sum() / (len(df) * len(df.columns))) * 100):.1f}%</p>
                </div>
            </div>
            
            <h2>数据预览</h2>
            <div id="data-preview">
                {df.head(10).to_html(classes='table table-striped', table_id='data-table')}
            </div>
        </body>
        </html>
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = os.path.join("output", f"dashboard_{timestamp}.html")
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_path
    except Exception as e:
        st.error(f"仪表板导出失败: {str(e)}")
        return None
