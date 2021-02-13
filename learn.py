import chainer
import chainer.functions as F
import chainer.links as L
import numpy as np
from chainer import iterators, training
from chainer.datasets import split_dataset_random, tuple_dataset
from chainer.training import extensions

DEVICE = 0


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


# 学習
for pi in range(34):
    model = Model()
    if DEVICE >= 0:
        chainer.cuda.get_device_from_id(0).use()
        chainer.cuda.check_cuda_available()
        model.to_gpu()

    target = L.Classifier(model, lossfun=F.softmax_cross_entropy)
    optimizer = chainer.optimizers.Adam()
    optimizer.setup(target)

    for fi in range(1):
        print('pi: {}, fi: {}'.format(pi, fi))

        n_epoch = 1000
        n_batchsize = 1024
        iteration = 0

        # データの準備
        f = np.loadtxt('data-{}.csv'.format(fi), delimiter=',')
        t, x = f[:, pi], f[:, 34:]
        t = t.astype('int32')
        x = x.astype('float32')
        dataset = tuple_dataset.TupleDataset(x, t)

        trn, vld = split_dataset_random(dataset, int(len(dataset)*0.8), seed=0)
        t_iterator = iterators.SerialIterator(trn, n_batchsize, shuffle=True)
        v_iterator = iterators.SerialIterator(vld, n_batchsize, repeat=False, shuffle=False)
        updater = training.StandardUpdater(t_iterator, optimizer, device=DEVICE)  # GPU
        trainer = training.Trainer(updater, (n_epoch, 'epoch'), out='result')

        trainer.extend(extensions.Evaluator(v_iterator, target, device=DEVICE))  # GPU
        trainer.extend(extensions.LogReport())
        trainer.extend(extensions.PrintReport(['epoch', 'main/loss', 'main/accuracy', 'validation/main/accuracy']))
        trainer.extend(extensions.ProgressBar())
        trainer.extend(extensions.PlotReport(
            ['main/loss', 'validation/main/loss'], x_key='epoch', file_name='loss.png'))
        trainer.extend(extensions.PlotReport(
            ['main/accuracy', 'validation/main/accuracy'], x_key='epoch', file_name='accuracy.png'))

        trainer.run()

    print('学習モデルmodel-{}を保存します．.. .   .'.format(pi))
    chainer.serializers.save_hdf5('model-{}'.format(pi), target)
    print('\t... .  .学習モデルを保存しました')
