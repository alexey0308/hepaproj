import dash_core_components as dcc
import dash
import numpy as np
import dash_html_components as html
import pandas as pd
import os
from plots import plotGene
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


def x2labels(x):
    return [{'label':y, 'value':y} for y in x]

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


@app.callback(Output("geneListDrop", "options"), Input("cellTypeSelector", "value"))
def updateGeneList(cellType):
    genes = DATA[cellType]["genes"]
    options = [{"label": x, "value": x} for x in genes]
    return options


@app.callback(
    [Output("genePlot", "figure"), Output("geneHeader", "children")],
    [Input("geneListDrop", "value"), Input("cellTypeSelector", "value")])
def updateGeneFigure(gene, cellType):
    d = DATA[cellType]
    if (d["genes"] != gene).all():
        raise dash.exceptions.PreventUpdate
    fig = plotGene(d["ann"].etaq,
                np.sqrt(d["fracs"][d["genes"] == gene,:].toarray()[0]),
                d["ann"].mouse)
    return fig, "Gene: {}".format(gene)


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H3(id="geneHeader", style={'color': "dodgerblue"}),
                dcc.Graph(id="genePlot", style={"width": "800px", "height": "500px",
                                                "margin":"auto"}),
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
