options(rgl.useNULL=TRUE)

library(shiny)
library(rgl)
##Define the application UI

shinyUI(fluidPage(
    titlePanel("Phylogenetic Network"),
    sidebarLayout(
        sidebarPanel(
            helpText("create the phylogeneic network for ryukyu dialect by Neighbor-Net."),

            fileInput("vowel_database",
                label=h3("Vowel DataBase File Input"),
                multiple=FALSE,
                accept=c(".csv",
                         "text/csv")
                ),
            uiOutput("vowel.text"),

            fileInput("consonant_database",
                label=h3("Consonants DataBase File Input"),
                multiple=FALSE,
                accept=c(".csv",
                         "text/csv")
                ),
            uiOutput("consonant.text"),

            fileInput("files",
                      label=h3("csvFile input"),
                      multiple=TRUE,
                      accept=c(
                          ".csv",
                          "text/csv")
                      ),
            actionButton("plot_action",label="Plot"),
            br(),
            br(),
            uiOutput("selectUI"),
            tabsetPanel(
                tabPanel(
                    "Area Select",
                    wellPanel(
                        actionButton("select_all", label="Select All"),
                        actionButton("unselect_all", label="Unselect All Selections"),
                        checkboxGroupInput("area_check_box",
                            label=NULL,
                            choices = NULL
                        )
                    )
                ),
                tabPanel(
                    "Options",
                    radioButtons("art_or_vc", label = h3("Articulation or Vowel&Consonant"),
                        choices = list("Articulation" = 0, "Vowel_Cons" = 1), selected = 0),
                    radioButtons("combine", label = h3("Combine Method"),
                        choices = list("Manhattan Distance" = 0, "Euclidean Distance" = 1), selected = 0),
                    helpText("Note: Combine Methodは複数単語を選択した場合に利用されます。")
                )
            )
        ),

        mainPanel(
            tabsetPanel(
                tabPanel("Plot Tree", plotOutput("tree", width="100%")),
                #tabPanel("Plot Tree", rglwidgetOutput("tree", width="100%", height = "512px")),
                tabPanel("Plot Network", plotOutput("net", width="100%", height="512px"))
                #以下はrglを使ってoutputするときに必要
                #tabPanel("Plot Network", rglwidgetOutput("net", width="100%", height = "512px"))
                ##tabPanel("Input File", verbatimTextOutput("contents"))
            )
        )
    )
))
