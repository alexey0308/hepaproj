import io
import zipfile
from functools import partial

import numpy as np
import plotly

from . import plots
from . import dataimport


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


def singleGeneLine(gene, betas, spline, d, cellType):
    genebetas = dataimport.getGeneBetas(betas,  cellType, gene)
    if genebetas.shape[0] == 0:
        return None
    x = dataimport.getMouseSplines(genebetas, spline).melt(id_vars="etaq")
    mouse2genotype = d['ann'][['mouse', 'Genotype']].drop_duplicates()
    x = x.join(mouse2genotype.set_index("mouse"), on="mouse")
    fig = plots.plotGeneLines(x.etaq, x.value, x.mouse, x.Genotype)
    return fig

def createGenesZip(genes, d, s, cellType, **kwargs):
    """
    Walk through genes, create figures, write to zipped byte array
    """
    f = partial(singleGeneScatter, d=d)
    scatterfigs = {gene:f(gene) for gene in genes}
    f = partial(singleGeneLine, d=d, betas=s['betas'], spline=s['spline'],
                cellType=cellType)
    linefigs = {gene:f(gene) for gene in genes}
    buf = io.BytesIO()
    zipbuf = zipfile.ZipFile(buf, "w")
    for gene in genes:
        with zipbuf.open("{gene}-scatter.png".format(gene=gene), "w") as pngfile:
            scatterfigs[gene].write_image(pngfile, "png", **kwargs)
        if linefigs[gene]:
            with zipbuf.open("{gene}-splines.png".format(gene=gene), "w") as pngfile:
                linefigs[gene].write_image(pngfile, "png", **kwargs)
    zipbuf.close()
    return buf
