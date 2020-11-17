import io
import zipfile
from functools import partial

import numpy as np
import plotly

from . import plots


def singleGeneScatter(gene, d):
    """
    d = DATA[cellType]
    """
    if (d["genes"] != gene).all():
        return None
    fig = plots.plotGeneScatter(d["ann"].etaq,
                np.sqrt(d["fracs"][d["genes"] == gene,:].toarray()[0]),
                          d["ann"].Genotype)
    return fig

def createGenesZip(genes, d, **kwargs):
    """
    Walk through genes, create figures, write to zipped byte array
    """
    f = partial(singleGeneScatter, d=d)
    figs = {gene:f(gene) for gene in genes}
    buf = io.BytesIO()
    zipbuf = zipfile.ZipFile(buf, "w")
    for gene in genes:
        with zipbuf.open("{gene}.png".format(gene=gene), "w") as pngfile:
            figs[gene].write_image(pngfile, "png", **kwargs)
    zipbuf.close()
    return buf
