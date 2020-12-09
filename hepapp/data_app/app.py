# from .data_app.dataimport import DataContainer
from .data_app.dataimport import DataContainer
from flask import Flask, jsonify
import sys, os
from flask_caching import Cache

configfile = os.getenv("DATA_CONFIG") or "config.yaml"
app = Flask("data_app")
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
dc = DataContainer(configfile)


@app.route("/betas/<celltype>/<gene>")
def get_gene_betas(celltype, gene):
    return dc.get_gene_betas(celltype, gene).to_dict()


@app.route("/genes/<celltype>")
def get_genes(celltype):
    return dc.data[celltype]["genes"].to_dict()


@app.route("/cell_anno/<celltype>")
def get_cell_anno(celltype):
    return dc.data[celltype]["anno"].to_dict()


@app.route("/fracs/<celltype>/<gene>")
@cache.cached(timeout = 500)
def get_fracs(celltype, gene):
    data = dc.data[celltype]
    fracs = data["fracs"]
    if (data["genes"] != gene).all():
        return {"gene": gene, "fracs": []}
    return {
        "gene": gene,
        "fracs": fracs[data["genes"] == gene, :].toarray()[0].tolist(),
    }


@app.route("/de_table/<celltype>")
def get_de_table(celltype):
    return dc.get_de_table(celltype).to_dict()

@app.route("/spline")
def get_spline():
    return jsonify(dc.get_spline().tolist())

if __name__ == "__main__":
    app.run()
