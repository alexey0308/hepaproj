import os

import numpy as np
import pandas as pd
from flask import Flask, Response
from flask_caching import Cache
from requests import Session

from .plots import plotGeneLines, plotGeneScatter

plotapp = Flask("plot")
reqsession = Session()
DATAHOST = os.getenv("DATAHOST") or "http://127.0.0.1:5080"


def request_json_data(url):
    return reqsession.get(f"{DATAHOST}" + url).json()


def compute_mouse_splines(betas, spline, anno):
    xcols = ["X1", "X2", "X3", "X4"]
    coefs = betas[xcols].to_numpy().T
    res = spline.dot(coefs)
    res = pd.DataFrame(res, columns=betas.mouse)
    res["etaq"] = np.linspace(0, 1, res.shape[0])
    res = res.melt(id_vars="etaq")
    mouse2genotype = anno[["mouse", "Genotype"]].drop_duplicates()
    res = res.join(mouse2genotype.set_index("mouse"), on="mouse")
    res.value = np.exp(res.value / 2)
    return res


@plotapp.route("/lines/<celltype>/<gene>")
def plot_line(celltype, gene):
    betas = pd.DataFrame(request_json_data(f"/betas/{celltype}/{gene}"))
    if betas.empty:
        return dict(data=[], layout={"title": "no estimation for this gene"})
    anno = pd.DataFrame(request_json_data(f"/cell_anno/{celltype}"))
    spline = np.array(request_json_data(f"/spline"))
    x = compute_mouse_splines(betas, spline, anno)
    fig = plotGeneLines(x.etaq, x.value, x.mouse, x.Genotype)
    return Response(fig.to_json(), mimetype="application/json", status=200)


@plotapp.route("/scatter/<celltype>/<gene>")
def plot_scatter(celltype, gene):
    anno = request_json_data(f"/cell_anno/{celltype}")
    fracs = request_json_data(f"/fracs/{celltype}/{gene}")["fracs"]
    fracs = np.array(fracs)
    if len(fracs) == 0:
        return {}
    fig = plotGeneScatter(
        pd.Series(anno["etaq"]), np.sqrt(fracs), pd.Series(anno["Genotype"])
    )
    return Response(fig.to_json(), mimetype="application/json", status=200)
