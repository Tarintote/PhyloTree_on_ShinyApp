#!/usr/bin/env python
# -*- coding: utf-8 -*-


class MakeBitFrame(object):
    def __init__(self, input_word_table, consonant_table, vowel_table):
        self.table = input_word_table
        self.cons = consonant_table
        self.vowel = vowel_table

        """単語ファイルのカラム番号情報"""
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

        """単語ファイルの地点のインデックス番号情報"""

        # 想定形のindex番号
        self.__locate_index = (self.table.T.iloc[self.__locate_col, :] == "想定形").tolist().index(
            True)

        self.__max_syllable_num = max(
            # 最大音節数
            [int(x) if (x == x) == True else 0 for x in self.table.T.iloc[self.__syllable_col, 1:self.index_size].tolist()])

        self.__art_frame = []
        self.__art_ori_frame = []
        self.__word_frame = []

        self.__index_name_list = []

    def makeFrameList(self):
        """単語の音素らを素性データベースと照合し、各言語地域の素性リスト作成する"""

        for kk in range(self.__locate_index, self.index_size):
            if(self.table.loc[kk][self.__region_col] == "岩波" or self.table.loc[kk][self.__region_col] == "鹿児島" or self.table.loc[kk][self.__region_col] == "種子" or self.table.loc[kk][self.__region_col] == "八丈" or self.table.iloc[kk][self.__region_col] == "OCLS"):
                continue
            art_lists = []
            word_lists = []
            for k in range(self.__first_cons, self.__first_cons + 2 * self.__max_syllable_num):
                # 子音の処理
                if (k % self.__first_cons) % 2 == 0:
                    try:
                        index = (
                            self.table.T.iloc[k][kk] == self.cons.index).tolist().index(True)
                    except Exception as e:
                        # print("第{0}列目の子音:{1}がデータベース内から見つかりませんでした。欠損(-9)を割り当てます".format(kk,
                        #                                                               self.table.T.iloc[k][kk]))
                        # やっぱり音落ち(-1)を割り当てる
                        index = self.cons.index.size - 2

                    art_lists = art_lists + \
                        self.cons.iloc[index][:5].values.tolist()

                    word_lists.append(self.cons.iloc[index][5])
                # 母音の処理
                else:
                    try:
                        index = (
                            self.table.T.iloc[k][kk] == self.vowel.index).tolist().index(True)
                    except Exception as e:
                        # print("第{0}列目の, 母音:{1}がデータベース内から見つかりませんでした。欠損(-9)を割り当てます".format(kk,
                        #                                                                 self.table.T.iloc[k][kk]))
                        # やっぱり音落ち(-1)を割り当てる
                        index = self.vowel.index.size - 2

                    art_lists = art_lists + \
                        self.vowel.iloc[index][:5].values.tolist()

                    word_lists.append(self.vowel.iloc[index][5])

            assert art_lists != [], "素性が見つかりませんでした"

            self.__art_frame.append(art_lists)
            self.__word_frame.append(word_lists)
        return 0

    def makeIndeces(self, index_type=0):
        """index名とcolumns名をリストに格納"""
        """In case index_type == 0: area_name & word, In case index_type == 1: area_name only, othrewise: word only """
        # for i in range(self.__first_of_index, self.table.index.size):
        for i in range(self.__locate_index, self.index_size):
            if(self.table.iloc[i][self.__region_col] == "岩波" or self.table.iloc[i][self.__region_col] == "鹿児島" or self.table.iloc[i][self.__region_col] == "種子" or self.table.iloc[i][self.__region_col] == "八丈" or self.table.iloc[i][self.__region_col] == "OCLS"):
                continue
            use_index_name = self.table.iloc[i][self.__region_col]
            if(use_index_name == use_index_name) == True:
                if i == self.__locate_index:
                    if index_type == 0:
                        self.__index_name_list.append("'想定形 " + "".join(
                            self.table.iloc[i][self.__first_cons:self.__first_cons + self.__max_syllable_num * 2].tolist()) + "'")
                    elif index_type == 1:
                        self.__index_name_list.append(
                            "'想定形'")
                    else:
                        self.__index_name_list.append("".join(
                            self.table.iloc[i][self.__first_cons:self.__first_cons + self.__max_syllable_num * 2].tolist()))
                else:
                    if(index_type == 0):
                        self.__index_name_list.append(
                            "'" + self.table.iloc[i][self.__region_col] + " " + "".join(
                                self.table.iloc[i][self.__first_cons:self.__first_cons + self.__max_syllable_num * 2].tolist()) + "'")
                    # self.__index_name_list.append(" ".join(
                    #    self.table.iloc[i][self.__first_cons:self.__first_cons + self.__max_syllable_num * 2].tolist()))
                    elif index_type == 1:
                        self.__index_name_list.append(
                            "'" + self.table.iloc[i][self.__region_col] + "'")
                    else:
                        self.__index_name_list.append("".join(
                            self.table.iloc[i][self.__first_cons:self.__first_cons + self.__max_syllable_num * 2].tolist()))

            else:
                self.__index_name_list.append('想定形')

    def getWordFrame(self):
        return self.__word_frame

    def getArticulationFrame(self):
        return self.__art_frame

    # def get_Original_ArticulationFrame(self):
    #    return self.__art_ori_frame

    def getNameIndex(self):
        if len(self.__index_name_list) == 0:
            return str("(InstancenName).sum_make_index() method is necessary to get the indexName")
        else:
            return self.__index_name_list

    def joinAlignments(self, alignList):
        """子音、母音ごとの要素に分かれている場合、この関数を用いて1地域1つのシーケンスとしてリストに格納し直す"""
        saveAlign = []
        returnAlignment = []
        for k in range(len(alignList)):
            saveAlign = "".join(alignList[k])
            returnAlignment.append(saveAlign)
        return returnAlignment

    def searchLoss(self, align_list):
        delete_index_list = []
        for x in range(len(align_list)):
            if ("1" in list(align_list[x])) == False and ("0" in list(align_list[x])) == False:
                delete_index_list.append(x)
        return delete_index_list

    def searchNanElem(self, data_list):
        have_non_index = []
        nan_check = [[i == i for i in x] for x in data_list]
        for ncl in nan_check:
            if False in ncl:
                have_non_elem = ncl
                have_non_index.append(nan_check.index(have_non_elem))
        return have_non_index

    def deleteNanElem(self, indeces, any_list):
        delete_count = 0
        if len(indeces) == 0:
            return any_list
        for k in indeces:
            any_list.pop(k - delete_count)
            delete_count += 1
        return any_list
