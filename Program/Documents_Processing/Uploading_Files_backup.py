from collections import defaultdict

import streamlit as st
import pandas as pd
import bibtexparser
import re

def Extract_Info_From_Refine(df_refine):
    """处理Refine文件生成统计数据和正则优化模式"""
    count_columns = [col for col in df_refine.columns if col.endswith('_Count')]
    refine_stats = defaultdict(dict)
    regex_patterns = {}

    for col in count_columns:
        main_attr = col[:-6]
        valid_values = df_refine[~df_refine[main_attr].isna()][main_attr].unique()
        # 生成正则优化模式（按出现频率排序）
        sorted_values = sorted(valid_values, key=lambda x: -df_refine[df_refine[main_attr] == x][col].sum())
        regex_patterns[main_attr] = r'(' + '|'.join(re.escape(str(v)) for v in sorted_values) + r')'
        # 存储统计数据
        refine_stats[main_attr] = {
            'values': df_refine[[main_attr, col]].dropna().values.tolist(),
            'total': df_refine[col].sum()
        }

    return {'stats': refine_stats, 'regex': regex_patterns}


def Extract_Info_From_TXT(text):
    info_list=[]
    current_info = {}
    lines = text.splitlines()
    current_field = None
    current_content = []
    Filename=None
    Versionnumber=None
    for line in lines:
        # FN 文件名,VR 版本号,,EF 文件结束
        if line.startswith("FN ") :
            Filename = line[3:].strip()  # 文件名
        elif line.startswith("VR ") :
            Versionnumber = line[3:].strip()  # 版本号
        #AB 摘要，AR 文献编号，AU 作者，AF 作者全名
        if line.startswith("AB "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "摘要"
            current_content = [line[3:].strip()]
        elif line.startswith("AU "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "作者"
            current_content = [line[3:].strip()]
        elif line.startswith("AF "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "作者全名"
        elif line.startswith("AR "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "文章编号"
            current_content = [line[3:].strip()]
        # BA 书籍作者， BF 书籍作者全名， BE 编者，BN 国际标准书号 (ISBN)，BP 开始页，BS 丛书副标题
        elif line.startswith("BA "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "书籍作者"
            current_content = [line[3:].strip()]
        elif line.startswith("BF "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "作者全名"
            current_content = [line[3:].strip()]
        elif line.startswith("BE "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "编者"
            current_content = [line[3:].strip()]
        elif line.startswith("BN "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "国际标准书号 (ISBN)"
            current_content = [line[3:].strip()]
        elif line.startswith("BP "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "开始页页码"
            current_content = [line[3:].strip()]
        elif line.startswith("BS "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "丛书副标题"
            current_content = [line[3:].strip()]
        #CA团体作者，CT会议标题，CY会议日期，CL，会议地点，CR 引用的参考文献，C1作者地址
        elif line.startswith("C1 "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "作者地址"
            current_content = [line[3:].strip()]
        elif line.startswith("CA "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "团体作者"
            current_content = [line[3:].strip()]
        elif line.startswith("CT "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "会议标题"
            current_content = [line[3:].strip()]
        elif line.startswith("CY "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "会议日期"
            current_content = [line[3:].strip()]
        elif line.startswith("CL "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "会议地点"
            current_content = [line[3:].strip()]
        elif line.startswith("CR "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "引用的参考文献"
            current_content = [line[3:].strip()]
        #DA 生成此报告的日期，DE 作者关键词，DI 数字对象标识符 (DOI)，D2 书籍的数字对象标识符 (DOI)，DT 文献类型
        elif line.startswith("DA "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "生成此报告的日期"
            current_content = [line[3:].strip()]
        elif line.startswith("DE "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "作者关键词"
            current_content = [line[3:].strip()]
        elif line.startswith("DI "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "数字对象标识符 (DOI)"
            current_content = [line[3:].strip()]
        elif line.startswith("D2 "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "书籍的数字对象标识符 (DOI)"
            current_content = [line[3:].strip()]
        elif line.startswith("DT "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "文献类型"
            current_content = [line[3:].strip()]
        # EA 提前访问日期，EI 电子国际标准期刊号 (eISSN)，EM 电子邮件地址，EP 结束页，ER 记录结束，EF 文件结束，ES ESI 热门论文。
        # ET ESI 常被引用的论文，EY 提前访问年份
        elif line.startswith("EA "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "提前访问日期"
            current_content = [line[3:].strip()]
        elif line.startswith("EI "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "电子国际标准期刊号 (eISSN)"
            current_content = [line[3:].strip()]
        elif line.startswith("EM "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "电子邮件地址"
            current_content = [line[3:].strip()]
        elif line.startswith("EP "):
                if current_field:
                    current_info[current_field] = " ".join(current_content).strip()
                current_field = "结束页"
                current_content = [line[3:].strip()]
        elif line.startswith("ES "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "ES热门"
            current_content = [line[3:].strip()]
        elif line.startswith("ET "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "ES常被引用的论文"
            current_content = [line[3:].strip()]
        elif line.startswith("EY "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "提前访问年份"
            current_content = [line[3:].strip()]
        #FU基金资助机构和授权号，FX基金资助正文
        elif line.startswith("FU "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "基金资助机构和授权号"
            current_content = [line[3:].strip()]
        elif line.startswith("FX "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "基金资助正文"
            current_content = [line[3:].strip()]
        #GA文献传递号，GP 书籍团体作者
        elif line.startswith("GA "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "文献传递号"
            current_content = [line[3:].strip()]
        elif line.startswith("GP "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "BookGroupAuthors"
            current_content = [line[3:].strip()]
        #HO 会议主办方,ID Keywords Plus®,IS 期,JI ISO 来源文献名称缩写,J9 长度为 29 个字符的来源文献名称缩写
        elif line.startswith("HO "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "ConferenceHost"
            current_content = [line[3:].strip()]
        elif line.startswith("ID "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "Keywords Plus®"
            current_content = [line[3:].strip()]
        elif line.startswith("IS "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "期"
            current_content = [line[3:].strip()]
        elif line.startswith("JI "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "ISO 来源文献名称缩写"
            current_content = [line[3:].strip()]
        elif line.startswith("J9 "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "长度为 29 个字符的来源文献名称缩写"
            current_content = [line[3:].strip()]
        #LA 语种,MA 会议摘要,NR 引用的参考文献数
        elif line.startswith("LA "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "语种"
            current_content = [line[3:].strip()]
        elif line.startswith("MA "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "会议摘要"
            current_content = [line[3:].strip()]
        elif line.startswith("NR "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "引用的参考文献数"
            current_content = [line[3:].strip()]
        #OA 公开访问指示符，PA 出版商地址，PI 出版商所在城市，PN 子辑，PM PubMed ID，PT 出版物类型（J=期刊；B=书籍；S=丛书；P=专利），
        #PU 出版商，PY 出版年
        elif line.startswith("OA "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "公开访问指示符"
            current_content = [line[3:].strip()]
        elif line.startswith("PA "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "出版商地址"
            current_content = [line[3:].strip()]
        elif line.startswith("PI "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "出版商所在城市"
            current_content = [line[3:].strip()]
        elif line.startswith("PN "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "子辑"
            current_content = [line[3:].strip()]
        elif line.startswith("PM "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "PubMed ID"
            current_content = [line[3:].strip()]
        elif line.startswith("PT "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "出版物类型"
            current_content = [line[3:].strip()]
        elif line.startswith("PU "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "出版商"
            current_content = [line[3:].strip()]
        elif line.startswith("PY "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "出版年"
            current_content = [line[3:].strip()]
        #RI ResearcherID 号，RP 通讯作者地址
        elif line.startswith("RI "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "ResearcherID 号"
            current_content = [line[3:].strip()]
        elif line.startswith("RP "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "通讯作者地址"
            current_content = [line[3:].strip()]
        #SC 研究方向，SE 丛书标题，SI 特刊，SN 国际标准期刊号 (ISSN)，SO 出版物名称，SP 会议赞助方，
        elif line.startswith("SC "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "研究方向"
            current_content = [line[3:].strip()]
        elif line.startswith("SE "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "丛书标题"
            current_content = [line[3:].strip()]
        elif line.startswith("SI "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "特刊"
            current_content = [line[3:].strip()]
        elif line.startswith("SN "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "国际标准期刊号 (ISSN)"
            current_content = [line[3:].strip()]
        elif line.startswith("SO "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "出版物名称"
            current_content = [line[3:].strip()]
        elif line.startswith("SP "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "会议赞助方"
            current_content = [line[3:].strip()]
        #TC Web of Science 核心合集的被引频次计数，TI 文献标题
        elif line.startswith("TC "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = '核心合集的被引频次计数'
            current_content = [line[3:].strip()]
        elif line.startswith("TI "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "文献标题"
            current_content = [line[3:].strip()]
        #U1 使用次数（最近 180 天）,U2 使用次数（2013 年至今）,UT 入藏号
        elif line.startswith("U1 "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "使用次数（最近 180 天）"
            current_content = [line[3:].strip()]
        elif line.startswith("U2 "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "使用次数（2013 年至今"
            current_content = [line[3:].strip()]
        elif line.startswith("UT "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "入藏号"
            current_content = [line[3:].strip()]
        #VL 卷,WC Web of Science 类别,
        elif line.startswith("VL "):
                if current_field:
                    current_info[current_field] = " ".join(current_content).strip()
                current_field = "卷"
                current_content = [line[3:].strip()]
        elif line.startswith("WC "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "Web of Science 类别"
            current_content = [line[3:].strip()]
        #Z9 被引频次合计
        elif line.startswith("Z9 "):
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            current_field = "被引频次合计"
            current_content = [line[3:].strip()]
        elif line == "ER":
        # 当读取到文章结束标识时，将当前文章信息添加到列表中
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            info_list.append(current_info)
            current_info = {}
            current_field = None
            current_content = []

        elif line == "EF":
            # 当读取到文件结束标识时，返回文件名和文章信息列表
            if current_field:
                current_info[current_field] = " ".join(current_content).strip()
            if current_info:
                info_list.append(current_info)
            break

        else:
            if current_field:
                current_content.append(line.strip())

    # 处理最后一个字段
    if current_field and current_content:
        current_info[current_field] = " ".join(current_content).strip()
    if current_info:
        info_list.append(current_info)

    return Filename, Versionnumber, pd.DataFrame(info_list)



def  Parse_Bib_File(bib_text):
    # 解析BIB文件的函数
    bib_database = bibtexparser.lads(bib_text)
    entries = []
    fn_values = []

    for entry in bib_database.entries:
        # 处理每个条目的字段
        for field in entry:
            value = entry[field]
            if not value.startswith('{') and not value.endswith('}'):
                entry[field] = '{' + value + '}'

        # 提取Unique-ID作为FN值
        if 'Unique-ID' in entry:
            fn_values.append(entry['Unique-ID'])

        # 将处理后的条目添加到列表中
        entries.append(entry)

    return fn_values, entries

@st.cache_data
def Load_TXT(uploaded_file):
        if uploaded_file.name.endswith('.txt'):
            # 尝试多种编码方式读取文件
            try:
                data = uploaded_file.read().decode("utf-8")
            except UnicodeDecodeError:
                try:
                    # 重置文件指针
                    uploaded_file.seek(0)
                    data = uploaded_file.read().decode("utf-8-sig")  # 处理BOM
                except UnicodeDecodeError:
                    try:
                        uploaded_file.seek(0)
                        data = uploaded_file.read().decode("latin-1")  # 备用编码
                    except UnicodeDecodeError:
                        uploaded_file.seek(0)
                        data = uploaded_file.read().decode("cp1252")  # Windows编码
            filename, versionnumber, info_list = Extract_Info_From_TXT(data)
            fn_value = [filename, versionnumber]
        df = pd.DataFrame(info_list)
        df.columns = df.columns.str.title()
        return df


@st.cache_data()
def load_image(image_path):
    return image_path



@st.cache_data
def Load_CSV(uploaded_file):
    df = pd.read_csv(uploaded_file).dropna(how='all')
    df.columns = df.columns.str.title()
    return df

@st.cache_data
def Load_Refine(uploaded_file):
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file.dropna(how='all'))
        df.columns = df.columns.str.title()
        return df


