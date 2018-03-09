#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys

def read_library_path():
  file = open('/Library/Python/2.7/site-packages/anaconda_module.pth.way', 'r')
  path_list = file.readlines()
  file.close()
  pl = map(lambda x: "".join(list(x)[0:-1]), path_list[0:-1])
  pl.append(path_list[-1])
  return(pl)

def append_to_sys_path(path_list):
  for i in path_list:
    sys.path.append(i)
