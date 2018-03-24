library(shiny)

'%!in%' <- function(x,y)!('%in%'(x,y))

getDistance <- function(){
    dist <- read.table("./DistanceStorage/distance.csv", header=T, sep=",", row.names=1, nrows=100, quote = "", check.names=TRUE)
    return(dist)
}

area_selected_distance_matrix <- function(distance, selected_areas){
    selected_area_id <- which(dimnames(distance)[[1]] %!in% selected_areas)
    print(selected_area_id)
    if ( is.null(selected_areas) || length(selected_area_id) == 0 ){
        return(as.matrix(distance))
    }else{
        if(length(dimnames(distance)[[1]]) - length(selected_area_id) >= 3){
            selected_areas_distance <- distance[-selected_area_id, -selected_area_id] #問題
        }else{
            selected_areas_distance <- distance
        }
        return(as.matrix(selected_areas_distance))
    }
}

calc_Dist <- function(filepaths){
    ##距離行列(csv)リスト
    ##fileList <- list.files("./distMatrices/", pattern="csv")

    ##選択された単語(csv)へのファイルパス
    ##i <- fileList[1]
    ##file_path<-paste("./distMatrices/", i, sep="")
    dists=0
    for(fp in filepaths){
        ##選択された単語(csv)のテーブルを読み込む
        table <- read.table(fp, header=TRUE)
        ##距離行列生成
        dist <- as.dist(table)
        dists <- dists+dist
    }
    dists
}

Phylogenetic_Tree <- function(dist){
    ##系統樹の作成
    nj.tree <- nj(dist)
    #any()は比較要素の内1つでもTRUEがあれば1つにまとめる (True, False, True) -> True
    if (any(nj.tree$tip.label %in% "想定形") == TRUE){
        reroot.nj.tree <- root(nj.tree, which(nj.tree$tip.label=="想定形"))
        return(reroot.nj.tree)
    }else{
        return(nj.tree)
    }
}

phylogenetic_network <- function(labels){#nj.tree){
    ##系統ネットワークの作成
    Nnet <- read.nexus.networx(file.path("../Nexusfile/","distance_forSplitsTree.nex"))
    indexs <- as.integer(substring(Nnet$tip.label, 2))
    foreach(x=1:length(labels))%do%{
        Nnet$tip.label[x] <- labels[indexs[x]]
    }
    Nnet
    #nnet <- neighborNet(dist, ord=NULL)
    #edge.lab <- createLabel(nnet, nj.tree, nj.tree$edge[,2], "edge")
    #edge.col <- rep("black", nrow(nnet$edge))
    #edge.col[ is.na(edge.lab) ] <- "gray"
}

upgma_tree <- function(dist){
    wm.hc<-hclust(dist,"average")
    upgma.tree<-as.phylo(wm.hc)
    if (any(upgma.tree$tip.label %in% "祖形") == TRUE){
        reroot.upgma.tree <- root(upgma.tree, which(upgma.tree$tip.label=="祖形"))
        return(reroot.upgma.tree)
    }else{
        return(upgma.tree)
    }
}
