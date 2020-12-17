from .celery import app
from .reporting import writeZipTask
import os

@app.task
def plotAll(celltype, genes, filepath):
    file_number = writeZipTask(celltype, genes, filepath)
    deleteFile.apply_async((filepath,), countdown=600)
    return dict(filepath=filepath, file_number=file_number)

@app.task
def deleteFile(filepath):
    os.remove(filepath)
