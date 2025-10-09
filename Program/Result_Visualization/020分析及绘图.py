import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import scienceplots
# 设置中文字体（如果需要）
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 使用科学绘图风格
plt.style.use ('science')

# 读取整理后的国家逐年统计数据
country_year_stats = pd.read_csv("../../output/country_year_stats.csv")

# 计算每个国家的总出版物数量，并排序
total_articles_per_country = country_year_stats.groupby('Country')['Articles_Count'].sum().reset_index()
top_countries = total_articles_per_country.nlargest(5, 'Articles_Count')['Country']

# 绘制每个国家逐年的文章数量
plt.figure(figsize=(20, 10))

# 为前五位国家绘制折线图
for country in top_countries:
    country_data = country_year_stats[country_year_stats['Country'] == country]
    plt.plot(country_data['YearPublished'], country_data['Articles_Count'], marker='o', label=country, linewidth=2)

# 设置标题和坐标轴标签为英文
plt.title("Top 5 Countries by Number of Articles per Year", fontsize=16, fontweight='bold')
plt.xlabel("Year", fontsize=14)
plt.ylabel("Number of Articles", fontsize=14)
plt.xticks(rotation=45, fontsize=12)
plt.yticks(fontsize=12)
plt.legend(title='Country', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)

# 添加数据标签
for country in top_countries:
    country_data = country_year_stats[country_year_stats['Country'] == country]
    for i in range(len(country_data)):
        plt.text(country_data['YearPublished'].iloc[i], country_data['Articles_Count'].iloc[i] + 0.5,  # 添加偏移量
                 str(country_data['Articles_Count'].iloc[i]), fontsize=10, ha='center', va='bottom')

# 显示图表
plt.tight_layout()  # 自动调整布局
plt.show()