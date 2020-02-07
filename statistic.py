COMB = 2
LEN = 10
LINE = {0: 1670121, 5: 1640467, 10: 1092518}[LEN]
SIZE = 80000
filename = 'sample' + str(COMB) + '-sp-' + str(LEN) + '-inf.csv'

def model_name(pi) :
  return 'result' + str(COMB) + '-sp-' + str(LEN) + '-' + str(pi) + '.net'

import numpy as np
import csv

import chainer
import chainer.links as L
import chainer.functions as F
import sklearn.metrics

from sklearn.model_selection import train_test_split
from chainer import Sequential
from chainer import serializers

import random

n_input = 74 ** COMB + 296
n_hidden = 128
n_output = 2

models = []

for pi in range(34) :
  net = Sequential(
    L.Linear(n_input, n_hidden), F.relu,
    L.Linear(n_hidden, n_hidden), F.relu,
    L.Linear(n_hidden, n_hidden), F.relu,
    L.Linear(n_hidden, n_output)
  )

  chainer.serializers.load_npz(model_name(pi), net)
  models.append(net)

# tp, fp, fn, tn
result = [[0] * 4 for _ in range(34)]
# pos[(t, y)]
pos = dict()
pos[(0, 0)] = 3 # tn
pos[(0, 1)] = 2 # fn
pos[(1, 0)] = 1 # fp
pos[(1, 1)] = 0 # tp

samples = set(random.sample(range(LINE), SIZE))

with open(filename) as f :
  line = f.readline().split(',')
  for i in range(LINE) :
    if not i in samples :
      continue
    print(i)
    x = [[0] * (74 ** COMB + 296)]
    for v in map(int, line[34:]) :
      x[0][v] = 1

    x = np.array(x).astype('float32')

    for pi in range(34) :
      y = int(line[pi])
      with chainer.using_config('train', False), chainer.using_config('enable_backprop', False) :
        t = np.argmax(models[pi](x).data)

        result[pi][pos[(t, y)]] += 1
      
    line = f.readline().split(',')

e = 1e-10
with open('stats' + str(COMB) + '-' + str(LEN) + '.log', 'w') as f :
  for pi in range(34) :
    tp, fp, fn, tn = result[pi]
    pre = tp / (tp + fp + e)
    rec = tp / (tp + fn + e)
    f1 = 2 * rec * pre / (rec + pre + e)
    f.write('{} {} {} {} {} {} {} {}\n'.format(pi, tp, fp, fn, tn, pre, rec, f1))
    print(pi, tp, fp, fn, tn, pre, rec, f1)