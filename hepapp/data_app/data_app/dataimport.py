# -*- coding: utf-8 -*-
import pandas as pd
import os
from scipy.io import mmread
import numpy as np
import yaml


class DataContainer:
    """
    An object to kepp all the data.
    """
    def __init__(self, configpath):
        with open(configpath) as configfile:
            self.config = yaml.safe_load(configfile)
        self.spline = self.read_spline()
        self.data = self.read_data()

    def data_path(self, path):
        return os.path.join(self.config["datadir"], path)

    def celltype_path(self, celltype, element):
        return self.data_path(
            self.config['celltypes-files'][celltype][element])

    def get_cell_anno(self, celltype):
        file = self.celltype_path(celltype, "anno")
        ann = pd.read_csv(file)
        ann.mouse = pd.Categorical(ann.mouse)
        return ann

    def get_fracs(self, celltype):
        file = self.celltype_path(celltype, "fracs")
        ## matrix with cells as columns
        mat = mmread(file).tocsr()
        return mat

    def get_genes(self, celltype):
        file = self.celltype_path(celltype, "genes")
        x = pd.read_csv(file)
        return x.iloc[:, 1]

    def get_de_table(self, celltype):
        file = self.celltype_path(celltype, "de")
        x = pd.read_csv(file).iloc[:, 1:]
        numberCols = ['l2fc', 'sd', 'pval']
        for c in numberCols:
            x[c] = x[c].map(lambda y: "{:.4f}".format(y))
            x.position = pd.Categorical(x.position)
        return x

    def read_cell_type(self, celltype):
        data = {
            "anno": self.get_cell_anno(celltype),
            "genes": self.get_genes(celltype),
            "fracs": self.get_fracs(celltype),
            "de": self.get_de_table(celltype),
        }
        return data

    def read_data(self):
        data = {}
        for celltype in self.config['celltypes-files'].keys():
            data[celltype] = self.read_cell_type(celltype)
        return data

    def read_spline(self):
        spline_data = {
            k: pd.read_csv(self.data_path(v))
            for k, v in self.config["spline-files"].items()
        }
        spline_data['spline'] = spline_data['spline'].to_numpy()
        return spline_data

    def get_gene_betas(self, celltype, gene):
        betas = self.spline["betas"]
        return betas[(betas.celltype == celltype) & (betas.gene == gene)]


def compute_mouse_splines(betas, spline):
    xcols = ["X1", "X2", "X3", "X4"]
    coefs = betas[xcols].to_numpy().T
    res = spline.dot(coefs)
    res = pd.DataFrame(res, columns=betas.mouse)
    res['etaq'] = np.linspace(0, 1, res.shape[0])
    return res
