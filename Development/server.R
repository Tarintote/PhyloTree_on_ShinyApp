options(rgl.useNULL=TRUE)
#options(rgl.printRglwidget=FALSE)

if(!require("foreach", character.only=TRUE)){
  install.packages("foreach")
}

pkgs.name = c("shiny", "devtools", "reticulate", "phangorn", "phytools", "phylocanvas",
 "igraph", "ggplot2", "dendextend", "RColorBrewer", "colormap", "gpclib", "maptools", "leaflet",
 "rgl")

foreach(i = pkgs.name, .packages="foreach") %do%{
    if(!require(i, character.only=TRUE)){
      install.packages(i)
    }
}

gc <- import("generate_controler")
nex <- import("helper")
os <- import("os")

source("helpers.R")

distance.object <- setRefClass(

    #クラス名を定義
    Class = "distance",

   #フィールドを定義
    fields=list(
        distance.matrix="data.frame"
    ),

    prototype=prototype(
        distance.matrix=0
    ),

   #メソッドを定義
    methods = list(
     #出力メソッド
    output = function(){
        distance.matrix
    }
   )
)

dis <- distance.object$new()
count.handlar <- 0
cwd <- os$getcwd()
dirpath <- os$path$join(cwd, "Development/DistanceStorage")
if(os$path$exists(dirpath)!=TRUE) os$mkdir(dirpath)
filepath <- os$path$join(dirpath, "distance.csv")

## サーバロジックの定義。ヒストグラムを描く
shinyServer(
    function(input, output, session) {
        graphics.off()
        row_names = 0

        ##########母音のデータベース入力UI
        output$vowel.text <- renderUI({
            input_base_file <- input$vowel_database
            if(is.null(input_base_file))
                return()
            paste(input_base_file$name, "を母音データベースとして利用します。", sep="")
        })

        vowelDataBaseFilePath <- reactive({
            input_file <- input$vowel_database
            if(is.null(input_file))
                return()
            data <- read.table(input_file$datapath, header=T, sep=",", skip=0, fileEncoding="shift_jis",comment.char="")
            storage_path = paste("./DataBaseStorage", input_file$name, sep="/")
            write.table(data, storage_path, quote=T, append=F, col.names=T, row.names=F, sep=",", fileEncoding='shift-JIS')
            return(storage_path)
        })
        ##########

        ##########子音のデータベース入力UI
        output$consonant.text <- renderUI({
            input_base_file <- input$consonant_database
            if(is.null(input_base_file))
                return()
            #print(attributes(input_base_file))
            paste(input_base_file$name, "を母音データベースとして利用します。", sep="")
        })

        consonantDataBaseFilePath <- reactive({
            input_file <- input$consonant_database
            if(is.null(input_file))
                return()
            data <- read.table(input_file$datapath, header=T, sep=",", skip=0, fileEncoding="shift_jis", comment.char="")
            storage_path = paste("./DataBaseStorage", input_file$name, sep="/")
            write.table(data, storage_path, quote=T, append=F, col.names=T, row.names=F, sep=",", fileEncoding='shift-JIS')
            return(storage_path)
        })
        ##########

        ########## 用いる単語のselectUI作成と入力したcsvファイルをStrageディレクトリに格納
        output$selectUI <- renderUI({
            file.remove(list.files(path = './Storage', full.names = T))
            inputed_file <- input$files
            if(is.null(inputed_file))
                return()
            foreach(x = 1:length(inputed_file$name)) %do%{
                data <- read.table(inputed_file$datapath[x], header=T, sep=",", skip=0, fileEncoding="shift_jis", quote = "")
                storage_path = paste("./Storage", inputed_file$name[x], sep="/")
                write.table(data, storage_path, quote=T, append=F, col.names=T, row.names=F, sep=",", fileEncoding='shift-JIS')
            }
            checkboxGroupInput("checkbox", label="Choose the Used Wards", choices=inputed_file$name)
        })

        #checkboxで選択されたファイル名のベクターを返す関数
        selectFile <- reactive({
            selected_files=c()
            inputed_file <- list.files(path = './Storage', full.names = F)
            foreach(k = input$checkbox) %do%{
                input_f <- paste("./Storage", inputed_file[which(inputed_file==k)], sep="/")
                selected_files = c(selected_files, input_f)
            }
            return(selected_files)
        })
        ##########

        ##########
        selectArt_VC <- reactive({
            return(as.integer(input$art_or_vc))
        })

        combineMethod <- reactive({
            return(as.integer(input$combine))
        })
        ##########

        generateDistance <- reactive({
            file_list <- selectFile()
            print(file_list)
            if(length(file_list)!=0){
                gcc <- gc$GenerateControler(file_list, vowelDataBaseFilePath(), consonantDataBaseFilePath())
                #gcc.makeUsingFileList('./csvFileList/notUsingCSV.dat')
                gcc$mainPreProccess()
                if (length(file_list) == 1){
                    gcc$oneWordFrame(types=selectArt_VC())
                }else{
                    gcc$sumDataFrame(types=selectArt_VC())
                }
                gcc$getDistanceMatrix()$to_csv(filepath, sep=',')
                return(0)
            }else{
                return(1)
            }
        })

        observeEvent(input$select_all, {
            if(input$select_all == 0) return(NULL)
            else{
              updateCheckboxGroupInput(session, "area_check_box",
                  label = "Choose the area",
                  choices=attributes(dis$distance.matrix)$row.names,
                  selected=attributes(dis$distance.matrix)$row.names
                )
            }
        })

        observeEvent(input$unselect_all, {
            if(input$unselect_all == 0) return(NULL)
            else{
                updateCheckboxGroupInput(session, "area_check_box",
                label = "Choose the area",
                choices=attributes(dis$distance.matrix)$row.names
                )
            }
        })

        update_checkbox.handlar <- reactive({
            updateCheckboxGroupInput(session, "area_check_box",
                label = "Choose the area",
                choices=attributes(dis$distance.matrix)$row.names,
                selected=attributes(dis$distance.matrix)$row.names
            )
            return(input$checkbox) #無理やり変更
        })

        ###############
        #####系統樹#####
        ###############

        tree <- reactive({
            getFlag = generateDistance()
            if(getFlag==0){
                dis$distance.matrix <- getDistance()
                update_checkbox.handlar()
                dist_ <- area_selected_distance_matrix(dis$distance.matrix, input$area_check_box)
                return(Phylogenetic_Tree(dist_))
            }else{
                return(1)
            }
        })

        tree.plot <- eventReactive(input$plot_action,{
            if( dev.cur() > 2 ) dev.off(3)
            par(family = "HiraKakuProN-W3")
            #direction="downwords"
            #plot(tree(), type="p", "3D", cex=0.8 ,use.edge.length = TRUE, tip.color="violetred")
            plotobj = tree()
            if(is.list(plotobj)==TRUE)
                phylocanvas(plotobj, treetype = input$tree.type, alignlabels = F)
        })

        output$tree <- renderPhylocanvas({
            tree.plot()
        })

        #output$tree <- renderPlot({
        #    tree.plot()
        #},height = 900)

        #output$tree <- renderRglwidget({
        #    rglwidget(tree.plot())
        #})
        ###############

        #####################
        #####クラスタリング####
        #####################

        cluster.plot <- eventReactive(input$plot_action,{
            getFlag = generateDistance()
            if(getFlag==0){
                dis$distance.matrix <- getDistance()

                update_checkbox.handlar()
                dist_ <- area_selected_distance_matrix(dis$distance.matrix, input$area_check_box)
                phy <- hclust(as.dist(dist_), method="average")

                cut_height <- input$height_slider
                phy <- color_labels(phy, h = cut_height)
                updateSliderInput(session, "height_slider", value = input$height_slider, min = 0, max = attributes(phy)$height)

                #Set3は最大12色までしかない
                colors_pal <- brewer.pal(12, "Set3")
                # クラスタ番号と対応した色ベクトル(ラベル順)
                col.cl <- colors_pal[cutree(phy, h=cut_height, order_clusters_as_data = F)]
                dend <- phy %>% dendextend::set("labels_colors", value = col.cl)
                return(dend)
            }else{
                return(1)
            }
        })

        output$clustering <- renderPlot({
            plot(cluster.plot(), cex=0.3)
            abline(h=input$height_slider, col="red", lty=2)
        }, height = 500)

        #####地図常にマッピング#####

        gis_map <- function(){
            jpn <- readShapePoly("./JPN_adm_shp/JPN_adm2.shp")
        }

        output$GIS_mapping <- renderPlot({
            point<-points()
            x<-point$x
            y<-point$y
            gm <- gis_map()
            plot(gm[gm$NAME_1=="Okinawa",], ylim=c(24, 25), xlim=c(123, 126))
            foreach(i = 1:length(x)) %do%{
                text(x[i], y[i], as.character("*"), cex=3, col=labels_colors(cluster.plot())[[i]])
            }
        })

        points <- function(){
            x <- c(125.210066, 123.004453, 123.756126, 124.197401, 123.004453, 123.933333, 123.907909, 124.009086,
                  124.308994, 124.161313, 124.222768, 125.27566, 125.244824, 124.700134, 125.307719, 123.981584,
                  124.088937, 124.201321, 125.321446, 125.268119, 126, 125.284957)
            y <- c(24.840554, 24.467969, 24.395636, 24.343883, 24.467969, 24.216667, 24.318895, 24.238294, 24.585801,
                  24.339397, 24.353555, 24.895688, 24.924279, 24.668716, 24.915659, 24.340133, 24.322248, 24.453884,
                  24.723368, 24.749511, 25, 24.806337)
            data.frame(x=x, y=y)
        }

        output$leaflet_map <- renderLeaflet({
            leaflet() %>%
                fitBounds(min(points()$x), min(points()$y), max(points()$x), max(points()$y)) %>%
                addTiles(urlTemplate = "http://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png")
        })

        observe({
            dend <- cluster.plot()
            if(dend!=1){
                leafletProxy("leaflet_map") %>%
                    clearShapes() %>%
                    fitBounds(min(points()$x), min(points()$y), max(points()$x), max(points()$y)) %>%
                    addCircleMarkers(lng=points()$x, lat=points()$y, radius=10, popup=rownames(data.frame(labels_colors(dend))), color=data.frame(labels_colors(dend))[,] )
            }
        })

        ###############

        #######################
        #####系統ネットワーク#####
        #######################

        network <- reactive({
            getFlag = generateDistance()
            if(getFlag==0){
                dis$distance.matrix <- getDistance()
                update_checkbox.handlar()
                dist_ <- area_selected_distance_matrix(dis$distance.matrix, input$area_check_box)
                label_names <- dimnames(dist_)[[1]]
                new_label_of_Index = c()
                foreach(x=1:length(label_names)) %do%{
                    new_label_of_Index <-c(new_label_of_Index, paste("a", x, sep=("")))
                }
                nex$makeNexusFile(dist_, "../Nexusfile/", "distance", new_label_of_Index)
                #system("../SplitsTree/SplitsTree.app/Contents/MacOS/JavaApplicationStub -g -c ../commandfile.split")
                system("'/mnt/c/Program Files/SplitsTree/SplitsTree.exe' -g -c ../commandfile.split")
                return(phylogenetic_network(label_names))
            }else{
                return(1)
            }
        })

        network.plot <- eventReactive(input$plot_action,{
            if(rgl.cur() > 0) rgl.close()
            #print(rgl.cur())
            par(family = "HiraKakuProN-W3")
            plot(network(), type="2D", show.edge.label=FALSE, tip.color="violetred")
            #scene3d()
        })

        output$net <- renderPlot({
            network.plot()
        },height = 700)
        #output$net <- renderRglwidget({
        #    rglwidget(network.plot())
        #})

        ###############

    }
)
