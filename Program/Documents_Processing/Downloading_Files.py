import os
import streamlit as st
import matplotlib.pyplot as plt
import math
import os
import sys

from Documents_Processing.Web_Format import st_radio, st_multiselect, st_markdown, st_latex, st_dataframe, st_subsubheader,st_text_input,st_button


current_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.dirname(current_dir)
# def Save_Form_to_Csv(df_name, df,autotext):
#     st.write(project_root)
#     # user_input_path =resources_directory
#     user_input_name = st.text_input("请输入" + df_name + "保存文件名",label_visibility="collapsed",value=autotext,).title()
#     if user_input_name and not user_input_name.endswith('.csv'):
#
#         user_input_name += '.csv'
#
#     file_name =user_input_path+user_input_name
#     st.write(file_name)
#     col5, col6 = st.columns([1, 2])
#     with col5:
#         if st_button("Download " + df_name + " Table File"):
#             df.to_csv(file_name, index=False, header=True)
#             with col6:
#                 st.success(f"🎉{df_name} 成果保存至：{ file_name } 文件！")
#                 st.snow()
#
#
