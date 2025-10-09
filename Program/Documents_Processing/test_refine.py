excel_file="/Users/gyw/Desktop/Project/2025/zyj_text_mining/000开发用/refine.xlsx"
import pandas as pd
df=pd.read_excel(excel_file)



# 提取所有包含“_Count”的列名
count_columns = [col for col in df.columns if col.endswith('_Count')]
print(count_columns)
# 构建包含所有三级属性的元组
result = []
for col in count_columns:
    # 提取对应的主属性名称（去掉“_Count”）
    main_attribute = col[:-6]  # 去掉最后6个字符（_Count）
    # 获取主属性和计数列的值
    sub_attributes = df[main_attribute].values
    counts = df[col].values
    # 将每个主属性、子属性和计数值组合成元组，同时过滤掉NaN值
    for sub_attribute, count in zip(sub_attributes, counts):
        if pd.notna(sub_attribute) and pd.notna(count):  # 检查是否为NaN
            result.append((main_attribute, sub_attribute, count))

# 将结果转换为元组
result_tuple = tuple(result)
# 查询特定属性的数量
def query_attribute_count(result_tuple, main_attribute, sub_attribute):
    for item in result_tuple:
        if item[0] == main_attribute and item[1] == sub_attribute:
            return item[2]  # 返回对应的数量
    return None  # 如果没有找到匹配项，返回 None
[main_attribute,sub_attribute]=input("please enter main attribute, sub attribute,spllit by space").split(" ")
print(query_attribute_count(result_tuple, main_attribute, int(sub_attribute)))