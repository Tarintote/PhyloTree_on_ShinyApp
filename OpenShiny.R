dir.create(path = Sys.getenv("R_LIBS_USER"), showWarnings = FALSE, recursive = TRUE)

if(!require("foreach", character.only=TRUE)){
  install.packages("foreach", lib=Sys.getenv("R_LIBS_USER"))
  require("foreach", character.only=TRUE)
}

pkgs.name = c("RNeXML", "shiny", "devtools", "reticulate", "phangorn", "phytools",
 "igraph", "ggplot2", "dendextend", "RColorBrewer", "colormap", "gpclib", "maptools", "leaflet")

foreach(i = pkgs.name, .packages="foreach") %do%{
    if(!require(i, character.only=TRUE)){
      install.packages(i, lib=Sys.getenv("R_LIBS_USER"))
      library(i, character.only=TRUE)
    }
}

if(!require("phylocanvas", character.only=TRUE)){
  devtools::install_github("zachcp/phylocanvas")
  library("phylocanvas", character.only=TRUE)
}

library(rgl)

#if (!require(shiny)){install.packages("shiny")}
shiny::runApp("Development", launch.browser=TRUE)
