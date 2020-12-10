from flask import Flask, send_file, request
from .reporting import createZip
import sys
import logging

logger = logging.getLogger(__name__)

app = Flask("reporting")


@app.route("/zip/<celltype>", methods=["POST"])
def zipplots(celltype):
    genes = request.json["genes"]
    try:
        plotarch = createZip(celltype, genes)
    except:
        return "Internal error :(", 500
    print(type(plotarch))
    if plotarch is None:
        return "No genes...", 204
    return send_file(plotarch, attachment_filename="genes.zip")
