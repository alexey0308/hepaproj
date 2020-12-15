from .celery import app
from .reporting import writeZipTask
import os

@app.task
def plotAll(celltype, genes, filepath):
    writeZipTask(celltype, genes, filepath)
    deleteFile.apply_async((filepath,), countdown=600)
    return genes

@app.task
def deleteFile(filepath):
    os.remove(filepath)
