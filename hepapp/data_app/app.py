from .data_app.dataimport import DataContainer
from flask import Flask
import sys, os

configfile = os.getenv("DATA_CONFIG") or "config.yaml"
dataapp = Flask("dataapp")
dc = DataContainer(configfile)


@dataapp.route("/betas/<celltype>/<gene>")
def get_gene_betas(celltype, gene):
    return dc.get_gene_betas(celltype, gene).to_dict()


@dataapp.route("/genes/<celltype>")
def get_genes(celltype):
    return dc.data[celltype]["genes"].to_dict()


@dataapp.route("/cell_anno/<celltype>")
def get_cell_anno(celltype):
    return dc.data[celltype]["anno"].to_dict()


@dataapp.route("/fracs/<celltype>/<gene>")
def get_fracs(celltype, gene):
    data = dc.data[celltype]
    fracs = data["fracs"]
    if (data["genes"] != gene).all():
        return gene
    return {
        "gene": gene,
        "fracs": fracs[data["genes"] == gene, :].toarray()[0].tolist(),
    }


@dataapp.route("/de_table/<celltype>")
def get_de_table(celltype):
    return dc.get_de_table(celltype)


if __name__ == "__main__":
    dataapp.run()
