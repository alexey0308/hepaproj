import dash_core_components as dcc
import dash
import plotly.express as px

def plotGene(etaq, values, groups):
    # import pdb; pdb.set_trace()
    fig = px.scatter(x = etaq, y = values, color=groups)
    return dcc.Graph(figure=fig)
