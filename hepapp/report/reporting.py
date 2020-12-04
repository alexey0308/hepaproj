import io
import zipfile
from functools import partial

import numpy as np
import pandas as pd
import plotly
import os

from requests import Session

PLOTTINGHOST = os.getenv("PLOTTINGHOST") or "http://127.0.0.1:5082"
reqsession = Session()

# genes = pd.Series(reqsession.get(f"{DATAHOST}/genes/hep").json())[0:10]
# celltype = "hep"


def get_plot(celltype, gene, plot_type):
    fig = reqsession.get(f"{PLOTTINGHOST}/{plot_type}/{celltype}/{gene}").json()
    if fig:
        return plotly.graph_objs.Figure(fig)
    return None


def write_image_to_zip(zipbuf, filename, fig, **kwargs):
    with zipbuf.open(filename, "w") as pngfile:
        fig.write_image(pngfile, "png", **kwargs)


def createZip(celltype, genes):
    plot_types = ["scatter", "lines"]
    figs = {
        type: filter(map(lambda gene: get_plot(celltype, gene, type), genes))
        for type in plot_types
    }

    buf = io.BytesIO()
    zipbuf = zipfile.ZipFile(buf, "w")
    for plot_type in plot_types:
        for gene, fig in zip(genes, figs[type]):
            write_image_to_zip(zipbuf, f"{plot_type}-{gene}.png", fig)
    zipbuf.close()
    buf.seek(0)
    return buf
