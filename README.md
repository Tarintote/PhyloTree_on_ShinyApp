PhyloTree_on_ShinyApp
=====================

これは沖縄諸語の言語系統樹を分析するために開発しているRのShinyを用いたwebアプリケーションである。
沖縄諸語の発音データから系統樹を作成したり、クラスタリングで分類して地図上にプロットしたりすることができる。

動作環境はLinux系を想定しており、Windows派はWindows10にubuntuのディストリビューションを入れるなどして対応して欲しい。

基本的に操作画面のインターフェースはRのShinyで作られているが、細かいデータの処理についてはpython2を用いている。今後、python3に移行する予定である。

起動方法
-----
1. gitからPhyloTree_on_ShinyAppをクローン
2. PhyloTree_on_ShinyAppディレクトリにパスを通す
3. ターミナル(command line)上で以下のコマンドを実行

        ExecuteApp

Usage
-----
このアプリではこのアプリで想定している形式の子音と母音の素性に関するデータベース(csv)、そして単語ファイル(csv)を入力する必要がある。

子音と母音に関するデータベースの形式については以下のファイルらを参考にして欲しい。

    PhyloTree_on_ShinyApp/ArticulationDataBase/子音入力数値一覧.csv
    PhyloTree_on_ShinyApp/ArticulationDataBase/母音入力数値一覧.csv

単語ファイルの形式については以下のファイルらを参考にして欲しい。

    PhyloTree_on_ShinyApp/csvFileList/*.csv

Dependencies(python)
------------

-  `Python 2 <http://www.python.org>`
-  `Numpy <http://www.numpy.org>`
-  `Pandas <http://www.pandas.org>`


Dependencies(R)
-----
適当に書き出してみる

- `shiny`
- `reticulate`
- `phangorn`
- `phytools`
- `phylocanvas`
- `igraph`
- `ggplot2`
- `RColorBrewer`
- `colormap`
- `gpclib`
- `maptools`
- `leaflet`
- `rgl`

Contact
-------
-  `Hiroyuki Tengan`
   tarintote@ms.ie.u-ryukyu.ac.jp
