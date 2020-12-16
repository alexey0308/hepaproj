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
    task_id = plotAll.delay(
        celltype, genes, os.path.join(image_dir, fileid + ".zip")
    ).task_id
    return dict(task_id=task_id, fileid=fileid)

@app.route("/task/<task_id>")
def get_status(task_id):
    # import pdb; pdb.set_trace()
    task = plotAll.AsyncResult(task_id)
    if task.status == "SUCCESS":
        return task.result
    return "not ready", 204
