#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
from scipy import linalg
import copy
from multiprocessing import Pool
import multiprocessing as multi
from joblib import Parallel, delayed

#"."と"?"を持つ列を削除


def del_n_index(vector_):
    """
    データ内のk列に"."もしくは"?"が存在していればそのk点でのデータは削除する
    """
    for k in range(len(vector_)):
        while 1:
            try:
                dot_num = vector_[k].tolist().index(".")
                vector_ = map(lambda x: np.delete(x, dot_num), vector_)
            except Exception as e:
                break
        while 1:
            try:
                que_num = vector_[k].tolist().index("?")
                vector_ = map(lambda x: np.delete(x, que_num), vector_)
            except Exception as e:
                break
    return vector_


def convert2float(data_vec):
    """
    データタイプをfloat型に変換, dataが数値(文字)が前提
    """
    for k in range(len(data_vec)):
        data_vec[k] = map(float, data_vec[k])
    return data_vec
    # 平方和

# ベクトルの内積


def dot_product(v1, v2):
    dotp = 0
    for z1, z2 in zip(v1, v2):
            # if z1=="." or z1=="?" or z2=="." or z2=="?": continue
        dotp = dotp + int(z1) * int(z2)
    return dotp

#


def sum_of_square(vec):
    sos = 0
    for z1 in vec:
        # if z1=="." or z1=="?": continue
        sos = sos + int(z1) * int(z1)
    return np.sqrt(sos)

# コサイン類似度


def cos_sim(v1, v2):
    return dot_product(v1, v2) / (sum_of_square(v1) * sum_of_square(v2))

# 相関係数の逆行列


def Inv_Correlation(correlation_matrix):
    return np.linalg.inv(np.array(correlation_matrix))

#
# 分散共分散行列生成
#

# データの平均リスト E[x]


def mean_vec(v):
    if len(v) == 0:
        print("vectorの長さが0です。データがありません。")
        return 0
    """
    sum_num = count = 0
    for i in range(len(v)):
            # if v[i] == "." or v[i] == "?":
            #    continue
        sum_num = sum_num + int(v[i])
        count = count + 1
    return float(sum_num) / count
    """
    return np.mean(v, dtype=float)

# 差ベクトル生成


def dist_vector(v1, v2):
    dispersion = []
    for k in range(len(v1)):
        # if v1[k] == "." or v1[k] == "?":
        #    dispersion.append(v1[k])
        # else:
        dispersion.append(float(v1[k]) - v2)  # np.power
    return dispersion


def co_valiance(v1, v2):
    cov = 0
    count = 0
    for i in range(len(v1)):
        if v1[i] == "." or v1[i] == "?" or v2[i] == "." or v2[i] == "?":
            continue
        else:
            cov = cov + (v1[i] * v2[i])
            count += 1
    return float(cov) / count


# 標本分散共分散行列作成

def covaliance_matrix(vectors):
    """
    means_vec = map(mean_vec, vectors)
    dist_vec = []
    for n in range(len(vectors)):
        dist_vec.append(dist_vector(vectors[n], means_vec[n]))
    cov_matrix = [[0 for i in range(len(vectors))]
                  for k in range(len(vectors))]
    for i in range(len(dist_vec)):
        for k in range(i, len(dist_vec)):
            cov_matrix[i][k] = co_valiance(dist_vec[i], dist_vec[k])
            cov_matrix[k][i] = cov_matrix[i][k]
    return cov_matrix
    """
    return np.cov(vectors, bias=1)

#
# 偏相関係数行列作成
#


def General_Inverse_Matrix(matrix):
    # 特異値分解(singular value decomposition)
    U, s, V_t = np.linalg.svd(matrix, full_matrices=True)

    rank = np.linalg.matrix_rank(np.array(matrix))
    downed_rank = len(matrix) - np.linalg.matrix_rank(np.array(matrix))

    # step2 sの逆行列のrank落ちした部分を0に変更
    for i in range(downed_rank):
        s[-(i + 1)] = 0

    object_s = np.diag(s[0:rank])
    inv_object_s = np.linalg.inv(object_s)
    a = np.array([np.append(inv_object_s[x], [0 for x in range(downed_rank)])
                  for x in range(rank)])
    inv_s = a.tolist()
    for k in range(downed_rank):
        inv_s.append(([0.0 for x in range(len(matrix))]))

    # 逆行列
    return np.dot(np.dot(V_t.T, np.array(inv_s)), U.T)
    # return np.linalg.pinv(matrix)

# ピアソン係数


def Correlation_Matrix(cov_matrix):
    correlation_matrix = [[0 for i in range(len(cov_matrix))]
                          for k in range(len(cov_matrix))]
    for i in range(len(np.array(cov_matrix))):
        for k in range(i, len(np.array(cov_matrix))):
            correlation_matrix[i][k] = (cov_matrix[i][k] /
                                        np.sqrt((cov_matrix[i][i] * cov_matrix[k][k])))
            correlation_matrix[k][i] = correlation_matrix[i][k]
    return correlation_matrix


# 偏相関係数行列


def Partial_Correlation(rxy, rxz, ryz):
    """except effect of valiable z"""
    return (rxy - (rxz * ryz)) / ((np.sqrt(1 - rxz**2) * (np.sqrt(1 - ryz**2))))


def Partial_Correlation_Matrix(correlation_matrix):
    inv_correlation_matrix = Inverse_Matrix(correlation_matrix)
    partial_correlation_matrix = [[0 for i in range(len(correlation_matrix))]
                                  for k in range(len(correlation_matrix))]
    # 逆行列を用いた偏相関係数の算出
    for i in range(len(correlation_matrix)):
        for k in range(i, len(correlation_matrix)):
            partial_correlation_matrix[i][k] = -(inv_correlation_matrix[i][k] /
                                                 np.sqrt(inv_correlation_matrix[i][i] * inv_correlation_matrix[k][k]))
            partial_correlation_matrix[k][i] = partial_correlation_matrix[i][k]
    return partial_correlation_matrix

    # 行列の低ランク近似


def low_rank_svd(a, rank):
    u, s, v = linalg.svd(a)
    ur = u[:, :rank]
    sr = np.matrix(linalg.diagsvd(s[:rank], rank, rank))
    vr = v[:rank, :]
    return np.dot(np.dot(ur, sr), vr)
