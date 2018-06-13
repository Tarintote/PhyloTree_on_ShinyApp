#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# from __future__ import unicode_literals
import make_database as md
import make_bit_frame as mbf
import make_distance_matrix as mdm
import helper
import sys
import pandas as pd
import numpy as np
import codecs
import glob
import copy

import pdb


class GenerateControler(object):

    def unicode_(self, uc):
        # 対話環境がutf-8と仮定している。
        # バイト列を unicode 型のオブジェクトに変換すること(デコード)
        return unicode(uc, encoding='utf-8')

    def encode_(self, ec):
        # unicode型オブジェクトをstr型にエンコーディングする
        return ec.encode("Shift-JIS")

    def __init__(self, input_files_path, vowel_file_path, cons_file_path):
        self.distance_matrix = None

        # jupytrで実行時はこちらを使う
        # self.file_list = map(self.unicode_, input_files_path)
        # shiny-app(R)で実行時はこちら
        self.file_list = input_files_path
        self.data_frame_list = []
        self.bit_frame_list = []
        self.orig_frame_list = []
        self.s_name_list = []
        with codecs.open(cons_file_path, "r", "Shift - JIS", "ignore") as file:
            self.cons = pd.read_table(file, delimiter=",")
        with codecs.open(vowel_file_path, "r", "Shift-JIS", "ignore") as file:
            self.vowel = pd.read_table(file, delimiter=",")
        self.cons_orig = copy.deepcopy(self.cons)
        self.vowel_orig = copy.deepcopy(self.vowel)

    def rstrip_(self, ls):
        # 引数なしの場合、文字列の末尾の空白文字、改行文字を除去した新しい文字列を返します。
        # 引数を与えた場合、引数に含まれる文字を文字列から削除した文字列を返す。
        return ls.rstrip()

    def makeUsingFileList(self, not_using_file_path):
        filename = []
        using_list = []
        # self.file_list = map(self.unicode_, self.file_list)
        # isinstance() ふたつの引数がオブジェクトとクラスまたはそのスーパークラスの関係にあれば True を返す
        if isinstance(self.file_list, list) == False:
            filename.append(self.file_list.split("/")[-1])
        else:
            for i in range(len(self.file_list)):
                filename.append((self.file_list[i].split("/"))[-1])

        with open(not_using_file_path) as files:
            lines = files.readlines()
            not_usings = map(self.unicode_, map(self.rstrip_, lines))
            # not_usings = list(map(self.unicode_, map(self.rstrip_, lines)))

        if len(filename) != 1:
            for l in range(len(filename)):
                # lines.rstrip():
                # and isinstance(self.file_list, list) == True:
                if filename[l] not in not_usings:
                    using_list.append(self.file_list[l])
            self.file_list = using_list
        else:
            if filename in not_usings:
                print("選択されたファイルには不正文字が含まれています。")
        return self.file_list

    def mainPreProccess(self):
        vow_col = (self.vowel.columns == "母音").tolist().index(True)
        vow_dot_index = (self.vowel.iloc[0:self.vowel.index.size,
                                         vow_col] == ".").tolist().index(True)
        vdb = md.VCDataBase(self.vowel.copy(), vow_dot_index)
        cons_col = (self.cons.columns == "子音").tolist().index(True)
        cons_dot_index = (self.cons.iloc[0: self.cons.index.size,
                                         cons_col] == ".").tolist().index(True)
        cdb = md.VCDataBase(self.cons.copy(), cons_dot_index)
        vdb.generate_table_for_ward()
        vdb.generate_table_for_art()
        cdb.generate_table_for_ward()
        cdb.generate_table_for_art()
        self.cons = cdb.showTable()
        self.vowel = vdb.showTable()

    def sumDataFrame(self, types=0):
        # 複数の単語による系統樹生成
        # types=0であればarticulationに基づく距離の生成, otherwise母音子音に基づく距離の生成
        if len(self.file_list) == 0:
            return -1

        with codecs.open(self.file_list[0], "r", "Shift-JIS", "ignore") as filer:
            init = pd.read_table(filer, delimiter=",")

        mbfs = mbf.MakeBitFrame(init, self.cons, self.vowel)
        mbfs.makeIndeces(index_type=1)
        area_name_list = mbfs.getNameIndex()

        name_list = copy.deepcopy(area_name_list)
        # pdb.set_trace()
        # for fl in range(0, len(self.file_list)):
        map(lambda x: self.make_data_frame(x, area_name_list, types), [
            i for i in range(0, len(self.file_list))])
        self.s_name_list = name_list
        mDM = mdm.MakeDistanceMatrix()
        mDM.makeHammDistanceFrame(self.bit_frame_list, self.orig_frame_list)
        df = mDM.getDistanceFrame()
        print(df)
        self.distance_matrix = pd.DataFrame(
            df, self.s_name_list, self.s_name_list)

    def make_data_frame(self, fl, area_name_list, types):
        data_list = []
        with codecs.open(self.file_list[fl], "r", "Shift-JIS", "ignore") as files:
            mtoshi = pd.read_table(files, delimiter=",")
            # print(self.file_list[fl])

            mbfs = mbf.MakeBitFrame(mtoshi, self.cons, self.vowel)
            mbfs.makeIndeces(index_type=2)
            # word_name_list = mbfs.getNameIndex()
            # name_list = [x + "/" + y for x,
            #             y in zip(name_list, word_name_list)]

            if mbfs.makeFrameList(self.cons_orig, self.vowel_orig) != 0:
                return 0

            if types == 0:
                data_list = mbfs.getArticulationFrame()
                origin_data_list = mbfs.get_Original_ArticulationFrame()
            else:
                data_list = mbfs.getWordFrame()

            if data_list != []:
                print(self.file_list[fl])
            else:
                return 0

            #data_list = mbfs.joinAlignments(copy.deepcopy(data_list))

            if len(self.bit_frame_list) == 0:
                self.bit_frame_list = data_list
                self.orig_frame_list = origin_data_list
            else:
                self.bit_frame_list = np.array([np.hstack((x, y)) for x,
                                                y in zip(self.bit_frame_list, data_list)])
                self.orig_frame_list = np.array([np.hstack((x, y)) for x,
                                                 y in zip(self.orig_frame_list, origin_data_list)])
        return 0

    def oneWordFrame(self, init_table=0, types=0):
        # def oneWordFrame(self, init_table, types=0):
        # １単語による距離の生成
        # types=0であればarticulationに基づく距離の生成, otherwise母音子音に基づく距離の生成
        # pdb.set_trace()
        # if len(self.file_list) != 1:
        #    print("oneWordFrame: 渡されたファイルが1つではなかったのでリストの最初の要素のみを用います。")
        #    self.file_list = self.file_list[0]
        have_nan_index_list = []
        # with codecs.open(self.file_list, "r", "Shift-JIS", "ignore") as files:
        with codecs.open(self.file_list, "r", "Shift-JIS", "ignore") as files:
            mtoshi = pd.read_table(files, delimiter=",")
        print(self.file_list)

        mbfs = mbf.MakeBitFrame(mtoshi, self.cons, self.vowel)
        mbfs.makeFrameList(self.cons_orig, self.vowel_orig)
        mbfs.makeIndeces(index_type=0)
        # mbfs.makeIndeces_from_another_table(init_table, index_type=0)

        name_list = mbfs.getNameIndex()
        if types == 0:
            frame = mbfs.getArticulationFrame()
            origin_data = mbfs.get_Original_ArticulationFrame()
        else:
            frame = mbfs.getWordFrame()

        # 欠損部分を持つ地域のindex列をリストから削除
        have_nan_index_list = mbfs.searchNanElem(frame)
        data_list = mbfs.deleteNanElem(have_nan_index_list, frame)
        origin_data_list = mbfs.deleteNanElem(have_nan_index_list, origin_data)

        name_list = mbfs.deleteNanElem(have_nan_index_list, name_list)

        align = mbfs.joinAlignments(copy.deepcopy(data_list))
        deleted_indeces = mbfs.searchLoss(align)
        c = 0
        for y in range(len(deleted_indeces)):
            data_list.pop(deleted_indeces[y] - c)
            name_list.pop(deleted_indeces[y] - c)
            origin_data_list.pop(deleted_indeces[y] - c)
            c = c + 1

        #data_list = mbfs.joinAlignments(copy.deepcopy(data_list))
        self.bit_frame_list = data_list
        self.orig_frame_list = origin_data_list
        self.s_name_list = name_list

        mDM = mdm.MakeDistanceMatrix()
        mDM.makeHammDistanceFrame(data_list, origin_data_list)
        df = mDM.getDistanceFrame()
        data_frame = pd.DataFrame(df, name_list, name_list)
        self.distance_matrix = data_frame

    def getDistanceMatrix(self, types=0, path=None):
        # helper.set_labels(self.distance_matrix)
        return self.distance_matrix.to_csv(path, sep=',')

    def calcTwoNorm(self, vectorList):
        if len(vectorList) == 1:
            return vectorList[0]
        sum_value = 0
        for i in vectorList:
            sum_value = sum_value + i * i
        return np.sqrt(sum_value)
