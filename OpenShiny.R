if(!require("foreach", character.only=TRUE)){
  install.packages("foreach")
}

pkgs.name = c("RNeXML", "shiny", "devtools", "reticulate", "phangorn", "phytools",
 "igraph", "ggplot2", "dendextend", "RColorBrewer", "colormap", "gpclib", "maptools", "leaflet",
 "rgl")

foreach(i = pkgs.name, .packages="foreach") %do%{
    if(!require(i, character.only=TRUE)){
      install.packages(i)
      require(i, character.only=TRUE)
    }
}

if(!require("phylocanvas", character.only=TRUE)){
  devtools::install_github("zachcp/phylocanvas")
  require("phylocanvas", character.only=TRUE)
}

#if (!require(shiny)){install.packages("shiny")}
shiny::runApp("Development", launch.browser=TRUE)
