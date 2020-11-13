from sklearn.model_selection import train_test_split
import chainer.functions as F
import chainer.links as L
import chainer
import numpy as np


class Model(chainer.Chain):
    def __init__(self):
        super().__init__()
        with self.init_scope():
            self.conv1 = L.Convolution2D(
                in_channels=None, out_channels=32, ksize=3, stride=1, pad=1)
            self.conv2 = L.Convolution2D(
                in_channels=None, out_channels=64, ksize=3, stride=1, pad=1)
            self.conv3 = L.Convolution2D(
                in_channels=None, out_channels=128, ksize=3, stride=1, pad=1)
            self.conv4 = L.Convolution2D(
                in_channels=None, out_channels=128, ksize=3, stride=1, pad=1)
            self.fc5 = L.Linear(None, 1000)
            self.fc6 = L.Linear(None, 2)

    def forward(self, x):
        h = F.relu(self.conv1(x.reshape((-1, 1, 5, 7))))
        h = F.max_pooling_2d(h, ksize=2, stride=2)
        h = F.relu(self.conv2(h))
        h = F.max_pooling_2d(h, ksize=2, stride=2)
        h = F.relu(self.conv3(h))
        h = F.max_pooling_2d(h, ksize=2, stride=2)
        h = F.relu(self.conv4(h))
        h = F.relu(self.fc5(h))
        return self.fc6(h)


for pi in range(9):
    f = np.loadtxt('sample-{}.csv'.format(pi), delimiter=',')
    t, x = f[:, 0], f[:, 1:]
    t = t.astype('int32')
    x = x.astype('float32')
    x_train, x_val, t_train, t_val = train_test_split(x, t, test_size=0.05)

    # net としてインスタンス化
    model = Model()
    optimizer = chainer.optimizers.Adam()
    optimizer.setup(model)

    n_epoch = 200
    n_batchsize = 1024
    iteration = 0
    for epoch in range(n_epoch):
        # データセット並べ替えた順番を取得
        order = np.random.permutation(range(len(x_train)))

        # 各バッチ毎の目的関数の出力と分類精度の保存用
        loss_list = []
        accuracy_list = []
        for i in range(0, len(order), n_batchsize):
            # バッチを準備
            index = order[i:i + n_batchsize]
            x_train_batch = x_train[index, :]
            t_train_batch = t_train[index]

            # 予測値を出力
            y_train_batch = model(x_train_batch)

            # 目的関数を適用し、分類精度を計算
            loss_train_batch = F.softmax_cross_entropy(
                y_train_batch, t_train_batch)
            accuracy_train_batch = F.accuracy(y_train_batch, t_train_batch)

            loss_list.append(loss_train_batch.array)
            accuracy_list.append(accuracy_train_batch.array)

            # 勾配のリセットと勾配の計算
            model.cleargrads()
            loss_train_batch.backward()

            # パラメータの更新
            optimizer.update()

            # カウントアップ
            iteration += 1

        # 訓練データに対する目的関数の出力と分類精度を集計
        loss_train = np.mean(loss_list)
        accuracy_train = np.mean(accuracy_list)

        # 1エポック終えたら、検証データで評価
        # 検証データで予測値を出力
        with chainer.using_config('train', False), chainer.using_config('enable_backprop', False):
            y_val = model(x_val)

        # 目的関数を適用し、分類精度を計算
        loss_val = F.softmax_cross_entropy(y_val, t_val)
        accuracy_val = F.accuracy(y_val, t_val)
        summary = F.classification_summary(y_val, t_val)

        # 結果の表示
        print('epoch:{}, iteration:{}, loss(train):{}, loss(valid):{}, acc(train):{}, acc(valid):{}'.format(
            epoch, iteration, loss_train, loss_val.array, accuracy_train, accuracy_val.array
        ))

    # モデルを保存
    chainer.serializers.save_npz('result' + str(pi) + '.net', model)

    # 集計
    # tp, fp, fn, tn
    result = [0] * 4
    # pos[(t, y)]
    pos = dict()
    pos[(0, 0)] = 3  # tn
    pos[(0, 1)] = 2  # fn
    pos[(1, 0)] = 1  # fp
    pos[(1, 1)] = 0  # tp
    for tt, yy in zip(t_val, model(x_val)):
        result[pos[tt, np.argmax(yy.data)]] += 1
        print(tt, yy.data, np.argmax(yy.data))

    e = 1e-10
    with open('stats.txt', 'a') as f:
        tp, fp, fn, tn = result
        pre = tp / (tp + fp + e)
        rec = tp / (tp + fn + e)
        f1 = 2 * rec * pre / (rec + pre + e)
        f.write('{} {} {} {} {} {} {} {}\n'.format(
            pi, tp, fp, fn, tn, pre, rec, f1))
        print(pi, tp, fp, fn, tn, pre, rec, f1)
