import chainer
import numpy as np
import chainer.functions as F
import chainer.links as L
from chainer import Chain, Variable
from sklearn.model_selection import train_test_split


# モデルクラス定義

class LSTM(Chain):
    def __init__(self, n_input, n_hidden, n_output):
        # クラスの初期化
        # :param n_input: 入力層のサイズ
        # :param n_hidden: 隠れ層のサイズ
        # :param n_output: 出力層のサイズ
        super(LSTM, self).__init__(
            xh=L.Linear(n_input, n_hidden),
            hh=L.LSTM(n_hidden, n_hidden),
            hy=L.Linear(n_hidden, n_output)
        )

    def __call__(self, x, t=None, train=False):
        # 順伝播の計算を行う関数
        # :param x: 入力値
        # :param t: 正解の予測値
        # :param train: 学習かどうか
        # :return: 計算した損失 or 予測値
        x = Variable(x)
        if train:
            t = Variable(t)
        h = self.xh(x)
        h = self.hh(h)
        y = self.hy(h)
        if train:
            return F.mean_squared_error(y, t)
        else:
            return y.data

    def reset(self):
        # 勾配の初期化とメモリの初期化
        self.zerograds()
        self.hh.reset_state()


for pi in range(9):
    f = np.loadtxt('sample-{}.csv'.format(pi), delimiter=',')
    t, x = f[:, 0], f[:, 1:]
    t = t.astype('int32')
    x = x.astype('float32')
    x_train, x_val, t_train, t_val = train_test_split(x, t, test_size=0.05)

    model = LSTM(n_input=35, n_hidden=64, n_output=2)
    optimizer = chainer.optimizers.Adam()
    optimizer.setup(model)

    n_epoch = 1000
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
            model.reset()
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
