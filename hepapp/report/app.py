from flask import Flask, send_file, request
from .tasks import plotAll
import sys
import os
import logging
import uuid

logger = logging.getLogger(__name__)

app = Flask("reporting")


@app.route("/zip/<celltype>", methods=["POST"])
def zipplots(celltype):
    genes = request.json["genes"]
    fileid = uuid.uuid4().hex
    image_dir = "images"
    plotAll.delay(celltype, genes, os.path.join(image_dir, fileid + ".zip"))
    return fileid, 200

