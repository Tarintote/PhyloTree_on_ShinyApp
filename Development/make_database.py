#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class VCData2bit():
    def __init__(self, input_table, number_of_element):
        #super(VCData2bit, self).__init__()
        self.table = input_table
        self.__number_of_element = number_of_element - 1

    def showTable(self):
        return(self.table)

    def make_bit(self, bit_length, position):
        bits = "0" * (bit_length)
        bits_list = list(bits)
        bits_list[0] = "1"
        if position != -1:
            bits_list[-(position + 1)] = "1"
        return "".join(bits_list)

    def convert_value2bit_on_table(self):
        """tableの値をビット列に変換"""
        for i in range(len(self.table.columns)):
            bit_length = max(map(int, self.table.values.T[i])) + 2

            bit_list = map(lambda x: self.make_bit(
                bit_length, int(x)), self.table.values.T[i])
            bit_list[-1] = bit_length*"?"
            bit_list[-2] = bit_length*"."
            self.table.iloc[:, i] = bit_list
