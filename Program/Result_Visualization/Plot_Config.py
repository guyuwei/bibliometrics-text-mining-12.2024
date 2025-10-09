"""
matplotlib配置模块
提供统一的图表样式和配置设置
"""
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import numpy as np

class PlotConfig:
    """图表配置类"""
    
    def __init__(self):
        self.setup_matplotlib()
        self.setup_colors()
        self.setup_group_mapping()
    
    def setup_matplotlib(self):
        """设置matplotlib基础配置"""
        # 字体和基础设置
        plt.rcParams['font.family'] = 'Times New Roman'
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['axes.linewidth'] = 1.2
        
        # 字体大小
        plt.rcParams['axes.titlesize'] = 18
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['xtick.labelsize'] = 12
        plt.rcParams['ytick.labelsize'] = 12
        plt.rcParams['legend.fontsize'] = 12
        
        # 图表样式
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = 'white'
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['grid.linewidth'] = 0.5
        
        # 设置seaborn样式
        sns.set_style("whitegrid")
        sns.set_palette("husl")
    
    def setup_colors(self):
        """设置颜色方案"""
        # 主要颜色方案
        self.colors = {
            'primary': ['#B5A8CA', '#C0D6EA', '#E0BBD0'],  # SMS, MTC, AIVC
            'secondary': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
            'accent': ['#A8E6CF', '#FFD3A5', '#FFAAA5', '#FF8B94', '#C7CEEA'],
            'gradient': ['#667eea', '#764ba2', '#f093fb', '#f5576c']
        }
        
        # 创建颜色映射
        self.color_mapping = {
            'SMS': '#B5A8CA',
            'MTC': '#C0D6EA', 
            'AIVC': '#E0BBD0'
        }
    
    def setup_group_mapping(self):
        """设置组别映射"""
        self.group_mapping = {1: 'SMS', 2: 'MTC', 3: 'AIVC'}
        self.reverse_group_mapping = {v: k for k, v in self.group_mapping.items()}
    
    def get_color(self, group_name=None, index=None):
        """获取颜色"""
        if group_name and group_name in self.color_mapping:
            return self.color_mapping[group_name]
        elif index is not None:
            return self.colors['primary'][index % len(self.colors['primary'])]
        else:
            return self.colors['primary'][0]
    
    def get_group_name(self, group_id):
        """根据组别ID获取组别名称"""
        return self.group_mapping.get(group_id, f"Group_{group_id}")
    
    def get_group_id(self, group_name):
        """根据组别名称获取组别ID"""
        return self.reverse_group_mapping.get(group_name, None)
    
    def create_gradient_colors(self, n_colors):
        """创建渐变颜色"""
        if n_colors <= len(self.colors['gradient']):
            return self.colors['gradient'][:n_colors]
        else:
            # 生成更多渐变颜色
            colors = []
            for i in range(n_colors):
                ratio = i / (n_colors - 1)
                if ratio < 0.5:
                    # 从第一个颜色到第二个颜色
                    t = ratio * 2
                    color = self._interpolate_color(
                        self.colors['gradient'][0], 
                        self.colors['gradient'][1], 
                        t
                    )
                else:
                    # 从第二个颜色到第三个颜色
                    t = (ratio - 0.5) * 2
                    color = self._interpolate_color(
                        self.colors['gradient'][1], 
                        self.colors['gradient'][2], 
                        t
                    )
                colors.append(color)
            return colors
    
    def _interpolate_color(self, color1, color2, t):
        """在两个颜色之间插值"""
        # 将十六进制颜色转换为RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        interpolated = tuple(
            rgb1[i] + t * (rgb2[i] - rgb1[i]) for i in range(3)
        )
        
        return rgb_to_hex(interpolated)
    
    def apply_style(self, fig, title=None, xlabel=None, ylabel=None):
        """应用样式到图表"""
        if title:
            fig.suptitle(title, fontsize=20, fontweight='bold', y=0.98)
        
        # 设置坐标轴标签
        if hasattr(fig, 'get_axes'):
            axes = fig.get_axes()
            for ax in axes:
                if xlabel:
                    ax.set_xlabel(xlabel, fontsize=14, fontweight='bold')
                if ylabel:
                    ax.set_ylabel(ylabel, fontsize=14, fontweight='bold')
                
                # 设置网格
                ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
                
                # 设置边框
                for spine in ax.spines.values():
                    spine.set_linewidth(1.2)
        
        return fig

# 创建全局配置实例
plot_config = PlotConfig()

def get_plot_config():
    """获取图表配置实例"""
    return plot_config

def apply_matplotlib_style():
    """应用matplotlib样式"""
    plot_config.setup_matplotlib()

def get_colors(scheme='primary', n_colors=None):
    """获取颜色方案"""
    if n_colors is None:
        return plot_config.colors[scheme]
    else:
        if scheme == 'gradient':
            return plot_config.create_gradient_colors(n_colors)
        else:
            base_colors = plot_config.colors[scheme]
            if n_colors <= len(base_colors):
                return base_colors[:n_colors]
            else:
                # 重复颜色
                return (base_colors * ((n_colors // len(base_colors)) + 1))[:n_colors]






