library(phangorn)
library(ape)
fileList<-list.files("./distmatrices/", pattern="csv")
i<-fileList[1]
file <- path<-paste("./distMatrices/", i, sep="")
table<-read.table(file <- path, header=TRUE)
dist<-as.dist(table)
nj.hoge<-nj(dist)
nnet<-neighborNet(dist)
##edge.lab <- createLabel(nnet, nj.hoge, nj.hoge$edge[,2], "edge")
##edge.col <- rep("black", nrow(nnet$edge))
##edge.col[ is.na(edge.lab) ] <- "red"
##or
##edge.col <- createLabel(nnet, nj.hoge, "black", nomatch="red")

##plot.networx(nnet, "3D", edge.color = edge.col)

