
import csv

import chainer
import chainer.functions as F
import chainer.links as L
import numpy as np
from chainer import Chain, serializers, training
from chainer.datasets import TupleDataset
from chainer.training import extensions
from sklearn.model_selection import train_test_split


file_name = 'richi'
n_output = 2

epoch = 150
batch_size = 256
frequency = -1


class CNN(Chain):
    def __init__(self, n_output):
        super(CNN, self).__init__()
        with self.init_scope():
            ksize = (5, 2)
            self.conv1 = L.Convolution2D(in_channels=None, out_channels=100, ksize=ksize)
            self.conv2 = L.Convolution2D(in_channels=None, out_channels=100, ksize=ksize)
            self.conv3 = L.Convolution2D(in_channels=None, out_channels=100, ksize=ksize)
            self.bnorm1 = L.BatchNormalization(100)
            self.bnorm2 = L.BatchNormalization(100)
            self.bnorm3 = L.BatchNormalization(100)
            self.fc1 = L.Linear(None, 300)
            self.fc2 = L.Linear(None, n_output)

    def __call__(self, x):
        # 1層
        h = self.conv1(x)
        h = self.bnorm1(h)
        h = F.relu(h)
        h = F.dropout(h, ratio=0.5)
        # 2層
        h = self.conv2(h)
        h = self.bnorm2(h)
        h = F.relu(h)
        h = F.dropout(h, ratio=0.5)
        # 3層
        h = self.conv3(h)
        h = self.bnorm3(h)
        h = F.relu(h)
        h = F.dropout(h, ratio=0.5)
        # 平坦化
        h = h.reshape(-1, 2200)
        # 4層
        h = self.fc1(h)
        h = F.relu(h)
        h = F.dropout(h, ratio=0.5)
        # 5層
        h = self.fc2(h)
        return h


model = L.Classifier(CNN(n_output=n_output))
# serializers.load_npz("mymodel.npz", model)

gpu_device = 0
chainer.cuda.get_device_from_id(0)
model.to_gpu()

optimizer = chainer.optimizers.Adam()
optimizer.setup(model)


# データ準備
x = []
t = []
with open(file_name + '.csv') as f:
    reader = csv.reader(f, delimiter=",")
    for row in reader:
        row = list(map(int, row))
        tt, row = row[0], row[1:]
        xx = []
        for i in range(len(row) // 34):
            xxx = []
            for j in range(34):
                xxx.append([1 if row[i * 34 + j] >= k else 0 for k in range(1, 5)])
            xx.append(xxx)
        x.append(xx)
        t.append(tt)

x = np.array(x, np.float32)
t = np.array(t, np.int32)

dataset = TupleDataset(x, t)
train, test = train_test_split(dataset, test_size=0.3)

train_iter = chainer.iterators.SerialIterator(train, batch_size)
test_iter = chainer.iterators.SerialIterator(test, batch_size, repeat=False, shuffle=False)

updater = training.StandardUpdater(train_iter, optimizer, device=gpu_device)
trainer = training.Trainer(updater, (epoch, 'epoch'))

trainer.extend(extensions.Evaluator(test_iter, model, device=gpu_device))
trainer.extend(extensions.dump_graph('main/loss'))

frequency = epoch if frequency == -1 else max(1, frequency)
trainer.extend(extensions.snapshot(), trigger=(frequency, 'epoch'))
trainer.extend(extensions.LogReport())
trainer.extend(
    extensions.PlotReport(['main/loss', 'validation/main/loss'],
                          'epoch', file_name='loss.png'))
trainer.extend(
    extensions.PlotReport(['main/accuracy', 'validation/main/accuracy'],
                          'epoch', file_name='accuracy.png'))
trainer.extend(extensions.PrintReport(
    ['epoch', 'main/loss', 'validation/main/loss',
     'main/accuracy', 'validation/main/accuracy', 'elapsed_time']))

trainer.run()

serializers.save_npz(file_name + '.npz', model)
