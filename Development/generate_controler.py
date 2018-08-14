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

    def generateSomeWordFrame(self, types=0):
        """
        複数の単語による系統樹生成
        types=0: 素性に基づく距離の生成, otherwise: 音素に基づく距離の生成
        """
        if len(self.file_list) == 0:
            return -1

        with codecs.open(self.file_list[0], "r", "Shift-JIS", "ignore") as filer:
            init = pd.read_table(filer, delimiter=",")

        mbfs = mbf.MakeBitFrame(init, self.cons, self.vowel)
        mbfs.setIndecesLabels(index_type=1)
        self.s_name_list = mbfs.getNameIndex()

        all_bit_data = map(lambda file_num: self.getBitData(
            file_num, types), range(len(self.file_list)))

        self.bit_frame_list = np.concatenate(all_bit_data, axis=1)

        hDM = hdm.HammingDistanceMatrix()
        hDM.calcHammingDistanceMatrix(self.bit_frame_list)

        self.distance_matrix = hDM.getDistanceMatrix()
        self.distance_matrix.index = self.s_name_list
        self.distance_matrix.columns = self.s_name_list

    def getBitData(self, file_number, types):
        """
        指定された単語ファイルから全地域の音素データをビットデータへ変換し、リストにして返す
        """
        bit_data = []
        # print(self.file_list[file_number])

        with codecs.open(self.file_list[file_number], "r", "Shift-JIS", "ignore") as files:
            mtoshi = pd.read_table(files, delimiter=",")

            mbfs = mbf.MakeBitFrame(mtoshi, self.cons, self.vowel)

            if types == 0:
                mbfs.makeFrameList(data_type="a")
            else:
                mbfs.makeFrameList(data_type="w")

            bit_data = mbfs.getBitDataFrame()

            assert bit_data != [], str(
                self.file_list[file_number]) + "のファイルに不正文字が含まれている可能性があります。"

            bit_data = mbfs.joinAlignments(copy.deepcopy(bit_data))

            # あとでconcatenateするために各要素をリストにする必要がある。
        return map(lambda x: [x], bit_data)

    def generateOneWordFrame(self, types=0):
        """
        １単語による距離の生成
        types=0: 素性に基づく距離の生成, otherwise: 音素に基づく距離の生成
        """

        have_nan_index_list = []

        with codecs.open(self.file_list, "r", "Shift-JIS", "ignore") as files:
            mtoshi = pd.read_table(files, delimiter=",")
        print(self.file_list)

        mbfs = mbf.MakeBitFrame(mtoshi, self.cons, self.vowel)
        mbfs.setIndecesLabels(index_type=0)
        name_list = mbfs.getNameIndex()

        if types == 0:
            mbfs.makeFrameList(data_type="a")
        else:
            mbfs.makeFrameList(data_type="w")

        bit_data = mbfs.getBitDataFrame()

        assert bit_data != [], "ビットシーケンスデータの抽出に失敗しています"

        # 欠損部分(NaN)を持つ地域をリストから削除
        have_nan_index_list = mbfs.searchNanElem(bit_data)
        data_list = mbfs.deleteNanElem(have_nan_index_list, bit_data)
        name_list = mbfs.deleteNanElem(have_nan_index_list, name_list)

        assert data_list != [], "すべてのデータが欠損であるため、処理が正しく行えませんでした。"

        align = mbfs.joinAlignments(copy.deepcopy(data_list))

        # 0と1のビット列でないデータ(-9のデータ)を削除
        deleted_indeces = mbfs.searchLoss(align)
        c = 0
        for y in range(len(deleted_indeces)):
            data_list.pop(deleted_indeces[y] - c)
            name_list.pop(deleted_indeces[y] - c)
            c = c + 1

        # data_list = mbfs.joinAlignments(copy.deepcopy(data_list))
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
