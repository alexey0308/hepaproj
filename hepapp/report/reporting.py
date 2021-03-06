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


def get_plot(celltype, gene, plot_type):
    fig = reqsession.get(f"{PLOTTINGHOST}/{plot_type}/{celltype}/{gene}").json()
    if fig:
        return plotly.graph_objs.Figure(fig)
    return None


def write_image_to_buf(buf, filename, fig, **kwargs):
    with buf.open(filename, "w") as pngfile:
        fig.write_image(pngfile, "png", **kwargs)


def writeZipTask(celltype, genes, filepath):
    plot_types = ["scatter", "lines"]

    def make_plots(plot_type):
        return {gene: get_plot(celltype, gene, plot_type) for gene in genes}

    figs = {plot_type: make_plots(plot_type) for plot_type in plot_types}
    buf = io.FileIO(filepath, mode="wb")
    zipbuf = zipfile.ZipFile(buf, "w")
    file_number = 0
    for plot_type in plot_types:
        for gene, fig in figs[plot_type].items():
            if fig is not None and len(fig.data) > 0:
                write_image_to_buf(zipbuf, f"{plot_type}-{gene}.png", fig)
                file_number += 1
    zipbuf.close()
    return file_number
