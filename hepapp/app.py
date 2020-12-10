import os
import re
import sys
from io import BytesIO
from re import split
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import flask
import numpy as np
import pandas as pd
import yaml
from dash.dependencies import Input, Output
from flask import request, send_file, Response, make_response, abort
from plotly.io import from_json
from requests import Session

import logging

app = dash.Dash(name=__name__, assets_folder="assets")
server = app.server
reqsession = Session()

DATAHOST = os.getenv("DATAHOST") or "http://127.0.0.1:5081"
PLOTTINGHOST = os.getenv("PLOTTINGHOST") or "http://127.0.0.1:5082"
REPORTING_API = os.getenv("REPORTING_API") or "http://127.0.0.1:5083"
APP_PREFIX = os.getenv("DASH_REQUESTS_PATHNAME_PREFIX") or ""


def celltypeDrop(id="cellTypeSelector"):
    return dcc.RadioItems(
        id=id,
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
    fig = from_json(reqsession.get(f"{PLOTTINGHOST}/scatter/{celltype}/{gene}").text)
    return fig, "Gene: {}".format(gene)


@app.callback(
    Output("genePlotLines", "figure"),
    [Input("geneListDrop", "value"), Input("cellTypeSelector", "value")],
)
def updateGeneLineFigure(gene, celltype):
    from plotly.io import from_json

    fig = from_json(reqsession.get(f"{PLOTTINGHOST}/lines/{celltype}/{gene}").text)
    return fig


def splitByDelimiters(x):
    return re.split("[,/;\t ]", x)


@app.server.route("/genes-plots/", methods=["POST"])
def genesZip():
    celltype = request.form["celltype"]
    genes = list(filter(None, splitByDelimiters(request.form["geneList"])))
    app.logger.info("genes:" + ",".join(genes))
    if len(genes) > 40:
        return "Too many genes", 500
    genes = [x.lower() for x in genes]
    r = reqsession.post(f"{REPORTING_API}/zip/{celltype}", json=dict(genes=genes))
    print(r.ok, r.status_code, r)
    if r.ok:
        if r.status_code == 204:
            return "No figures..."
        return send_file(BytesIO(r.content), mimetype="application/zip")
    else:
        abort(500)


@app.callback(
    Output("zipButton", "children"),
    Input("cellTypeSelector", "value"),
)
def downloadButton(celltype):
    button = html.Form(
        action=APP_PREFIX + "/genes-plots/",
        target="_blank",
        method="post",
        children=[
            dcc.Input(id="geneFormInput", name="geneList"),
            dcc.Input(
                id="hiddenCellType", name="celltype", value=celltype, type="hidden"
            ),
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
                html.Div(id="zipButton"),
                html.H3("Comparison along the central(0.0)-portal(1.0) axis"),
                resultTable(),
            ],
            style={"width": "80%", "margin": "auto"},
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
