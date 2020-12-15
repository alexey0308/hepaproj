from .celery import app
from .reporting import writeZipTask

@app.task
def plotAll(celltype, genes, filepath):
    writeZipTask(celltype, genes, filepath)
    return genes
