import dash_core_components as dcc
from flask import request
import re
import dash
import numpy as np
import dash_html_components as html
import pandas as pd
import os
from .plots import plotGeneScatter, plotGeneLines
import dash_table
from  .dataimport import readAll, readSpline, getGeneBetas, getMouseSplines
import yaml
from dash.dependencies import Input, Output
from .reporting import createGenesZip
# from . import reporting


datadir = os.environ.get("HEPAPP_DATA", default="data")
DATA = readAll(datadir)
SPLINE = readSpline(datadir)

import flask; print(flask.helpers.get_root_path(__name__))
app = dash.Dash(name=__name__, assets_folder="assets")
server = app.server


def celltypeDrop():
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
def updateResultTable(celltype):
    tbl = DATA[celltype]["detbl"]
    data=tbl.to_dict("records")
    columns=[{'id':c, 'name':c} for c in tbl.columns]
    return data, columns


@app.callback(Output("geneListDrop", "options"),
              Input("cellTypeSelector", "value"))
def updateGeneList(celltype):
    genes = DATA[celltype]["genes"]
    options = [{"label": x, "value": x} for x in genes]
    return options


@app.callback(
    [Output("genePlotScatter", "figure"), Output("geneHeader", "children")],
    [Input("geneListDrop", "value"), Input("cellTypeSelector", "value")])
def updateGeneScatterFigure(gene, celltype):
    d = DATA[celltype]
    if (d["genes"] != gene).all():
        raise dash.exceptions.PreventUpdate
    fig = plotGeneScatter(d["ann"].etaq,
                np.sqrt(d["fracs"][d["genes"] == gene,:].toarray()[0]),
                          d["ann"].Genotype)
    return fig, "Gene: {}".format(gene)


@app.callback(
    Output("genePlotLines", "figure"),
    [Input("geneListDrop", "value"), Input("cellTypeSelector", "value")])
def updateGeneLineFigure(gene, celltype):
    betas = getGeneBetas(SPLINE["betas"],  celltype, gene)
    if betas.shape[0] == 0:
        return dict(data=[], layout={"title":"no estimation for this gene"})
    x = getMouseSplines(betas, SPLINE["spline"]).melt(id_vars="etaq")
    mouse2genotype = DATA['hep']['ann'][['mouse', 'Genotype']].drop_duplicates()
    x = x.join(mouse2genotype.set_index("mouse"), on="mouse")
    fig = plotGeneLines(x.etaq, x.value, x.mouse, x.Genotype)
    return fig


def splitByDelimiters(x):
    return re.split("[,/;\t ]", x)

@app.server.route("/genes", methods=["POST"])
def genesZip():
    celltype = request.form['cellTypeInput']
    genes = splitByDelimiters(request.form['genesInput'])
    buf = createGenesZip(genes, DATA[celltype], SPLINE,
                         width=1000, height=800,
                         celltype=celltype)
    buf.seek(0)
    return flask.send_file(buf, attachment_filename="genes.zip")

def downloadButton(uri):
    button = html.Form(
        action=uri,
        target="_blank",
        method="post",
        children=[
            dcc.Input(id="geneFormInput", name="geneList"), 
            html.Button(
                className="button",
                type="submit",
                children=["download"]
            )
        ]
    )
    return button

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
                    children=[celltypeDrop(), dcc.Dropdown(id="geneListDrop")],
                    id="selectorsContainer"
                ),
                html.Div(
                    children=[downloadButton("genes")]
                ),
                html.H3("Comparison along the central(0.0)-portal(1.0) axis"),
                resultTable()
            ], style={"width":"80%", "margin":"auto"}),
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
