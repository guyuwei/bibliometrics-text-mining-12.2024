import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class EnhancedLayout:
    """增强布局组件 - 统一的表格和选项美化"""
    
    @staticmethod
    def create_section_header(title, subtitle=None, icon="📊"):
        """创建章节标题"""
        st.markdown(f"""
        <div style="text-align: center; margin: 30px 0;">
            <h3 style="color: #2C3E50; font-size: 1.8rem; font-weight: 400; margin-bottom: 10px; letter-spacing: 0.5px;">
                {icon} {title}
            </h3>
            {f'<p style="color: #5A4B6B; font-size: 1rem; margin: 0;">{subtitle}</p>' if subtitle else ''}
            <div style="width: 80px; height: 2px; background: linear-gradient(90deg, #C0D6EA 0%, #B5A8CA 100%); margin: 15px auto; border-radius: 1px;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def create_info_card(title, content, icon="ℹ️"):
        """创建信息卡片"""
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(192, 214, 234, 0.08) 0%, rgba(181, 168, 202, 0.08) 100%); 
                    padding: 20px; border-radius: 15px; margin: 15px 0; 
                    border: 1px solid rgba(181, 168, 202, 0.2); 
                    backdrop-filter: blur(10px); 
                    box-shadow: 0 8px 32px rgba(181, 168, 202, 0.1);">
            <h4 style="color: #2C3E50; font-size: 1.2rem; font-weight: 500; margin-bottom: 10px; letter-spacing: 0.3px;">
                {icon} {title}
            </h4>
            <p style="color: #5A4B6B; font-size: 0.95rem; line-height: 1.6; margin: 0;">
                {content}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def create_enhanced_dataframe(df, title=None, height=400, show_info=True):
        """创建美化的数据表格"""
        if title:
            st.markdown(f"""
            <div style="margin: 20px 0 10px 0;">
                <h4 style="color: #2C3E50; font-size: 1.3rem; font-weight: 500; margin-bottom: 10px; letter-spacing: 0.3px;">
                    📊 {title}
                </h4>
            </div>
            """, unsafe_allow_html=True)
        
        if show_info and not df.empty:
            st.markdown(f"""
            <div style="background: rgba(192, 214, 234, 0.1); padding: 10px 15px; border-radius: 8px; margin-bottom: 15px; 
                        border-left: 4px solid #B5A8CA;">
                <p style="color: #5A4B6B; font-size: 0.9rem; margin: 0;">
                    📈 显示 {len(df)} 行数据，共 {len(df.columns)} 列
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        return st.dataframe(
            df, 
            height=height, 
            use_container_width=True,
            hide_index=True
        )
    
    @staticmethod
    def create_metrics_row(metrics_data, columns=4):
        """创建指标行"""
        cols = st.columns(columns)
        for i, (title, value, delta) in enumerate(metrics_data):
            with cols[i % columns]:
                st.metric(
                    label=title,
                    value=value,
                    delta=delta
                )
    
    @staticmethod
    def create_enhanced_selectbox(label, options, key=None, help_text=None):
        """创建美化的选择框"""
        if help_text:
            st.markdown(f"""
            <div style="margin-bottom: 5px;">
                <p style="color: #5A4B6B; font-size: 0.9rem; margin: 0;">💡 {help_text}</p>
            </div>
            """, unsafe_allow_html=True)
        
        return st.selectbox(
            label,
            options,
            key=key,
            help=help_text
        )
    
    @staticmethod
    def create_enhanced_multiselect(label, options, key=None, help_text=None):
        """创建美化的多选框"""
        if help_text:
            st.markdown(f"""
            <div style="margin-bottom: 5px;">
                <p style="color: #5A4B6B; font-size: 0.9rem; margin: 0;">💡 {help_text}</p>
            </div>
            """, unsafe_allow_html=True)
        
        return st.multiselect(
            label,
            options,
            key=key,
            help=help_text
        )
    
    @staticmethod
    def create_enhanced_slider(label, min_value, max_value, value, key=None, help_text=None):
        """创建美化的滑块"""
        if help_text:
            st.markdown(f"""
            <div style="margin-bottom: 5px;">
                <p style="color: #5A4B6B; font-size: 0.9rem; margin: 0;">💡 {help_text}</p>
            </div>
            """, unsafe_allow_html=True)
        
        return st.slider(
            label,
            min_value=min_value,
            max_value=max_value,
            value=value,
            key=key,
            help=help_text
        )
    
    @staticmethod
    def create_enhanced_checkbox(label, key=None, help_text=None):
        """创建美化的复选框"""
        if help_text:
            st.markdown(f"""
            <div style="margin-bottom: 5px;">
                <p style="color: #5A4B6B; font-size: 0.9rem; margin: 0;">💡 {help_text}</p>
            </div>
            """, unsafe_allow_html=True)
        
        return st.checkbox(
            label,
            key=key,
            help=help_text
        )
    
    @staticmethod
    def create_enhanced_text_input(label, key=None, help_text=None, placeholder=None):
        """创建美化的文本输入框"""
        if help_text:
            st.markdown(f"""
            <div style="margin-bottom: 5px;">
                <p style="color: #5A4B6B; font-size: 0.9rem; margin: 0;">💡 {help_text}</p>
            </div>
            """, unsafe_allow_html=True)
        
        return st.text_input(
            label,
            key=key,
            help=help_text,
            placeholder=placeholder
        )
    
    @staticmethod
    def create_enhanced_file_uploader(label, type=None, key=None, help_text=None):
        """创建美化的文件上传器"""
        if help_text:
            st.markdown(f"""
            <div style="margin-bottom: 5px;">
                <p style="color: #5A4B6B; font-size: 0.9rem; margin: 0;">💡 {help_text}</p>
            </div>
            """, unsafe_allow_html=True)
        
        return st.file_uploader(
            label,
            type=type,
            key=key,
            help=help_text
        )
    
    @staticmethod
    def create_enhanced_button(label, key=None, type="secondary", help_text=None):
        """创建美化的按钮"""
        if help_text:
            st.markdown(f"""
            <div style="margin-bottom: 5px;">
                <p style="color: #5A4B6B; font-size: 0.9rem; margin: 0;">💡 {help_text}</p>
            </div>
            """, unsafe_allow_html=True)
        
        return st.button(
            label,
            key=key,
            type=type,
            help=help_text
        )
    
    @staticmethod
    def create_enhanced_expander(label, expanded=False):
        """创建美化的展开器"""
        return st.expander(
            label,
            expanded=expanded
        )
    
    @staticmethod
    def create_enhanced_tabs(tab_names, tab_icons=None):
        """创建美化的标签页"""
        if tab_icons:
            formatted_tabs = [f"{icon} {name}" for icon, name in zip(tab_icons, tab_names)]
        else:
            formatted_tabs = tab_names
        
        return st.tabs(formatted_tabs)
    
    @staticmethod
    def create_enhanced_columns(num_columns, gap="medium"):
        """创建美化的列布局"""
        return st.columns(num_columns, gap=gap)
    
    @staticmethod
    def create_enhanced_alert(message, type="info"):
        """创建美化的警告框"""
        icons = {
            "info": "ℹ️",
            "success": "✅", 
            "warning": "⚠️",
            "error": "❌"
        }
        
        colors = {
            "info": "#0dcaf0",
            "success": "#28a745",
            "warning": "#ffc107", 
            "error": "#dc3545"
        }
        
        icon = icons.get(type, "ℹ️")
        color = colors.get(type, "#0dcaf0")
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {color}20 0%, {color}10 100%); 
                    padding: 15px 20px; border-radius: 12px; margin: 15px 0; 
                    border-left: 4px solid {color}; 
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);">
            <p style="color: #2C3E50; font-size: 0.95rem; margin: 0; font-weight: 500;">
                {icon} {message}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def create_enhanced_progress_bar(progress, label=None):
        """创建美化的进度条"""
        if label:
            st.markdown(f"""
            <div style="margin-bottom: 10px;">
                <p style="color: #2C3E50; font-size: 0.95rem; margin: 0; font-weight: 500;">{label}</p>
            </div>
            """, unsafe_allow_html=True)
        
        return st.progress(progress)
    
    @staticmethod
    def create_enhanced_spinner(message="处理中..."):
        """创建美化的加载器"""
        return st.spinner(message)
    
    @staticmethod
    def create_enhanced_plotly_chart(fig, title=None, height=400):
        """创建美化的Plotly图表"""
        if title:
            fig.update_layout(
                title={
                    'text': title,
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 16, 'color': '#2C3E50'}
                },
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#4A3C5C')
            )
        
        return st.plotly_chart(fig, use_container_width=True, height=height)
