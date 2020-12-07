from flask import Flask, send_file, request
from .reporting import createZip
import sys

app = Flask("reporting")


@app.route("/zip/<celltype>", methods=["POST"])
def zipplots(celltype):
    genes = request.json["genes"]
    try:
        plotarch = createZip(celltype, genes)
    except:
        return "Internal error :(", 404
    return send_file(plotarch, attachment_filename="genes.zip")
