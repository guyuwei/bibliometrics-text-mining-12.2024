import networkx as nx
import plotly.graph_objects as go
import streamlit as st
def draw_author_network_visualiaztion():
    G = nx.Graph()
    # 添加节点和边，这里只是一个示例
    edges = [
        ('作者A', '作者B'),
        ('作者B', '作者C'),
        # ('作者A', '作者C','作者B','作者D',),
        ('作者A', '作者C'),
        # ... 添加更多作者和合作关系
    ]
    G.add_edges_from(edges)

    # 使用布局算法确定节点位置
    pos = nx.spring_layout(G)

    # 创建节点的trace
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers+text',
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2)
    )

    # 创建边的trace
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    # 添加节点和边到trace
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += (x0, x1, None)
        edge_trace['y'] += (y0, y1, None)

    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += (x,)
        node_trace['y'] += (y,)
        node_trace['text'] += (node,)

    # 创建Plotly图表
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Author Collaboration Network',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(
                            # text="Vivian: <a href='https://plotly.com'> https://plotly.com </a>",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False))
                    )
    return fig
def draw_author_overlay_visualiaztion():
    G = nx.Graph()

    # 添加节点和边，节点属性包括作者名称、发表数量和研究领域
    edges = [
        ('作者A', '作者B'),
        ('作者B', '作者C'),
        ('作者A', '作者C'),
        # ... 添加更多合作关系
    ]

    # 假设的研究领域和颜色映射
    fields = ['领域1', '领域2', '领域3']
    field_colors = {'领域1': 'blue',
                    '领域2': 'green',
                    '领域3': 'red'}

    # 添加节点属性
    for author in ['作者A', '作者B', '作者C']:
        G.add_node(author, publications=10 + (
                author == '作者B'),
                   field=fields[author.count(
                       '作者') - 1])

    G.add_edges_from(edges)

    # 设置节点位置
    pos = nx.spring_layout(G)

    # 创建节点和边的数据
    node_x = []
    node_y = []
    node_info = []
    node_color = []
    node_size = []

    for node, (x, y) in pos.items():
        node_x.append(x)
        node_y.append(y)
        node_info.append(
            f"{node} - {G.nodes[node]['field']}")
        node_color.append(field_colors[
                              G.nodes[node][
                                  'field']])  # 使用领域映射到颜色
        node_size.append(G.nodes[node][
                             'publications'])  # 节点大小表示发表数量

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    # 创建 Plotly 图表
    fig = go.Figure()

    # 添加节点
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_info,
        marker=dict(
            size=node_size,  # 节点大小
            color=node_color,  # 节点颜色
            showscale=True,
            colorbar=dict(
                thickness=15,
                title='Research Field',
                xanchor='left',
                titleside='right'
            ),
            line_width=2)
    ))

    # 添加边
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=0.5, color='#888'),
        hoverinfo='none'
    ))

    # 更新布局
    fig.update_layout(
        title='Overlay Visualization of Author Collaboration Network',
        titlefont_size=16,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False,
                   zeroline=False,
                   showticklabels=False),
        yaxis=dict(showgrid=False,
                   zeroline=False,
                   showticklabels=False)
    )

    return fig

def draw_author_density_visualiaztion():
    # 创建一个空的无向图
    G = nx.Graph()

    # 添加节点和边，这里只是一个示例
    edges = [
        ('作者A', '作者B'),
        ('作者B', '作者C'),
        ('作者A', '作者C'),
        ('作者A', '作者D'),
        ('作者D', '作者E'),
        ('作者E', '作者F'),
        ('作者F', '作者C'),
        # ... 添加更多合作关系
    ]
    G.add_edges_from(edges)

    # 设置节点位置，使用不同的布局算法可以影响密度的视觉效果
    pos = nx.random_layout(G)  # 随机布局以增加密度感

    # 创建节点和边的数据
    node_x = []
    node_y = []
    edge_x = []
    edge_y = []

    # 为节点和边分配数据
    for node, (x, y) in pos.items():
        node_x.append(x)
        node_y.append(y)

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    # 创建 Plotly 图表
    fig = go.Figure()

    # 添加节点
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            size=5,  # 节点大小
            opacity=0.7,  # 节点透明度
            color='blue',  # 节点颜色
            showscale=False
        ),
        text=[f"{node}" for node in G.nodes()]
        # 节点标签
    ))

    # 添加边
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=0.5, color='#888',
                  dash='dot'),  # 边的样式
        hoverinfo='none'
    ))

    # 更新布局
    fig.update_layout(
        title='Density Visualization of Author Collaboration Network',
        titlefont_size=16,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False,
                   zeroline=False,
                   showticklabels=False),
        yaxis=dict(showgrid=False,
                   zeroline=False,
                   showticklabels=False),
        annotations=[dict(
            text="By Vivian: <a href='https://plotly.com'> https://plotly.com </a>",
            showarrow=False,
            xref="paper", yref="paper",
            x=0.005, y=-0.002
        )]
    )

    return fig