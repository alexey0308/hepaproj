import dash_core_components as dcc
from flask import request
import re
import dash
import numpy as np
import dash_html_components as html
import pandas as pd
import os
from .plots_app.plots import plotGeneScatter, plotGeneLines
import dash_table
import yaml
from dash.dependencies import Input, Output
from requests import Session


import flask

app = dash.Dash(name=__name__, assets_folder="assets")
server = app.server
reqsession = Session()

DATAHOST = os.getenv("DATAHOST") or "http://127.0.0.1:5080"
PLOTTINGHOST = os.getenv("PLOTTINGHOST") or "http://127.0.0.1:5081"


def celltypeDrop():
    return dcc.RadioItems(
        id="cellTypeSelector",
        options=[
            {"label": "hepatocytes", "value": "hep"},
            {"label": "lsec", "value": "lsec"},
        ],
        value="hep",
    )


def resultTable():
    dt = dash_table.DataTable(
        id="resultTable", page_size=30, filter_action="native", sort_action="native"
    )
    return dt


@app.callback(
    [Output("resultTable", "data"), Output("resultTable", "columns")],
    Input("cellTypeSelector", "value"),
)
def updateResultTable(celltype):
    tbl = pd.DataFrame(reqsession.get(f"{DATAHOST}/de_table/{celltype}").json())
    data = tbl.to_dict("records")
    columns = [{"id": c, "name": c} for c in tbl.columns]
    return data, columns


@app.callback(Output("geneListDrop", "options"), Input("cellTypeSelector", "value"))
def updateGeneList(celltype):
    genes = pd.Series(reqsession.get(f"{DATAHOST}/genes/{celltype}").json())
    options = [{"label": x, "value": x} for x in genes]
    return options


@app.callback(
    [Output("genePlotScatter", "figure"), Output("geneHeader", "children")],
    [Input("geneListDrop", "value"), Input("cellTypeSelector", "value")],
)
def updateGeneScatterFigure(gene, celltype):
    if gene is None:
        raise dash.exceptions.PreventUpdate
    anno = reqsession.get(f"{DATAHOST}/cell_anno/{celltype}").json()
    fracs = reqsession.get(f"{DATAHOST}/fracs/{celltype}/{gene}").json()
    if len(fracs) == 0:
        raise dash.exceptions.PreventUpdate
    fig = plotGeneScatter(
        pd.Series(anno["etaq"]),
        np.sqrt(fracs["fracs"]),
        pd.Series(anno["Genotype"])
    )
    return fig, "Gene: {}".format(gene)

@app.callback(
    Output("genePlotLines", "figure"),
    [Input("geneListDrop", "value"), Input("cellTypeSelector", "value")])
def updateGeneLineFigure(gene, celltype):
    from plotly.io import from_json
    fig = from_json(reqsession.get(f"{PLOTTINGHOST}/lines/{celltype}/{gene}").text)
    return fig


def splitByDelimiters(x):
    return re.split("[,/;\t ]", x)


# @app.server.route("/genes", methods=["POST"])
# def genesZip():
#     celltype = request.form['cellTypeInput']
#     genes = splitByDelimiters(request.form['genesInput'])
#     buf = createGenesZip(genes, DATA[celltype], SPLINE,
#                          width=1000, height=800,
#                          celltype=celltype)
#     buf.seek(0)
#     return flask.send_file(buf, attachment_filename="genes.zip")


def downloadButton(uri):
    button = html.Form(
        action=uri,
        target="_blank",
        method="post",
        children=[
            dcc.Input(id="geneFormInput", name="geneList"),
            html.Button(className="button", type="submit", children=["download"]),
        ],
    )
    return button


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H3(id="geneHeader", style={"color": "dodgerblue"}),
                html.Div(
                    id="figures",
                    children=[
                        dcc.Graph(
                            id="genePlotScatter",
                            style={"width": "45%", "min-width": "400px"},
                        ),
                        dcc.Graph(
                            id="genePlotLines",
                            style={"width": "45%", "min-width": "400px"},
                        ),
                    ],
                    style={"height": "500px", "margin": "auto", "display": "flex"},
                ),
                html.Div(
                    children=[celltypeDrop(), dcc.Dropdown(id="geneListDrop")],
                    id="selectorsContainer",
                ),
                html.Div(children=[downloadButton("genes")]),
                html.H3("Comparison along the central(0.0)-portal(1.0) axis"),
                resultTable(),
            ],
            style={"width": "80%", "margin": "auto"},
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
