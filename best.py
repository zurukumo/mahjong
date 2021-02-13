import chainer
import chainer.functions as F
import chainer.links as L
import numpy as np


class Model(chainer.Chain):
    def __init__(self):
        super().__init__()
        with self.init_scope():
            self.fc1 = L.Linear(None, 256)
            self.fc2 = L.Linear(None, 256)
            self.fc3 = L.Linear(None, 2)

    def __call__(self, x):
        h = F.relu(self.fc1(x))
        h = F.relu(self.fc2(h))
        return self.fc3(h)


# データ読み込み
f = np.loadtxt('data-3.csv', delimiter=',')
t, x = f[:, :34], f[:, 34:]
t = t.astype('int32')
x = x.astype('float32')

print(f.shape)
ret = [[] for _ in range(f.shape[0])]

# 学習
for pi in range(34):
    model = Model()
    target = L.Classifier(model, lossfun=F.softmax_cross_entropy)
    print('学習モデルmodel-{}を読み込みます．.. .   .'.format(pi))
    chainer.serializers.load_hdf5('model-{}'.format(pi), target)
    print('\t... .  .学習モデルをロードしました')

    with chainer.using_config('train', False), chainer.using_config('enable_backprop', False):
        yyy = target.predictor(x)

    for i, (yn, yt) in enumerate(yyy):
        ret[i].append(yt.data)

c, a = 0, len(ret)

for i, ys in enumerate(ret):
    m = np.argmax(ys)
    if t[i][m] == 1:
        c += 1

print(c, a)


# 41620 330393

# 3330393 6150458 32201116
