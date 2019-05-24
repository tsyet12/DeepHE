
from gekko import GEKKO
import numpy as np
import numpy.random as random
import csv
import pandas as pd
import ast


data=pd.read_csv('data/train.csv',names=['T_hot','T_cold','wh','wc','Qm','obj'])
npdata=data.values
print(npdata)
print(npdata.shape[1])






'''
with open('data/train.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
            line_count += 1
    print(f'Processed {line_count} lines.')
'''