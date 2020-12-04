from flask import Flask, send_file, request
from .reporting import createZip

app = Flask("reporting")


@app.route("/zip/<celltype>", methods=["POST"])
def zipplots(celltype):
    return str(request.form["genes"])
    plotarch = createZip(celltype, genes)
    send_file(plotarch)
