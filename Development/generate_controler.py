#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# from __future__ import unicode_literals
import convert_2bit as c2b  # md
import make_bit_frame as mbf
import hamming_distance_matrix as hdm
import helper
import sys
import pandas as pd
import numpy as np
import codecs
import glob
import copy
import re

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
        self.s_name_list = []
        with codecs.open(cons_file_path, "r", "Shift - JIS", "ignore") as file:
            self.cons = pd.read_table(file, delimiter=",")
        with codecs.open(vowel_file_path, "r", "Shift-JIS", "ignore") as file:
            self.vowel = pd.read_table(file, delimiter=",")

    def rstrip_(self, ls):
        # 引数なしの場合、文字列の末尾の空白文字、改行文字を除去した新しい文字列を返します。
        # 引数を与えた場合、引数に含まれる文字を文字列から削除した文字列を返す。
        return ls.rstrip()

    def mainPreProccess(self):
        """母音と子音の前処理(ビット列変換)"""
        """母音"""
        vowel_col = self.vowel.columns.tolist().index("母音")
        vowel_dot_idx = (
            self.vowel.iloc[0:self.vowel.index.size, vowel_col] == ".").tolist().index(True)
        vowel_phoneme_Data = pd.DataFrame(np.array(
            self.vowel.iloc[:vowel_dot_idx, 2:7]), index=self.vowel.iloc[:vowel_dot_idx, 1].values, columns=self.vowel.columns[2:7])
        vowel_phoneme_Idx = pd.DataFrame(range(
            vowel_dot_idx-2)+[-1, -9], index=self.vowel.iloc[:vowel_dot_idx, 1].values, columns=["idx"])
        vowel_Data = pd.concat([vowel_phoneme_Data, vowel_phoneme_Idx], axis=1)
        vdb = c2b.VCData2bit(vowel_Data, vowel_dot_idx)

        """子音"""
        cons_col = self.cons.columns.tolist().index("子音")
        cons_dot_idx = (
            self.cons.iloc[0: self.cons.index.size, cons_col] == ".").tolist().index(True)
        cons_phoneme_Data = pd.DataFrame(np.array(
            self.cons.iloc[:cons_dot_idx, 2:7]), index=self.cons.iloc[:cons_dot_idx, 1].values, columns=self.cons.columns[2:7])
        cons_phoneme_Idx = pd.DataFrame(range(
            cons_dot_idx-2)+[-1, -9], index=self.cons.iloc[:cons_dot_idx, 1].values, columns=["idx"])
        cons_Data = pd.concat([cons_phoneme_Data, cons_phoneme_Idx], axis=1)
        cdb = c2b.VCData2bit(cons_Data, cons_dot_idx)

        vdb.convert_value2bit_on_table()
        cdb.convert_value2bit_on_table()
        self.cons = cdb.showTable()
        self.vowel = vdb.showTable()

    def someWordFrame(self, types=0):
        # 複数の単語による系統樹生成
        # types=0: 素性に基づく距離の生成, otherwise: 音素に基づく距離の生成
        if len(self.file_list) == 0:
            return -1

        with codecs.open(self.file_list[0], "r", "Shift-JIS", "ignore") as filer:
            init = pd.read_table(filer, delimiter=",")

        mbfs = mbf.MakeBitFrame(init, self.cons, self.vowel)
        mbfs.makeIndeces(index_type=1)
        self.s_name_list = mbfs.getNameIndex()

        some_data = map(lambda file_num: self.SamplingData(
            file_num, types), range(len(self.file_list)))

        hDM = hdm.HammingDistanceMatrix()
        dms = []
        for sd in some_data:
            hDM.calcHammingDistanceMatrix(sd)
            dms.append(hDM.getDistanceMatrix())

        self.distance_matrix = sum(dms) #hDM.getDistanceMatrix()
        self.distance_matrix.index = self.s_name_list
        self.distance_matrix.columns = self.s_name_list

    def SamplingData(self, file_number, types):
        data_list = []
        print(self.file_list[file_number])

        with codecs.open(self.file_list[file_number], "r", "Shift-JIS", "ignore") as files:
            mtoshi = pd.read_table(files, delimiter=",")

        mbfs = mbf.MakeBitFrame(mtoshi, self.cons, self.vowel)
        mbfs.makeIndeces(index_type=2)
        mbfs.makeFrameList()
        if types == 0:
            data_list = np.array(mbfs.getArticulationFrame())
        else:
            data_list = np.array(mbfs.getWordFrame())
        assert len(data_list) != 0, str(self.file_list[file_number])
        concat_data = np.array(map(lambda x: "".join(np.hstack(x)), data_list))
        
        return concat_data

    def oneWordFrame(self, init_table=0, types=0):
        """
        １単語による距離の生成
        types=0: 素性に基づく距離の生成, otherwise: 音素に基づく距離の生成
        """

        have_nan_index_list = []

        with codecs.open(self.file_list, "r", "Shift-JIS", "ignore") as files:
            mtoshi = pd.read_table(files, delimiter=",")
        print(self.file_list)

        mbfs = mbf.MakeBitFrame(mtoshi, self.cons, self.vowel)
        mbfs.makeIndeces(index_type=0)
        name_list = np.array(mbfs.getNameIndex())

        mbfs.makeFrameList()

        if types == 0:
            data_list = np.array(mbfs.getArticulationFrame())
        else:
            data_list = np.array(mbfs.getWordFrame())

        assert len(data_list) != 0, "ビットシーケンスデータの抽出に失敗しています"

        # 連結
        concat_data = np.array(map(lambda x: "".join(np.hstack(x)), data_list))

        # 欠損部分(NaN)を持つ地域をリストから削除
        nanfilter = [i for i, x in enumerate(concat_data) if len(re.match("\?*",x).group())==0]
        booler = np.zeros(len(concat_data), dtype=bool)
        booler[nanfilter] = True
        data_list = concat_data[booler]
        name_list = name_list[booler]

        assert len(data_list) != 0, "すべてのデータが欠損であるため、処理が正しく行えませんでした。"

        self.bit_frame_list = data_list
        self.s_name_list = name_list

        hDM = hdm.HammingDistanceMatrix()
        hDM.calcHammingDistanceMatrix(data_list)
        self.distance_matrix = hDM.getDistanceMatrix()
        self.distance_matrix.index = name_list
        self.distance_matrix.columns = name_list

    def getDistanceMatrix(self, path=None):
        # helper.set_labels(self.distance_matrix)
        return self.distance_matrix.to_csv(path, sep=',')
