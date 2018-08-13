#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import copy


class HammingDistanceMatrix(object):
    def __init__(self, *args):
        self.__distance_matrix = None

    def getDistanceMatrix(self):
        return self.__distance_matrix

    def calcHammingDistanceMatrix(self, data):
        # dataは子音母音または素性の「符号」の配列
        # compareDataは類似性を比較される子音母音自体または調音法名の配列、dataとcompareDataは配列の長さが同じでなければならない
        """重み付きハミング距離で距離行列を作成"""
        init_matrix = pd.DataFrame(
            [[0.0 for i in range(len(data))] for k in range(len(data))])
        col, idx = np.triu_indices_from(init_matrix, k=0)
        for c, i in zip(col, idx):
            # ハミング距離に対する類似度重み付け, default=1
            symilarity = 1
            # 言語地域間の距離
            distance = sum(map(lambda x: symilarity * self.calchammingDistance(
                data[c][x], data[i][x]), range(len(data[c]))))
            init_matrix[i][c] = distance
        init_matrix.T.values[np.triu_indices_from(
            init_matrix, k=0)] = init_matrix.values[np.triu_indices_from(init_matrix, k=0)]
        self.__distance_matrix = init_matrix

    def calchammingDistance(self, purpose, other):
        """目的の配列とそれ以外から各々のハミング距離の計算計算して配列に格納"""
        purpose = list(purpose)
        other = list(other)
        str_length = len(purpose)
        assert str_length == len(other)

        skip = 0
        result_value = 0

        for k in range(str_length):
            if ("?" in purpose[k]) == True or ("?" in other[k]) == True:
                skip += 1
                continue
            if purpose[k] != other[k]:
                result_value += 1

        if (str_length - skip) != 0:
            result_value = float(result_value) / (str_length - skip)
            return result_value
        else:
            return 0
