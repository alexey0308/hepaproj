library(Matrix)
library(purrr)
library(ggplot2)
library(dplyr)
library(tidyr)
source("code/func.r")
source("code/assets.r")
resdir <- "results/tables/"
pydir <- "app/data"


pytestdir <- "app/data-test"
testGenes <- 1:50


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
Matrix::writeMM(fracs, file = file.path(pydir, "hep-mm.mtx"))

Matrix::writeMM(fracs[testGenes, ], file = file.path(pytestdir, "hep-mm.mtx"))
genes <- write.csv(rownames(fracs)[testGenes], file.path(pytestdir, "hep-genes.csv"))

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

Matrix::writeMM(fracs[testGenes, ], file = file.path(pytestdir, "lsec-mm.mtx"))
genes <- write.csv(rownames(fracs)[testGenes], file.path(pytestdir, "lsec-genes.csv"))

tbls <- list(
  "hep-glm-de-test.csv",
  "lsec-glm-de-test.csv",
  "spline.csv"
)
for (x in tbls) {
  file.copy(
    file.path("results", "tables", x),
    file.path(pydir, x), overwrite = TRUE)
}

{ cat("save beta values for every mouse... ")

  res <- list(
    hep  = readRDS(file.path(rdsDir, "hepa-glm-mouse-nb-hvg.rds")),
    lsec = readRDS(file.path(rdsDir, "lsec-glm-mouse-nb-hvg.rds")))

  extractMouseBetas <- function(widebetas) {
    labels <- do.call(rbind, strsplit(split = ":", colnames(widebetas)))
    z <- split(seq_along(labels[,1]), labels[,2]) %>%
      map(~widebetas[,.x]) %>%
      map(function(.x) {
        colnames(.x) <- gsub(":mouse.+", "", colnames(.x))
        .x <- as.data.frame(.x)
        .x$gene <- rownames(.x)
        .x
      }) %>% bind_rows(.id = "mouse") %>%
      mutate(mouse = gsub("mouse", "", mouse))
    z
  }

  betas <- lapply(set_names(c("hep", "lsec")), function(celltype) {
    x <- do.call(rbind, res[[celltype]]$betas)
    extractMouseBetas(x)
  })
  betas <- bind_rows(betas, .id = "celltype")
  write.csv(betas, file.path(pydir, "betas.csv"))
}
