import dash_core_components as dcc
import dash
import plotly.express as px
import dash_html_components as html
import pandas as pd
import os
from .plots import plotGene
import dash_table
from  .dataimport import getCellAnno, getFracs, getGenes, getDETable
import yaml

with open("src/config.yaml") as file:
    config = yaml.safe_load(file)

datadir = config["datadir"]

app = dash.Dash()
dash.Dash(name=__name__)
server = app.server


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
        data=tbl.iloc[1:30,:].to_dict("records"),
        columns=[{'id':c, 'name':c} for c in tbl.columns],
        page_size=100,
        filter_action="native",
        sort_action="native"
    )
    return dt

cellType = "hep"
ann = getCellAnno(datadir, cellType).iloc[0:200,:]
genes =  getGenes(datadir, cellType)[0:10]
fracs =  getFracs(datadir, cellType)
tbl =  getDETable(datadir, cellType)

app.layout = html.Div(children=[
    html.H2("Hepatocytes", style={'color': "dodgerblue"}, className="pageh2")
    ,cellTypeDrop()
    ,geneListDrop(genes)
    ,resultTable(tbl)
], style={"width":"50%"})

if __name__ == '__main__':
    app.run_server(debug=True)
