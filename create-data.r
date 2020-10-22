library(Matrix)
library(purrr)
library(ggplot2)
library(dplyr)
library(tidyr)
source("code/func.r")
source("code/assets.r")
resdir <- "results/tables/"
pydir <- "app/data"


{cat("reading...")
  d <- readCellType("heps")
  counts <- d$counts; cellanno <- d$cellanno
  markers <- loadFiles("markers")$itzkevitz
  markers <- add6LandMarks(markers)
  cat("OK\n")
}

totals <- colSums(counts)
fracs <- t(t(counts) / totals)
cellpositions <- assignPosition(counts, cellanno, totals, fracs, markers)
write.csv(cellpositions, file.path(pydir, "hep-anno.csv"))
genes <- write.csv(rownames(fracs), file.path(pydir, "hep-genes.csv"))
Matrix::writeMM(fracs[1:100,1:200], file = file.path(pydir, "hep-mm.mtx"))

{cat("reading...")
  d <- readCellType("lsec")
  counts <- d$counts; cellanno <- d$cellanno
  markers <- loadFiles("markers")$lsec
  cat("OK\n")
}

totals <- colSums(counts)
fracs <- t(t(counts) / totals)
cellpositions <- assignPosition(counts, cellanno, totals, fracs, markers)
write.csv(cellpositions, file.path(pydir, "lsec-anno.csv"))

genes <- write.csv(rownames(fracs), file.path(pydir, "lsec-genes.csv"))
Matrix::writeMM(fracs, file = file.path(pydir, "lsec-mm.mtx"))

tbls <- list(
  "hep-glm-de-test.csv",
  "lsec-glm-de-test.csv"
)
for (x in tbls) {
  file.copy(
    file.path("results", "tables", x),
    file.path(pydir, x))
}
