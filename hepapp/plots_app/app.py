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

def compute_mouse_splines(betas, spline):
    xcols = ["X1", "X2", "X3", "X4"]
    coefs = betas[xcols].to_numpy().T
    res = spline.dot(coefs)
    res = pd.DataFrame(res, columns=betas.mouse)
    res['etaq'] = np.linspace(0, 1, res.shape[0])
    return res

@plotapp.route("/lines/<celltype>/<gene>")
def plot_scatter(celltype, gene):
    betas = pd.DataFrame(reqsession.get(f"{DATAHOST}/betas/{celltype}/{gene}").json())
    if betas.empty:
        return dict(data=[], layout={"title": "no estimation for this gene"})
    anno = pd.DataFrame(reqsession.get(f"{DATAHOST}/cell_anno/{celltype}").json())
    spline = reqsession.get(f"{DATAHOST}/spline")
    spline = np.array(spline.json())
    x = compute_mouse_splines(betas, spline).melt(id_vars="etaq")
    mouse2genotype = anno[['mouse', 'Genotype']].drop_duplicates()
    x = x.join(mouse2genotype.set_index("mouse"), on="mouse")
    values = np.exp(x.value/2)
    fig = plotGeneLines(x.etaq, values, x.mouse, x.Genotype)
    return Response(fig.to_json(), mimetype="application/json", status = 200)
