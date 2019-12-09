import numpy as np
import pandas as pd
import csv
import chainer
import chainer.links as L
import chainer.functions as F
import sklearn.metrics

from sklearn.model_selection import train_test_split
from chainer import Sequential

file = open('sample.csv', 'r')
f = csv.reader(file, delimiter=",")
t = []
x = []
for row in f :
    row = [int(r) for r in row]
    t_ = [0] * 34
    x_ = [0] * 5772
    for i, v in enumerate(row[:34]) :
        if v == 1 :
            t_[i] = 1
    for i in row[34:] :
        x_[i] = 1
        
    t.append(t_)
    x.append(x_)

t = np.array(t)
x = np.array(x)