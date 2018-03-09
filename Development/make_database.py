#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class VCBase(object):
    def __init__(self):
        self.table = None

    def showTable(self):
        return(self.table)

    def __making_bit(self, bit_length, position):
        bits = "0" * (bit_length)
        bits_list = list(bits)
        bits_list[0] = "1"
        if position != -1:
            bits_list[-(position + 1)] = "1"
        return "".join(bits_list)

    def inputBit(self, index_length, bitLength, column):
        for index_len in range(0, index_length + 2):
            if index_len == index_length:
                self.table.loc[index_len, column] = "?" * bitLength
            elif index_len == index_length + 1:
                self.table.loc[index_len, column] = "." * bitLength
            else:
                self.table.loc[index_len, column] = self.__making_bit(
                    bitLength, int(self.table.loc[index_len, column]))
        return self.table

    def inputBitforWord(self, index_length, bitLength):
        for index_len in range(0, index_length + 2):
            if index_len == index_length:
                self.table.iloc[[index_len], [0]] = "?" * bitLength
            elif index_len == index_length + 1:
                self.table.iloc[[index_len], [0]] = "." * bitLength
            else:
                self.table.iloc[[index_len], [0]] = self.__making_bit(
                    bitLength, index_len)
        return self.table

    def generate_table_for_ward(self):
        raise NotImplementedError

    def generate_table_for_art(self):
        raise NotImplementedError


class VCDataBase(VCBase):
    def __init__(self, input_table, number_of_element):
        super(VCDataBase, self).__init__()
        self.table = input_table
        self.__number_of_element = number_of_element - 1

    def generate_table_for_ward(self):
        index_length = self.__number_of_element
        bitLength = index_length + 1
        self.table = self.inputBitforWord(index_length, bitLength)

    def generate_table_for_art(self):
        index_length = self.__number_of_element
        for i in range(2, 7):
            col = self.table.columns[i]
            property_ = self.table.iloc[0:index_length][col]
            property_bitLength = max([int(i)
                                      for i in property_.tolist()]) + 2

            self.table = self.inputBit(index_length,
                                       property_bitLength, col)
