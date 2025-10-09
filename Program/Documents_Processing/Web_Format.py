import streamlit as st
import base64
from io import BytesIO
#Title
def st_title(title_text):
    st.title(title_text, justify="center",align="center")

def set_page_title_with_image(title: str, image_path: str, image_width: int = 50, image_height: int = 50):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    # 构造 HTML 代码
    html_code = f"""
    <div style="display: flex; align-items: center;">
        <img src="data:image/png;base64,{encoded_image}" alt="Logo" style="width: {image_width}px; height: {image_height}px; margin-right: 10px;">
        <h1 style="  font-size: 80px;
                color: black!important;  /* 强制应用颜色 */
                font-weight: 700;
                text-align: center!;
                margin-top: 60px;
                text-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                letter-spacing: 1.2px;">{title}</h1>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# Header
def st_header(header_text):
    st.markdown(f"""
        <style>
            body {{
                background-color: #fafafa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #333;
            }}
            h1 {{
                font-size: 50px;
                color: black!important;  /* 强制应用颜色 */
                font-weight: 700;
                text-align: center;
                margin-top: 60px;
                text-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                letter-spacing: 1.2px;
            }}
        </style>
        <h1>{header_text}</h1>
    """, unsafe_allow_html=True)


# Subheader
def st_subheader(subheader_text):
    st.markdown(f"""
        <style>
            body {{
                background-color: #fafafa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            h2 {{
                font-size: 26px;
                color: #ff6f61!important;  /* 强制应用颜色 */
                font-weight: 600;
                text-align: left;
                text-shadow: 0px 3px 6px rgba(0, 0, 0, 0.05);
                margin-left: 20px;
                margin-top: 35px;
                letter-spacing: 1px;
            }}
        </style>
        <h2>{subheader_text}</h2>
    """, unsafe_allow_html=True)


#
def st_subsubheader(subsubheader_text):
    st_markdown(fr'##### {subsubheader_text}')


# Card
def st_card(card_title, card_content):
    with st.expander(card_title, expanded=True):
        st.markdown(f"""
        <style>
            .card {{
                background-color: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0px 6px 20px rgba(0, 0, 0, 0.1);
                margin-bottom: 40px;
            }}
            .card-title {{
                font-size: 28px;
                font-weight: 700;
                color: #ff6f61; /* 标题颜色 */
                margin-bottom: 20px;
            }}
            .card-content {{
                font-size: 18px;
                color: #777; /* 内容颜色 */
                line-height: 1.6; /* 行高 */
            }}
            .card-content ul {{
                list-style-type: disc; /* 列表样式 */
                margin-left: 20px;
            }}
            .card-content ul li {{
                margin-bottom: 10px; /* 列表项间距 */
            }}
        </style>
            {card_content}
        </div>
    """, unsafe_allow_html=True)


# Text Input
def st_text_input(label):
    st.markdown(f"""
        <style>
            .stTextInput>div>div>input {{
                border-radius: 30px;
                border: 2px solid #ff6f61!important;  /* 强制应用颜色 */
                padding: 12px;
                font-size: 18px;
                color: #333;
                background-color: #f9f9f9;
                transition: all 0.3s ease;
            }}
            .stTextInput>div>div>input:focus {{
                border-color: #e04e3f!important;  /* 强制应用颜色 */
                box-shadow: 0 0 12px rgba(0, 0, 0, 0.1);
            }}
        </style>
        {label}
    """, unsafe_allow_html=True)


# Text Area
def st_text_area(label):
    st.markdown(f"""
        <style>
            .stTextArea>div>textarea {{
                border-radius: 20px;
                border: 2px solid #ff6f61!important;  /* 强制应用颜色 */
                padding: 14px;
                font-size: 18px;
                color: #333;
                background-color: #f9f9f9;
                transition: all 0.3s ease;
            }}
            .stTextArea>div>textarea:focus {{
                border-color: #e04e3f!important;  /* 强制应用颜色 */
                box-shadow: 0 0 12px rgba(0, 0, 0, 0.1);
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.text_area(label)


# Select Box
def st_selectbox(label, options):
    st.markdown(f"""
        <style>
            .stSelectbox>div>div>div {{
                border-radius: 25px;
                border: 2px solid #ff6f61!important;  /* 强制应用颜色 */
                padding: 12px;
                font-size: 18px;
                color: #333;
                background-color: #f9f9f9;
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.selectbox(label, options)


# Checkbox
def st_checkbox(label):
    st.markdown(f"""
        <style>
            .stCheckbox>div>div>label {{
                font-size: 20px;
                color: #ff6f61!important;  /* 强制应用颜色 */
                font-weight: 600;
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.checkbox(label)


# Radio Buttons
def st_radio(label, options, index, horizontal):
    st.markdown(f"""
        <style>
            .stRadio>div>div>label {{
                font-size: 20px;
                color: #ff6f61!important;  /* 强制应用颜色 */
                font-weight: 600;
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.radio(label, options, index, horizontal=True)


# Slider
def st_slider(label, min_value, max_value, value, step):
    st.markdown(f"""
        <style>
            .stSlider>div>div>div>input {{
                border-radius: 15px;
                background-color: #ff6f61!important;  /* 强制应用颜色 */
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.slider(label, min_value, max_value, value, step)


def st_sidebar_slider(label, min_value, max_value, value, step):
    st.markdown(f"""
        <style>
            .stSlider>div>div>div>input {{
                border-radius: 15px;
                background-color: #ff6f61!important;  /* 强制应用颜色 */
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.sidebar.slider(label, min_value, max_value, value, step)


# Tags
def st_tags(tags):
    st.markdown(f"""
        <style>
            .tag {{
                background-color: #ff6f61!important;  /* 强制应用颜色 */
                color: white!important;  /* 强制应用颜色 */
                border-radius: 25px;
                padding: 8px 20px;
                margin: 6px;
                display: inline-block;
                font-size: 16px;
            }}
        </style>
        <div>
            {''.join([f'<span class="tag">{tag}</span>' for tag in tags])}
        </div>
    """, unsafe_allow_html=True)


# Button
def st_button(button_text):
    st.markdown(f"""
        <style>
            .stButton>button {{
                background-color: white!important;
                color: white;
                border: none;
                padding: 16px 32px;
                border-radius: 50px;
                font-size: 18px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            .stButton>button:hover {{
                background-color: #e04e3f;
                box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.1);
            }}
        </style>
    """, unsafe_allow_html=False)
    st.button(button_text)


# Dataframe Table
def st_dataframe(df, height, width, use_container_width=True):
    st.markdown(f"""
        <style>
            .stDataFrame {{
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.1);
            }}
            table {{
                font-size: 18px;
                color: black!important;
                border-collapse: collapse;
                width: 100%;
                text-align: center;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
            }}
            th {{
                background-color: #ff6f61!important; /* 列标题背景色 */
                color: white!important; /* 列标题字体颜色 */
                text-align: center;
            }}
            td {{
                background-color: #fff!important; /* 单元格背景色 */
                text-align: center;
            }}
            tr:hover {{
                background-color: #f7f7f7!important;
                text-align: center;
            }}
            tbody tr th {{
                background-color: #ff6f61!important; /* 行标题背景色 */
                color: white!important; /* 行标题字体颜色 */
                text-align: center;
            }}
        </style>
    """, unsafe_allow_html=True)
    st.dataframe(df, height=400, width=500, use_container_width=use_container_width)


# Multi Select
def st_multiselect(label, options, default,label_visibility):
    st.markdown(f"""
        <style>
            .stMultiSelect>div>div>div {{
                border-radius: 0px;
                border: 2px solid grey!important;
                padding: 10px;
                font-size: 10px pink!important;
                background-color: white!important;
                transition: all 0.2s ease;
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.multiselect(label, options, default,label_visibility="hidden")


# Warning
def st_warning(warning_text):
    st.markdown(f"""
        <style>
            .stWarning {{
                font-size: 18px;
                background-color: #ffcc00;
                color: #333;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.1);
                margin-top: 30px;
            }}
        </style>
        <div class="stWarning">
            {warning_text}
        </div>
    """, unsafe_allow_html=True)


# Markdown
def st_markdown(markdown_text):
    st.markdown(markdown_text)


# Expander
def st_expander(card_title, card_content):
    with st.expander(card_title, expanded=False):
        st.markdown(f"""
        <style>
            .card {{
                background-color: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0px 6px 20px rgba(0, 0, 0, 0.1);
                margin-bottom: 40px;
            }}
            .card-title {{
                font-size: 28px;
                font-weight: 700;
                color: #ff6f61; /* 标题颜色 */
                margin-bottom: 20px;
            }}
            .card-content {{
                font-size: 18px;
                color: #777; /* 内容颜色 */
                line-height: 1.6; /* 行高 */
            }}
            .card-content ul {{
                list-style-type: disc; /* 列表样式 */
                margin-left: 20px;
            }}
            .card-content ul li {{
                margin-bottom: 10px; /* 列表项间距 */
            }}
        </style>
            {card_content}
        </div>
    """, unsafe_allow_html=True)


# LaTeX
def st_latex(latex_code):
    st.latex(latex_code)


def st_table(df):
    st.table(df)


import streamlit as st

# 定义全局样式
primary_color = "#ff6f61"
secondary_color = "#777"
background_color = "#fafafa"
font_family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"


# Header
def st_header(header_text):
    st.markdown(f"""
        <style>
            body {{
                background-color: {background_color};
                font-family: {font_family};
                color: #333;
            }}
            h1 {{
                font-size: 50px;
                color: black!important;
                font-weight: 700;
                text-align: center;
                margin-top: 60px;
                text-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                letter-spacing: 1.2px;
            }}
        </style>
        <h1>{header_text}</h1>
    """, unsafe_allow_html=True)


# Subheader
def st_subheader(subheader_text):
    st.markdown(f"""
        <style>
            h2 {{
                font-size: 26px;
                color: {primary_color}!important;
                font-weight: 600;
                text-align: left;
                text-shadow: 0px 3px 6px rgba(0, 0, 0, 0.05);
                margin-left: 20px;
                margin-top: 35px;
                letter-spacing: 1px;
            }}
        </style>
        <h2>{subheader_text}</h2>
    """, unsafe_allow_html=True)


# Card
def st_card(card_title, card_content):
    st.markdown(f"""
        <style>
            .card {{
                background-color: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0px 6px 20px rgba(0, 0, 0, 0.1);
                margin-bottom: 40px;
            }}
            .card-title {{
                font-size: 28px;
                font-weight: 700;
                color: {primary_color}!important;
                margin-bottom: 20px;
            }}
            .card-content {{
                font-size: 18px;
                color: {secondary_color}!important;
                line-height: 1.6;
            }}
            .card-content ul {{
                list-style-type: disc;
                margin-left: 20px;
            }}
            .card-content ul li {{
                margin-bottom: 10px;
            }}
        </style>
        <div class="card">
            <div class="card-title">{card_title}</div>
            <div class="card-content">{card_content}</div>
        </div>
    """, unsafe_allow_html=True)


# Text Input
def st_text_input(label):
    st.markdown(f"""
        <style>
            .stTextInput>div>div>input {{
                border-radius: 30px;
                border: 2px solid {primary_color}!important;
                padding: 12px;
                font-size: 18px;
                color: #333;
                background-color: #f9f9f9;
                transition: all 0.3s ease;
            }}
            .stTextInput>div>div>input:focus {{
                border-color: #e04e3f!important;
                box-shadow: 0 0 12px rgba(0, 0, 0, 0.1);
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.text_input(label)


# Text Area
def st_text_area(label):
    st.markdown(f"""
        <style>
            .stTextArea>div>textarea {{
                border-radius: 20px;
                border: 2px solid {primary_color}!important;
                padding: 14px;
                font-size: 18px;
                color: #333;
                background-color: #f9f9f9;
                transition: all 0.3s ease;
            }}
            .stTextArea>div>textarea:focus {{
                border-color: #e04e3f!important;
                box-shadow: 0 0 12px rgba(0, 0, 0, 0.1);
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.text_area(label)


# Select Box
def st_selectbox(label, options):
    st.markdown(f"""
        <style>
            .stSelectbox>div>div>div {{
                border-radius: 25px;
                border: 2px solid {primary_color}!important;
                padding: 12px;
                font-size: 18px;
                color: #333;
                background-color: #f9f9f9;
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.selectbox(label, options)


# Checkbox
def st_checkbox(label):
    st.markdown(f"""
        <style>
            .stCheckbox>div>div>label {{
                font-size: 20px;
                color: {primary_color}!important;
                font-weight: 600;
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.checkbox(label)


# Radio Buttons
def st_radio(label, options, index, horizontal):
    st.markdown(f"""
        <style>
            .stRadio>div>div>label {{
                font-size: 20px;
                color: {primary_color}!important;
                font-weight: 600;
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.radio(label, options, index=index, horizontal=horizontal)


# Slider
def st_slider(label, min_value, max_value, value, step):
    st.markdown(f"""
        <style>
            .stSlider>div>div>div>input {{
                border-radius: 15px;
                background-color: {primary_color}!important;
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.slider(label, min_value, max_value, value, step)


# Multi Select
def st_multiselect(label, options, default):
    st.markdown(f"""
        <style>
            .stMultiSelect>div>div>div {{
                border-radius: 10px;
                border: 2px solid {primary_color}!important;
                padding: 10px;
                font-size: 16px;
                color: #333;
                background-color: #f9f9f9;
                transition: all 0.2s ease;
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.multiselect(label, options, default)


# File Upload
def st_file_uploader(content, type,label_visibility="collapsed"):
    st.markdown(f"""
        <style>
            .stFileUploader>div>div {{
                border-radius: 10px;
                background-color: #f9f9f9!important;
                padding: 10px;
                font-size: 18px;
                color: #333;
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.file_uploader(content, type, label_visibility="collapsed")


# Warning
def st_warning(warning_text):
    st.markdown(f"""
        <style>
            .stWarning {{
                font-size: 18px;
                background-color: #ffcc00;
                color: #333;
                padding: 15px;
                
                border-radius: 10px;
                box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.1);
                margin-top: 30px;
            }}
        </style>
        <div class="stWarning">
            {warning_text}
        </div>
    """, unsafe_allow_html=True)


# Dataframe Table
def st_dataframe(df, height=400, width=500, use_container_width=True):
    st.markdown(f"""
        <style>
            .stDataFrame {{
                border-radius: 15 px;
                overflow: hidden;
                box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.1);
            }}
            table {{
                font-size: 18px;
                color: black!important;
                border-collapse: collapse;
                width: 100%;
                text-align: center;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
            }}
            th {{
                background-color: {primary_color}!important;
                color: white!important;
                text-align: center;
            }}
            td {{
                background-color: #fff!important;
                text-align: center;
            }}
            tr:hover {{
                background-color: #f7f7f7!important;
                text-align: center;
            }}
            tbody tr th {{
                background-color: {primary_color}!important;
                color: white!important;
                text-align: center;
            }}
        </style>
    """, unsafe_allow_html=True)
    st.dataframe(df, height=height, width=width, use_container_width=use_container_width)


# Button
def st_button(button_text):
    st.markdown(f"""
        <style>
            .stButton>button {{
                background-color: {primary_color};
                color: white;
                border: none;
                padding: 16px 32px;
                border-radius: 50px;
                font-size: 18px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            .stButton>button:hover {{
                background-color: #e04e3f;
                box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.1);
            }}
        </style>
    """, unsafe_allow_html=True)
    return st.button(button_text)
