options(rgl.useNULL=TRUE)
#options(rgl.printRglwidget=FALSE)

library(shiny)
library(devtools)
library(reticulate)
library(phangorn) ## phylogenetic network
#library(shinyRGL)
library(rgl)
library(foreach)

gc <- import("generate_controler")
nex <- import("helper")

source("helpers.R")

## サーバロジックの定義。ヒストグラムを描く
shinyServer(
    function(input, output, session) {
        graphics.off()
        row_names = 0
        distance = 0

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
            file_list = selectFile()

            gcc <- gc$GenerateControler(file_list, vowelDataBaseFilePath(), consonantDataBaseFilePath())
            #gcc.makeUsingFileList('./csvFileList/notUsingCSV.dat')
            gcc$mainPreProccess()
            if (length(file_list) == 1){
                gcc$oneWordFrame(types=selectArt_VC())
                gcc$getDistanceMatrix()$to_csv('./DistanceStorage/distance.csv', sep=',')
            }else{
                gcc$sumDataFrame(types=selectArt_VC())
                gcc$getDistanceMatrix()$to_csv('./DistanceStorage/distance.csv', sep=',')
            }
        })

        observeEvent(input$select_all, {
            if(input$select_all == 0) return(NULL)
            else{
              updateCheckboxGroupInput(session, "area_check_box",
                  label = "Choose the area",
                  choices=attributes(distance)$row.names,
                  selected=attributes(distance)$row.names
                )
            }
        })

        observeEvent(input$unselect_all, {
            if(input$unselect_all == 0) return(NULL)
            else{
                updateCheckboxGroupInput(session, "area_check_box",
                label = "Choose the area",
                choices=attributes(distance)$row.names
                )
            }
        })

        update_checkbox.handlar <- reactive({
            updateCheckboxGroupInput(session, "area_check_box",
                label = "Choose the area",
                choices=attributes(distance)$row.names,
                selected=attributes(distance)$row.names
            )
            return(input$checkbox) #無理やり変更
        })

        tree <- reactive({
            generateDistance()
            distance <<- getDistance()
            update_checkbox.handlar()
            dis <- area_selected_distance_matrix(distance, input$area_check_box)
            Phylogenetic_Tree(dis)
        })

        tree.plot <- eventReactive(input$plot_action,{
            if( dev.cur() > 2 ) dev.off(3)
            par(family = "HiraKakuProN-W3")
            plot(tree(), type="p", cex=0.5 ,use.edge.length = TRUE, tip.color="violetred")
        })

        output$tree <- renderPlot({
            tree.plot()
        },height = 700)

        #output$tree <- renderRglwidget({
        #    rglwidget(tree.plot())
        #})

        network <- reactive({
            generateDistance()
            distance <<- getDistance()
            update_checkbox.handlar()
            dis <- area_selected_distance_matrix(distance, input$area_check_box)
            nex$makeNexusFile(dis, "../Nexusfile/", "distance", dimnames(dis)[[1]])
            system("../SplitsTree/SplitsTree.app/Contents/MacOS/JavaApplicationStub -g -c ../commandfile.split")
            phylogenetic_network(as.dist(dis))
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

    }
)
