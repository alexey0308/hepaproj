import dash_core_components as dcc
import dash
import numpy as np
import dash_html_components as html
import pandas as pd
import os
from plots import plotGene
import dash_table
from  dataimport import getCellAnno, getFracs, getGenes, getDETable
import yaml

with open("config.yaml") as file:
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
        data=tbl.to_dict("records"),
        columns=[{'id':c, 'name':c} for c in tbl.columns],
        page_size=100,
        filter_action="native",
        sort_action="native"
    )
    return dt

def readCellType(cellType, datadir):
    ann = getCellAnno(datadir, cellType)
    ann.mouse = pd.Categorical(ann.Genotype)
    genes =  getGenes(datadir, cellType)
    fracs =  getFracs(datadir, cellType)
    tbl =  getDETable(datadir, cellType)
    return {"ann":ann, "genes":genes, "fracs":fracs, "detbl":tbl}

DATA = {}
for cellType in ["hep", "lsec"]:
    DATA[cellType] = readCellType(cellType, datadir)

cellType = "hep"
gene = "0610040b10rik"
d =  DATA[cellType]
fig = plotGene(d["ann"].etaq,
               np.sqrt(d["fracs"][d["genes"] == gene,:].toarray()[0]),
               d["ann"].mouse)

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H2("Hepatocytes", style={'color': "dodgerblue"}, className="pageh2")
                ,fig
                ,cellTypeDrop()
                ,geneListDrop(d["genes"])
                ,resultTable(d["detbl"])
            ], style={"width":"80%"}),
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
