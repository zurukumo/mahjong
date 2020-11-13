from collections import defaultdict
import numpy as np

import chainer
import chainer.links as L
import chainer.functions as F
from chainer import Sequential

n_input = 35
n_hidden = 40
n_output = 2

model = []

for pi in range(34):
    net = Sequential(
        L.Linear(n_input, n_hidden), F.relu,
        L.Linear(n_hidden, n_hidden), F.relu,
        L.Linear(n_hidden, n_hidden), F.relu,
        L.Linear(n_hidden, n_hidden), F.relu,
        L.Linear(n_hidden, n_hidden), F.relu,
        L.Linear(n_hidden, n_hidden), F.relu,
        L.Linear(n_hidden, n_output)
    )

    chainer.serializers.load_npz('result{}.net'.format(pi), net)
    model.append(net)

print('model:', len(model))

# tp, fp, fn, tn
result = [[0] * 4 for _ in range(34)]
# pos[(t, y)]
pos = dict()
pos[(0, 0)] = 3  # tn
pos[(0, 1)] = 2  # fn
pos[(1, 0)] = 1  # fp
pos[(1, 1)] = 0  # tp

f = np.loadtxt('sample.csv', delimiter=',')
t_all, x = f[:, :34], f[:, 34:]
x = x[np.random.choice(x.shape[0], 50000, replace=False), :]
t_all = t_all.astype('int32')
x = x.astype('float32')

a = defaultdict(int)
b = defaultdict(int)

for pi in range(9):
    print('pi:', pi)
    t = f[:, pi]
    with chainer.using_config('train', False), chainer.using_config('enable_backprop', False):
        y = model[pi](x)

    print(t[:30])

    for tt, yy in zip(t, y):
        result[pi][pos[tt, np.argmax(yy.data)]] += 1
        a[(pi, tt)] += 1
        b[(pi, np.argmax(yy.data))] += 1


e = 1e-10
with open('stats.txt', 'w') as f:
    for pi in range(34):
        tp, fp, fn, tn = result[pi]
        pre = tp / (tp + fp + e)
        rec = tp / (tp + fn + e)
        f1 = 2 * rec * pre / (rec + pre + e)
        f.write('{} {} {} {} {} {} {} {}\n'.format(
            pi, tp, fp, fn, tn, pre, rec, f1))
        print(pi, tp, fp, fn, tn, pre, rec, f1)

print(a)
print(b)
