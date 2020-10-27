# -*- coding: utf-8 -*-
import pandas as pd
import os
from scipy.io import mmread

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
    ann.mouse = pd.Categorical(ann.Genotype)
    genes =  getGenes(datadir, cellType)
    fracs =  getFracs(datadir, cellType)
    tbl =  getDETable(datadir, cellType)
    return {"ann":ann, "genes":genes, "fracs":fracs, "detbl":tbl}

def readAll(datadir="data"):
    DATA = {}
    for cellType in ["hep", "lsec"]:
        DATA[cellType] = readCellType(cellType, datadir)
    return DATA
