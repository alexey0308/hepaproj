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
from dash.dependencies import Input, Output

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
        id="cellTypeSelector",
        options=[
            {'label':"hepatocytes", 'value': "hep"},
            {'label':"lsec", 'value': "lsec"},
        ], value="hep"
    )

@app.callback(
    Output("geneHeader", "children"),
    Input("geneSelector", "value")
)
def updateGeneHeader(gene):
    return "Gene: {}".format(gene)


def geneListDrop(genes, default=None):
    if default is None:
        default = genes[0]
    x = dcc.Dropdown(
        id="geneSelector",
        options=[{"label": x, "value": x} for x in genes],
        value=default)
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
d = DATA[cellType]
fig = plotGene(d["ann"].etaq,
               np.sqrt(d["fracs"][d["genes"] == gene,:].toarray()[0]),
               d["ann"].mouse)

@app.callback(
    Output("genePlot", "figure"),
    [Input("geneSelector", "value"), Input("cellTypeSelector", "value")])
def updateGeneFigure(gene, cellType):
    d = DATA[cellType]
    fig = plotGene(d["ann"].etaq,
                np.sqrt(d["fracs"][d["genes"] == gene,:].toarray()[0]),
                d["ann"].mouse)
    return fig


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H3(id="geneHeader",
                        children=gene,
                        style={'color': "dodgerblue"})
                ,dcc.Graph(id="genePlot")
                ,cellTypeDrop()
                ,geneListDrop(d["genes"])
                ,resultTable(d["detbl"])
            ], style={"width":"80%"}),
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
