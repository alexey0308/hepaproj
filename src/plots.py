import dash_core_components as dcc
import dash
import plotly.express as px

def plotGene(etaq, values, groups):
    fig = px.scatter(x = etaq, y = values, color=groups)
    return fig
