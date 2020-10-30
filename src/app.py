import dash_core_components as dcc
import dash
import numpy as np
import dash_html_components as html
import pandas as pd
import os
from plots import plotGeneScatter, plotGeneLines
import dash_table
from  dataimport import readAll
import yaml
from dash.dependencies import Input, Output

with open("config.yaml") as file:
    config = yaml.safe_load(file)


datadir = config["datadir"]
DATA = readAll(datadir)
import flask; print(flask.helpers.get_root_path(__name__))
app = dash.Dash(name=__name__, assets_folder="assets")
server = app.server
print(app.config)


def cellTypeDrop():
    return dcc.RadioItems(
        id="cellTypeSelector",
        options=[
            {'label':"hepatocytes", 'value': "hep"},
            {'label':"lsec", 'value': "lsec"},
        ], value="hep")


def resultTable():
    dt = dash_table.DataTable(
        id="resultTable",
        page_size=30,
        filter_action="native",
        sort_action="native"
    )
    return dt

@app.callback([Output("resultTable", "data"), Output("resultTable", "columns")],
              Input("cellTypeSelector", "value"))
def updateResultTable(cellType):
    tbl = DATA[cellType]["detbl"]
    data=tbl.to_dict("records")
    columns=[{'id':c, 'name':c} for c in tbl.columns]
    return data, columns


@app.callback(Output("geneListDrop", "options"),
              Input("cellTypeSelector", "value"))
def updateGeneList(cellType):
    genes = DATA[cellType]["genes"]
    options = [{"label": x, "value": x} for x in genes]
    return options


@app.callback(
    [Output("genePlotScatter", "figure"), Output("geneHeader", "children")],
    [Input("geneListDrop", "value"), Input("cellTypeSelector", "value")])
def updateGeneScatterFigure(gene, cellType):
    d = DATA[cellType]
    if (d["genes"] != gene).all():
        raise dash.exceptions.PreventUpdate
    fig = plotGeneScatter(d["ann"].etaq,
                np.sqrt(d["fracs"][d["genes"] == gene,:].toarray()[0]),
                d["ann"].mouse)
    return fig, "Gene: {}".format(gene)


@app.callback(
    Output("genePlotLines", "figure"),
    [Input("geneListDrop", "value"), Input("cellTypeSelector", "value")])
def updateGeneLineFigure(gene, cellType):
    d = DATA[cellType]
    if (d["genes"] != gene).all():
        raise dash.exceptions.PreventUpdate
    fig = plotGeneLines(d["ann"].etaq,
                np.sqrt(d["fracs"][d["genes"] == gene,:].toarray()[0]),
                d["ann"].mouse)
    return fig



app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H3(id="geneHeader", style={'color': "dodgerblue"}),
                html.Div(id="figures", children=[
                    dcc.Graph(id="genePlotScatter",
                              style={"width": "45%", "min-width": "400px"}),
                    dcc.Graph(id="genePlotLines",
                              style={"width": "45%", "min-width": "400px"})
                ], style={"height": "500px", "margin":"auto",
                          "display": "flex"}),
                html.Div(
                    children=[cellTypeDrop(), dcc.Dropdown(id="geneListDrop")],
                    id="selectorsContainer"
                ),
                html.H3("Comparison along the central(0.0)-portal(1.0) axis"),
                resultTable()
            ], style={"width":"80%", "margin":"auto"}),
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
