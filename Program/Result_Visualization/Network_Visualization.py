import plotly.graph_objects as go


def draw_network_visualization(nodes_df, edges_df):
    fig = go.Figure()

    # 添加边
    for _, row in edges_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["source"], row["target"], None],
            y=[1, 1, None],
            mode="lines",
            line=dict(width=row["weight"] / 2, color="#888"),
            hoverinfo="none"
        ))

    # 添加节点
    fig.add_trace(go.Scatter(
        x=nodes_df["node"],
        y=[1] * len(nodes_df),
        mode="markers+text",
        marker=dict(
            size=nodes_df["size"],
            color="#007bff",
            line=dict(width=2, color="DarkSlateGrey")
        ),
        text=nodes_df["node"],
        textposition="top center"
    ))

    fig.update_layout(
        showlegend=False,
        hovermode="closest",
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False)
    )

    return fig


# 可视化函数：绘制作者耦合网络图
def draw_author_network(nodes, edges):
    """
    绘制作者耦合网络图
    :param nodes: 节点数据（作者列表）
    :param edges: 边数据（source, target, weight）
    :return: Plotly Figure对象
    """
    # 创建节点数据
    node_trace = go.Scatter(
        x=[], y=[],  # 节点位置
        text=[],  # 节点标签
        mode="markers+text",
        hoverinfo="text",
        marker=dict(
            size=10,
            color="#007bff",
            line=dict(width=2, color="DarkSlateGrey")
        )
    )

    # 创建边数据
    edge_trace = go.Scatter(
        x=[], y=[],  # 边的起点和终点
        line=dict(width=1, color="#888"),
        hoverinfo="none",
        mode="lines"
    )

    # 添加节点和边的位置信息
    for node in nodes:
        node_trace["x"] += (node["x"],)
        node_trace["y"] += (node["y"],)
        node_trace["text"] += (node["name"],)

    for edge in edges:
        x0, y0 = edge["source"]["x"], edge["source"]["y"]
        x1, y1 = edge["target"]["x"], edge["target"]["y"]
        edge_trace["x"] += (x0, x1, None)
        edge_trace["y"] += (y0, y1, None)

    # 创建图
    fig = go.Figure(data=[edge_trace, node_trace])

    # 更新布局
    fig.update_layout(
        showlegend=False,
        hovermode="closest",
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False)
    )

    return fig