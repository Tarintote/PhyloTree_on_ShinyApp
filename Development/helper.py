#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs
import numpy as np
import pandas as pd
from datetime import datetime

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

def set_labels(dist):
    for i in range(len(dist)):
        if i == len(dist):
            break
        dis = dist[dist.columns[:]]
        rep_indeces = dis.iloc[i, :][(
            dis.iloc[i, :] == 0.000000) == True].index[:]
        print(rep_indeces)
        try:
            pronunce = rep_indeces[0].split(" ")[1]
            new_name = pronunce + " " + \
                " ".join(map(lambda x: x.split(" ")[0], rep_indeces))
        except Exception as e:
            new_name = " ".join(rep_indeces)

        set_index = rep_indeces[1:]
        dist = dist[dist.index.isin(set_index) == False]
        dist = dist.drop(columns=set_index)
        dist = dist.rename(
            columns={dist.columns[i]: new_name}, index={dist.index[i]: new_name})
    return dist

def squeezeArea(array, original_index, new_index):
    if new_index==None:
        return np.array(array)
    else:
        seq = np.array(array)
        exist_idx = [i for i,x in enumerate(original_index) if x in new_index]
        booler = np.zeros(len(original_index), dtype=bool)
        booler[exist_idx] = True
        return seq[booler]

def makeNexusFile_verArray(array, nex_path, filename, index):
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
    with codecs.open(nex_path + filename + datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + ".nex", mode="a", encoding="UTF-8") as file:
        file.write("#nexus\n")
        file.write("[!Mtoshi]\n\n")
        file.write("BEGIN Taxa;\n")
        file.write("DIMENSIONS ntax=" + str(len(index)) + ";\n")
        file.write("TAXLABELS\n")
        for i in range(0, len(index)):
            file.write("[" + str(i+1) + "] " +
                       unicode(index[i], "UTF-8") + "\n")
            #file.write("["+ str(i+1) +"] " + index[i] + "\n")

        file.write(";\n")
        file.write("END; [Taxa]\n\n")

        file.write("BEGIN Characters;\n")
        file.write("DIMENSIONS nchar=" + str(len(array[0])) + ";\n")
        file.write("FORMAT datatype=standard labels;\n")
        file.write("MATRIX\n")

        # distance matrix
        for k in range(0, len(array)):
            writeLine = "[" + str(k+1) + "]" + " " + \
                unicode(index[k], "UTF-8") + "\t" + str(array[k])
            file.write(writeLine + "\n")

        file.write(";\nend;")
