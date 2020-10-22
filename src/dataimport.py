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
    return x.iloc[:,1].to_list()

def getDETable(datadir="data", cellType="hep"):
    file = os.path.join(datadir, f"{cellType}-glm-de-test.csv")
    x = pd.read_csv(file).iloc[:,1:]
    numberCols = ['l2fc', 'sd', 'pval', 'position']
    for c in numberCols:
        x[c] = x[c].map(lambda y: "{:.4f}".format(y))
    return x


