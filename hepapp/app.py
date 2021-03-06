import logging
import os
import re
import sys
from io import BytesIO
from re import split
from time import sleep

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import flask
import numpy as np
import pandas as pd
import yaml
from dash.dependencies import Input, Output
from flask import Response, abort, make_response, redirect, request, send_file, url_for
from plotly.io import from_json
from requests import Session

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


def getEdgesTable():
    tbl = pd.DataFrame(reqsession.get(f"{DATAHOST}/edges_table").json())
    edges_data = tbl.to_dict("records")
    columns = [{"id": c, "name": c} for c in tbl.columns]
    edgesTestTable = dash_table.DataTable(
        id="edgesTestTable",
        page_size=30,
        filter_action="native",
        sort_action="native",
        data=edges_data,
        columns=columns,
    )
    return edgesTestTable


def resultTable():
    genotypeTestsTable = dash_table.DataTable(
        id="genotypeTestsTable",
        page_size=30,
        filter_action="native",
        sort_action="native",
    )
    tabs = dcc.Tabs(
        id="tables",
        children=[
            dcc.Tab(children=genotypeTestsTable, label="Testing DKO vs WT"),
            dcc.Tab(children=getEdgesTable(), label="Testing PV vs CV edge"),
        ],
    )
    return tabs


@app.callback(
    [Output("genotypeTestsTable", "data"), Output("genotypeTestsTable", "columns")],
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
    if len(genes) > 400:
        return "Too many genes", 500
    genes = [x.lower() for x in genes]
    r = reqsession.post(f"{REPORTING_API}/zip/{celltype}", json=dict(genes=genes))

    if r.ok:
        task_id = r.json()["task_id"]
        sleep(3)
        return redirect(url_for("getZipFile", task_id=task_id))
    else:
        abort(500)


@app.server.route("/tasks/<task_id>")
def getZipFile(task_id):
    image_dir = "/app/images"
    r = reqsession.get(f"{REPORTING_API}/task/{task_id}")
    if r.status_code != 200:
        return "Not finished, try to refresh in a while", 202
    print(r.content)
    filepath = r.json()["filepath"]
    if r.json()["file_number"] == 0:
        return "No figures available for these genes..."
    if os.path.exists(filepath):
        return send_file(os.path.abspath(filepath))
    else:
        return "Looks like the file is already removed, submit again."
    return "Something went wrong", 500


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
            html.P(
                children="insert gene names, separated by any of ',', '/', ';' or space:"
            ),
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
                html.H3("Comparison along the central(0.0)-portal(1.0) axis"),
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
                resultTable(),
            ],
            style={"width": "80%", "margin": "auto"},
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
