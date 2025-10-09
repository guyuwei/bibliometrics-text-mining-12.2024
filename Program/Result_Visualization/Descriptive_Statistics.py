import os
import sys

import pandas as pd

current_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.dirname(current_dir)
picture_path= os.path.join(os.getcwd(), 'output/picture')
sys.path.append(project_root)  # 添加项目根目录
sys.path.append(os.path.join(project_root, 'Calculate_Anaysis'))
sys.path.append(os.path.join(project_root, 'Documents_Processing'))
sys.path.append(os.path.join(project_root, 'Result_Visualization'))
from Documents_Processing.Web_Format import st_multiselect, st_dataframe


def Form_Information_Description(df):
    number_of_total_articles = df.shape[0]
    count_result = {}  # 数据库的info
    missing_value_columns = st_multiselect('选择需要统计的参数:', df.columns,
                                           default=df.columns[:8])
    if missing_value_columns:
        for para in missing_value_columns:
            count_result[para] = {"共计": str(len(df[para].value_counts())),
                                  "缺失值": str(number_of_total_articles - len(
                                      df[para].value_counts())),
                                  "参数类型": type(df[para][0]).__name__}
        count_result = pd.DataFrame(count_result).sort_index(axis=1)
        st_dataframe(count_result,height=100,width=400,use_container_width=True)

# 从修改后的表格提取出一层遍历的集合
def shift_edited_df_into_list(edited_df):
    data=edited_df.fillna("").values
    all_result=[]
    for row in data:
        all_result.extend(row)
    return all_result