# -*- coding: utf-8 -*-
import pandas as pd
import os
from scipy.io import mmread
import numpy as np


def getCellAnno(datadir="data", cellType="hep"):
    file = os.path.join(datadir, f"{cellType}-anno.csv")
    return pd.read_csv(file)

def getFracs(datadir="data", cellType="hep"):
    file = os.path.join(datadir, f"{cellType}-mm.mtx")
    ## matrix with cells as columns
    mat = mmread(file).tocsr()
    return mat

def getGenes(datadir="data", cellType="hep"):
    file = os.path.join(datadir, f"{cellType}-genes.csv")
    x = pd.read_csv(file)
    return x.iloc[:,1]

def getDETable(datadir="data", cellType="hep"):
    file = os.path.join(datadir, f"{cellType}-glm-de-test.csv")
    x = pd.read_csv(file).iloc[:,1:]
    numberCols = ['l2fc', 'sd', 'pval']
    for c in numberCols:
        x[c] = x[c].map(lambda y: "{:.4f}".format(y))
        x.position = pd.Categorical(x.position)
    return x

def readCellType(cellType, datadir):
    ann = getCellAnno(datadir, cellType)
    ann.mouse = pd.Categorical(ann.mouse)
    genes =  getGenes(datadir, cellType)
    fracs =  getFracs(datadir, cellType)
    tbl =  getDETable(datadir, cellType)
    return {"ann":ann, "genes":genes, "fracs":fracs, "detbl":tbl}


def readAll(datadir="data"):
    DATA = {}
    for cellType in ["hep", "lsec"]:
        DATA[cellType] = readCellType(cellType, datadir)
    return DATA


def readSpline(datadir):
    betas = pd.read_csv(os.path.join(datadir, 'betas.csv'))
    spline = pd.read_csv(os.path.join(datadir, "spline.csv")).to_numpy()
    return dict(betas=betas, spline=spline)

def getGeneBetas(betas, cellType, gene):
    return betas[(betas.celltype == cellType) & (betas.gene == gene)]

def getMouseSplines(betas, spline):
    xcols = ["X1", "X2", "X3", "X4"]
    coefs = betas[xcols].to_numpy().T
    res = spline.dot(coefs)
    res = pd.DataFrame(res, columns=betas.mouse)
    res['etaq'] = np.linspace(0,1, res.shape[0])
    return res
