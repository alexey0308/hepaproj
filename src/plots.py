import dash_core_components as dcc
import dash
import plotly.express as px

def plotGene():
    i = 0
    values = fracs[i, :].toarray()[0]
    etaq = ann["etaq"].values

    fig = px.scatter(x = etaq, y = values)
