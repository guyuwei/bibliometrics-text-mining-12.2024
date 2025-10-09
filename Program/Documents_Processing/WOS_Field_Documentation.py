"""
WOS字段文档页面
提供Web of Science字段的详细说明和帮助信息
"""

import streamlit as st
import pandas as pd
from typing import Dict, List

def display_wos_field_documentation():
    """显示WOS字段文档页面"""
    
    st.title("📚 Web of Science 字段文档")
    st.markdown("---")
    
    # 字段分类
    field_categories = {
        "基本标识字段": {
            "FN": "文件名 - Web of Science导出文件的标识",
            "VR": "版本号 - 导出文件的版本信息", 
            "PT": "出版物类型 - J=期刊文章, B=书籍, S=丛书, P=专利等",
            "UT": "入藏号 - Web of Science唯一标识符",
            "AR": "文章编号 - 文章的唯一编号"
        },
        "作者相关字段": {
            "AU": "作者 - 文章作者列表",
            "AF": "作者全名 - 作者完整姓名",
            "BA": "书籍作者 - 书籍的作者",
            "BF": "书籍作者全名 - 书籍作者的完整姓名",
            "CA": "团体作者 - 机构或组织作为作者",
            "GP": "书籍团体作者 - 书籍的团体作者",
            "RI": "ResearcherID号 - 研究者的唯一标识",
            "OR": "ORCID号 - 开放研究者身份标识"
        },
        "标题和摘要": {
            "TI": "文献标题 - 文章的标题",
            "AB": "摘要 - 文章摘要",
            "MA": "会议摘要 - 会议论文摘要"
        },
        "期刊和出版物信息": {
            "SO": "出版物名称 - 期刊或书籍名称",
            "J9": "期刊名称缩写 - 期刊的缩写形式",
            "JI": "ISO期刊名称缩写 - 国际标准期刊名称缩写",
            "SN": "ISSN - 国际标准期刊号",
            "EI": "eISSN - 电子版国际标准期刊号",
            "BN": "ISBN - 国际标准书号"
        },
        "出版信息": {
            "PY": "出版年 - 文章发表年份",
            "PD": "出版日期 - 具体发表日期",
            "VL": "卷 - 期刊卷号",
            "IS": "期 - 期刊期号",
            "BP": "开始页 - 文章起始页码",
            "EP": "结束页 - 文章结束页码",
            "PG": "页数 - 文章总页数",
            "DI": "DOI - 数字对象标识符",
            "D2": "书籍DOI - 书籍的数字对象标识符"
        },
        "出版商信息": {
            "PU": "出版商 - 出版机构名称",
            "PI": "出版商所在城市 - 出版商所在城市",
            "PA": "出版商地址 - 出版商详细地址",
            "PN": "子辑 - 期刊的子辑信息"
        },
        "关键词和主题": {
            "DE": "作者关键词 - 作者提供的关键词",
            "ID": "Keywords Plus - Web of Science自动提取的关键词",
            "WC": "Web of Science类别 - 文章所属学科类别",
            "SC": "研究方向 - 文章的研究领域"
        },
        "地址信息": {
            "C1": "作者地址 - 作者所属机构地址",
            "RP": "通讯作者地址 - 通讯作者的联系地址",
            "EM": "电子邮件地址 - 作者邮箱地址"
        },
        "会议信息": {
            "CT": "会议标题 - 会议名称",
            "CY": "会议日期 - 会议举办日期",
            "CL": "会议地点 - 会议举办地点",
            "HO": "会议主办方 - 会议主办机构",
            "SP": "会议赞助方 - 会议赞助机构"
        },
        "引用信息": {
            "CR": "参考文献 - 文章引用的参考文献列表",
            "NR": "参考文献数 - 参考文献的总数量",
            "TC": "被引频次 - 文章被引用的次数",
            "Z9": "被引频次合计 - 总被引频次",
            "U1": "使用次数(最近180天) - 最近180天的使用次数",
            "U2": "使用次数(2013年至今) - 2013年至今的使用次数"
        },
        "基金信息": {
            "FU": "基金资助机构和授权号 - 资助机构信息",
            "FX": "基金资助正文 - 资助项目的详细描述"
        },
        "其他信息": {
            "LA": "语种 - 文章使用的语言",
            "DT": "文献类型 - 文章的具体类型",
            "OA": "公开访问指示符 - 开放获取状态",
            "PM": "PubMed ID - PubMed数据库标识符",
            "GA": "文献传递号 - 文献传递服务编号",
            "SE": "丛书标题 - 丛书名称",
            "SI": "特刊 - 特刊信息",
            "DA": "生成此报告的日期 - 报告生成日期",
            "EA": "提前访问日期 - 提前在线发表日期",
            "EY": "提前访问年份 - 提前在线发表年份",
            "ES": "ESI热门论文 - 高被引论文标识",
            "ET": "ESI常被引用的论文 - 常被引论文标识",
            "WE": "数据库 - 数据来源数据库"
        }
    }
    
    # 创建侧边栏导航
    st.sidebar.title("📖 字段分类")
    selected_category = st.sidebar.selectbox(
        "选择字段分类",
        list(field_categories.keys())
    )
    
    # 显示选中的分类
    st.subheader(f"📋 {selected_category}")
    
    # 创建字段表格
    fields_data = []
    for field_code, description in field_categories[selected_category].items():
        fields_data.append({
            "字段代码": field_code,
            "字段名称": description.split(" - ")[0],
            "详细说明": description.split(" - ")[1] if " - " in description else description
        })
    
    df = pd.DataFrame(fields_data)
    st.dataframe(df, use_container_width=True)
    
    # 添加使用说明
    st.markdown("---")
    st.subheader("💡 使用说明")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔍 字段查找技巧：**
        - 使用侧边栏选择字段分类
        - 字段代码通常为2-3个字母
        - 字段名称采用中文描述
        - 详细说明包含具体含义
        """)
    
    with col2:
        st.markdown("""
        **📊 数据解析说明：**
        - 多值字段用分号(;)分隔
        - 数值字段自动转换为数字类型
        - 日期字段自动解析为日期格式
        - 空值用NaN表示
        """)
    
    # 添加常见问题
    st.markdown("---")
    st.subheader("❓ 常见问题")
    
    with st.expander("为什么有些字段为空？"):
        st.markdown("""
        字段为空的原因可能包括：
        - 原始数据中该字段确实为空
        - 字段名称不匹配导致解析失败
        - 数据格式不符合WOS标准
        - 文件编码问题导致解析错误
        """)
    
    with st.expander("如何处理多作者信息？"):
        st.markdown("""
        多作者信息的处理方式：
        - AU字段：用分号分隔多个作者
        - AF字段：用分号分隔多个作者全名
        - C1字段：用分号分隔多个地址
        - 建议在分析时先分割这些字段
        """)
    
    with st.expander("引用数据如何理解？"):
        st.markdown("""
        引用相关字段说明：
        - TC：当前被引频次
        - Z9：总被引频次
        - U1：最近180天使用次数
        - U2：2013年至今使用次数
        - 这些数据反映文章的影响力
        """)

def get_field_examples() -> Dict[str, List[str]]:
    """获取字段示例数据"""
    return {
        "AU": ["Smith, J", "Johnson, A", "Brown, M"],
        "TI": ["Digital Twin Technology in Construction Industry"],
        "SO": ["Journal of Building Engineering"],
        "PY": ["2024"],
        "DE": ["digital twin", "construction", "building information modeling"],
        "TC": ["15"],
        "C1": ["[Smith, J] Univ Technol, Sydney, NSW, Australia", "[Johnson, A] MIT, Cambridge, MA USA"]
    }

def display_field_examples():
    """显示字段示例"""
    st.subheader("📝 字段示例")
    
    examples = get_field_examples()
    
    for field_code, example_values in examples.items():
        st.markdown(f"**{field_code} 字段示例：**")
        for value in example_values:
            st.code(value)
        st.markdown("---")
