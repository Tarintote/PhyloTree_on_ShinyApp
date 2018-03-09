#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import copy


class MakeDistanceMatrix(object):
    def __init__(self, *args):
        self.__distance_matrix = None

    def getDistanceFrame(self):
        return self.__distance_matrix

    def makeHammDistanceFrame(self, data, origin_data):
        # dataは子音母音または調音法の「符号」の配列
        # compareDataは類似性を比較される子音母音自体または調音法名の配列、dataとcompareDataは配列の長さが同じでなければならない
        """重み付きハミング距離で距離行列を作成"""
        init_align = [[0 for row in range(len(data))]
                      for col in range(len(data))]
        for part in range(0, len(data)):  # data全体の配列長 対象の地域用
            for others in range(part, len(data)):  # data全体の配列長 対象外の地域用
                # distance_list = []
                distance = 0
                # ハミング距離に対する類似度重み付け(symilarity)
                # 1地域の配列長(子音と母音の数,もしくは調音方の数)
                for elem in range(0, len(data[part])):
                    symilarity = 1
                    # if (origin_data[part][elem] == ":" or origin_data[others][elem] == ":"):
                    #    symilarity = 0.5
                    # else:
                    #    symilarity = 1
                    distance = distance + symilarity * \
                        self.hammingDistance(
                            data[part][elem], data[others][elem])
                init_align[part][others] = distance
                init_align[others][part] = distance
        self.__distance_matrix = np.array(init_align)

    def hammingDistance(self, purpose, other):
        """目的の配列とそれ以外から各々のハミング距離の計算計算して配列に格納"""
        purpose = list(purpose)
        other = list(other)
        str_length = len(purpose)
        skip = 0
        if str_length != len(other):
            return 0
        result_value = 0

        for k in range(str_length):
            if ("?" in purpose[k]) == True or ("?" in other[k]) == True or ("." in purpose[k]) == True or ("." in other[k]) == True:
                skip += 1
                continue
            if purpose[k] != other[k]:
                result_value += 1

        if (str_length - skip) != 0:
            result_value = float(result_value) / (str_length - skip)
            return result_value
        else:
            return 0

    # 類似度
    def hammingDistance_ver2(self, purpose_, other_):
        """目的の配列とそれ以外から各々のハミング距離の計算計算して配列に格納"""
        purpose = copy.deepcopy(purpose_)
        other = copy.deepcopy(other_)
        str_length = len(purpose)
        skip = 0
        if str_length != len(other):
            return 0
        result_value = 0

        for k in range(str_length):
            if ("-9" == purpose[k]) == True or ("-9" == other[k]) == True or ("-1" == purpose[k]) == True or ("-1" == other[k]) == True:
                skip += 1
                continue
            if purpose[k] == other[k]:
                result_value += 1

        if (str_length - skip) != 0:
            result_value = float(result_value) / (str_length - skip)
            return result_value
        else:
            return 0
