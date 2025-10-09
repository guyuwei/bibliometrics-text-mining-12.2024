import matplotlib.pyplot as plt
import pandas as pd
import pylustrator
# 读取国家数据
file_countrymap = 'country.csv'
country_df = pd.read_csv(file_countrymap)
print(country_df.head(4))

# 将DataFrame转换为字典：
allcountry_dict = {}
for index, row in country_df.iterrows():
    country = row['Countries']
    allcountry_dict[country] = {
        'Year': int(row['Year']),  # 将年份取整
        'Publications': row['Publications'],
        'Citations': row['Citations']
    }
pylustrator.start()
# 绘制每个国家的 Publications 随时间变化的图表
plt.figure(figsize=(20,8))
for country, country_detail in allcountry_dict.items():
    print(country,"\n")
    print(country_detail,'\n')
    plt.plot(country_detail['Year'], country_detail['Publications'], marker='o', label=f"{country}")

# 设置标题和坐标轴标签
plt.title("Publications of Countries over Time")
plt.xlabel("Year")
plt.ylabel("Articles")

# 设置图例，标签按照两行排列在上方
# plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2)

# 显示网格
plt.grid(True)

# 显示图表
#% start: automatic generated code from pylustrator
plt.figure(1).ax_dict = {ax.get_label(): ax for ax in plt.figure(1).axes}
import matplotlib as mpl
getattr(plt.figure(1), '_pylustrator_init', lambda: ...)()
plt.figure(1).axes[0].set(position=[0.07321, 0.4052, 0.8707, 0.4836], xlim=(2020., 2025.), ylim=(0., 100.))
#% end: automatic generated code from pylustrator
plt.show()
