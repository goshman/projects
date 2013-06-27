"""
1 parameter - filename
2 parameter - final line start position
3 parameter - final line finish position
"""
# -*- coding: utf-8 -*-
import sys

doc = sys.argv[1]
line_start_char_num = int(sys.argv[2])
line_end_char_num = int(sys.argv[3]) + 1

f = open(doc, 'r')
fl = f.readlines()
for line in fl:
	xxx = line[line_start_char_num:line_end_char_num]
	print xxx
f.close()	