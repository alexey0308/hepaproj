import dash_core_components as dcc
import dash
import plotly.express as px
import numpy as np

def plotGeneScatter(etaq, values, groups):
    fig = px.scatter(x=etaq, y=values, color=groups,
                     labels={
                         "x":"central ➡ portal",
                         "y":"sqrt(umi/total)"
                     })
    fig.layout.xaxis.title.font.size = 20
    fig.layout.yaxis.title.font.size = 20
    fig.update_layout(legend=dict(
        yanchor="top", y=1, xanchor="right", x=.99))
    return fig

def plotGeneLines(etaq, values, mouse, groups):
    values = np.exp(values + np.log(1e4))
    values = np.sqrt(values)
    fig = px.line(x=etaq.values,
                  y=values.values,
                  color=groups,
                  line_group=mouse,
                  labels={
                      "x":"central ➡ portal",
                      "y":"sqrt(umi/total)"})
    fig.layout.xaxis.title.font.size = 20
    fig.layout.yaxis.title.font.size = 20
    fig.update_layout(legend=dict(
        yanchor="top", y=1, xanchor="right", x=.99))
    return fig
