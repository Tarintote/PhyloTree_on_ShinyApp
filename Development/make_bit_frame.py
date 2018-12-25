#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import numpy as np


class MakeBitFrame(object):
    def __init__(self, input_word_table, consonant_table, vowel_table):
        self.table = input_word_table
        self.cons = consonant_table
        self.vowel = vowel_table

        """
        単語ファイルのカラム番号情報
        """
        # 通し番号のcolumns番号
        self.__number_col = (self.table.loc[0][:] == "通し番号").tolist().index(
            True)

        # 読み出すindexのサイズ
        try:
            nan_position = (self.table.T.iloc[self.__number_col, :] ==
                            self.table.T.iloc[self.__number_col, :]).tolist().index(False)
            self.index_size = nan_position
        except Exception as e:
            self.index_size = self.table.index.size

        # 表示用のcolumns番号
        self.__region_col = (self.table.loc[0, :] == "表示用").tolist().index(
            True)
        # 表示用のcolumns番号 ...たまに"表示用"カラムのセルに"想定形"がない場合があるためこちらを利用
        self.__locate_col = (self.table.loc[0, :] == "現市町村名").tolist().index(
            True)

        # 音節のcolumns番号
        self.__syllable_col = (self.table.loc[0, :] == "モーラ").tolist().index(
            True)

        # 最初の子音カラム番号
        self.__first_cons = (
            self.table.loc[0, :] == "1子音").tolist().index(True)

        # 最初の素性アライメント列のカラム番号 (母音も同じ)
        self.__first_columns = (self.cons.columns == "位置").tolist().index(True)

        """
        単語ファイルの地点のインデックス番号情報
        """

        # 想定形のindex番号
        self.__locate_index = (self.table.T.iloc[self.__locate_col, :] == "想定形").tolist().index(
            True)

        self.__max_syllable_num = max(
            # 最大音節数
            [int(x) if (x == x) == True else 0 for x in self.table.T.iloc[self.__syllable_col, 1:self.index_size].tolist()])

        # ビットデータの格納配列
        self.__data_frame = []

        self.__index_name_list = []

    def makeFrameList(self, data_type="a"):
        """
        単語の音素らを素性データベースと照合し、各言語地域の素性リスト作成する
        """
        #locate_idx = range(self.__locate_index, self.index_size)
        fc = range(self.__first_cons, self.__first_cons +
                   2 * self.__max_syllable_num)
        #itertools.product(locate_idx, fc)
        # map(lambda x: lookupBitDataFromOnso(
        #        x[0], x[1]), itertools.product(kk, k))
        for locate_idx in range(self.__locate_index, self.index_size):
            self.__data_frame.append(np.array(
                map(lambda x: self.lookupBitDataFromOnso(locate_idx, x, data_type), fc)).flatten())

        assert self.__data_frame != [], "おかしいな〜"

    def lookupBitDataFromOnso(self, tbl_idx, tbl_col, data_type="a"):
        """
        単語テーブルで指定されたセルの音素から対応するビットデータをルックアップする
        """

        assert data_type == "a" or data_type == "w", "取得したいデータタイプの指定方法: 'a'→素性, 'w'→音素 (default is 'a')"

        # 子音の処理
        if (tbl_col % self.__first_cons) % 2 == 0:
            try:
                index = (
                    self.table.T.iloc[tbl_col][tbl_idx] == self.cons.index).tolist().index(True)
            except Exception as e:
                # print("第{0}列目の子音:{1}がデータベース内から見つかりませんでした。欠損(-9)を割り当てます".format(kk,
                #                                                               self.table.T.iloc[k][kk]))
                # やっぱり音落ち(-1)を割り当てる
                index = self.vowel.index.size - 2

            if data_type == "a":
                return self.cons.iloc[index][:5].values.tolist()
            elif data_type == "w":
                return self.cons.iloc[index][5]
        # 母音の処理
        else:
            try:
                index = (
                    self.table.T.iloc[tbl_col][tbl_idx] == self.vowel.index).tolist().index(True)
            except Exception as e:
                # print("第{0}列目の, 母音:{1}がデータベース内から見つかりませんでした。欠損(-9)を割り当てます".format(kk,
                #                                                                 self.table.T.iloc[k][kk]))
                # やっぱり音落ち(-1)を割り当てる
                index = self.vowel.index.size - 2

            if data_type == "a":
                return self.vowel.iloc[index][:5].values.tolist()
            elif data_type == "w":
                return self.vowel.iloc[index][5]
        return -1

    def setIndecesLabels(self, index_type=0):
        """
        index名とcolumns名をリストに格納
        In case index_type == 0: area_name & word, In case index_type == 1: area_name only, othrewise: word only
        """
        self.__index_name_list = map(lambda x: self.getAreaName(
            x, index_type), range(self.__locate_index, self.index_size))

    def getAreaName(self, idx, index_type=0):
        """
        地点名のリストを取得 出力時のLavelとして表示のさせ方を複数用意
        """
        use_index_name = self.table.iloc[idx][self.__region_col]
        if(use_index_name == use_index_name) == True:
            if idx == self.__locate_index:
                if index_type == 0:
                    return(str("'想定形 " + "".join(self.table.iloc[idx][self.__first_cons:self.__first_cons + self.__max_syllable_num * 2].tolist()) + "'"))
                elif index_type == 1:
                    return(str("'想定形'"))
                else:
                    return(str("".join(self.table.iloc[idx][self.__first_cons:self.__first_cons + self.__max_syllable_num * 2].tolist())))
            else:
                if(index_type == 0):
                    return(str("'" + self.table.iloc[idx][self.__region_col] + " " + "".join(
                        self.table.iloc[idx][self.__first_cons:self.__first_cons + self.__max_syllable_num * 2].tolist()) + "'"))
                elif index_type == 1:
                    return(str("'" + self.table.iloc[idx][self.__region_col] + "'"))
                else:
                    return(str("".join(self.table.iloc[idx][self.__first_cons:self.__first_cons + self.__max_syllable_num * 2].tolist())))
        else:
            return(str('Unnamed_Area'))

    def getBitDataFrame(self):
        return self.__data_frame

    # def get_Original_ArticulationFrame(self):
    #    return self.__art_ori_frame

    def getNameIndex(self):
        if len(self.__index_name_list) == 0:
            return str("(InstancenName).sum_make_index() method is necessary to get the indexName")
        else:
            return self.__index_name_list
