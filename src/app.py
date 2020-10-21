import dash_core_components as dcc
import dash
import plotly.express as px
import dash_html_components as html
import pandas as pd
import os
import dash_table
from  dataimport import getCellAnno, getFracs, getGenes, getDETable

app = dash.Dash()
dash.Dash(name=__name__)

def x2labels(x):
    return [{'label':y, 'value':y} for y in x]

def cellTypeDrop():
    return dcc.Dropdown(
        options=[
            {'label':"hepatocytes", 'value': "hep"},
            {'label':"lsec", 'value': "lsec"},
        ]
    )

def geneListDrop(genes):
    x = dcc.Dropdown(
        options=[{"label": x, "value": x} for x in genes])
    return x

def resultTable(tbl):
    dt = dash_table.DataTable(
        data=tbl.to_dict("records"),
        columns=[{'id':c, 'name':c} for c in tbl.columns],
        page_size=100
    )
    return dt

ann = getCellAnno(cellType="hep")
genes = getGenes(cellType="hep")
# fracs = getFracs(cellType="hep")
tbl = getDETable(cellType="hep")

app.layout = html.Div(children=[
    html.H2("Hepatocytes", style={'color': "dodgerblue"}, className="pageh2")
    ,cellTypeDrop()
    ,geneListDrop(genes)
    ,resultTable(tbl)
], className='two columns')

if __name__ == '__main__':
    app.run_server(debug=True)
