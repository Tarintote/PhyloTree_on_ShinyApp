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
        col, idx = np.triu_indices_from(init_matrix, k=1)
        dist_array = list(map(lambda x: self.calcHammingDistance(data[x[0]], data[x[1]]), zip(col, idx)))

        init_matrix.values[np.triu_indices_from(
            init_matrix, k=1)] = dist_array
        init_matrix.T.values[np.triu_indices_from(
            init_matrix, k=1)] = dist_array

        self.__distance_matrix = init_matrix

    def calcHammingDistance(self, array1, array2):
        """2つの配列間のハミング距離の計算して配列に格納"""
        a1 = list(array1)
        a2 = list(array2)
        str_length = len(a1)
        assert str_length == len(a2)

        skip = 0.0
        result_value = 0.0

        for k in range(str_length):
            if ("?" == a1[k]) or ("?" == a2[k]):
                skip += 1.0
                continue
            if a1[k] != a2[k]:
                result_value += 1.0

        if (str_length - skip) != 0:
            return result_value / (str_length - skip)
        else:
            return 0
