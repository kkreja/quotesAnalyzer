# coding: utf-8
import pandas
p = pandas.read_csv('CCC.mst')
print p[:2]
print p[:2]['<VOL>']
print p[:2]['<OPEN>']
