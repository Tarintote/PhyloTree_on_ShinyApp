#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs
import pandas as pd


def makeNexusFile(dm, nex_path, filename, index):
    """
    SplitTree作成のためのNexファイルを作成
    dm : distance matrix(array型)
    nex_path: nexusフォーマットのファイルの保存先へのパス
    filename: 保存ファイル名
    index: 地域名
    """
    index = map(lambda x: x.replace(":", "-"), index)
    if(os.path.exists(nex_path + filename + ".nex") == True):
        os.remove(nex_path + filename + ".nex")
    if(os.path.exists(nex_path + filename + "_forSplitsTree.nex") == True):
        os.remove(nex_path + filename + "_forSplitsTree.nex")
    with codecs.open(nex_path + filename + ".nex", mode="a", encoding="UTF-8") as file:
        file.write("#nexus\n")
        file.write("[!list1.txt]\n\n")
        file.write("BEGIN Taxa;\n")
        file.write("DIMENSIONS ntax=" + str(len(index)) + ";\n")
        file.write("TAXLABELS\n")
        for i in range(0, len(index)):
            file.write("[" + str(i+1) + "] " +
                       unicode(index[i], "UTF-8") + "\n")
            #file.write("["+ str(i+1) +"] " + index[i] + "\n")

        file.write(";\n")
        file.write("END; [Taxa]\n\n")

        file.write("BEGIN Distances;\n")
        file.write("DIMENSIONS ntax=" + str(len(index)) + ";\n")
        file.write("FORMAT labels=left diagonal triangle=both;\n")
        file.write("MATRIX\n")

        # distance matrix
        for k in range(0, len(dm)):
            writeLine = "[" + str(k+1) + "]" + " " + \
                unicode(index[k], "UTF-8") + "\t"
            for i in range(0, len(dm[0])):
                writeLine = writeLine + " " + str(dm[k][i])
            file.write(writeLine + "\n")

        file.write(";\nend;")
