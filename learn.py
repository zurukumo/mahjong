from chainer import Sequential
from sklearn.model_selection import train_test_split
import chainer.functions as F
import chainer.links as L
import chainer
import numpy as np

for pi in range(9):
    f = np.loadtxt('sample-{}.csv'.format(pi), delimiter=',')
    t, x = f[:, 0], f[:, 1:]
    x = x.astype('float32')
    t = t.astype('int32')
    x_train_val, x_test, t_train_val, t_test = train_test_split(
        x, t, test_size=0.3)
    x_train, x_val, t_train, t_val = train_test_split(
        x_train_val, t_train_val, test_size=0.3)

    # net としてインスタンス化
    n_input = 34
    n_hidden = 40
    n_output = 2

    net = Sequential(
        L.Linear(n_input, n_hidden), F.relu,
        L.Linear(n_hidden, n_hidden), F.relu,
        L.Linear(n_hidden, n_hidden), F.relu,
        L.Linear(n_hidden, n_hidden), F.relu,
        L.Linear(n_hidden, n_output)
    )

    optimizer = chainer.optimizers.Adam()
    optimizer.setup(net)

    n_epoch = 100
    n_batchsize = 32
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
            y_train_batch = net(x_train_batch)

            # 目的関数を適用し、分類精度を計算
            loss_train_batch = F.softmax_cross_entropy(
                y_train_batch, t_train_batch)
            accuracy_train_batch = F.accuracy(y_train_batch, t_train_batch)

            loss_list.append(loss_train_batch.array)
            accuracy_list.append(accuracy_train_batch.array)

            # 勾配のリセットと勾配の計算
            net.cleargrads()
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
            y_val = net(x_val)

        # 目的関数を適用し、分類精度を計算
        loss_val = F.softmax_cross_entropy(y_val, t_val)
        accuracy_val = F.accuracy(y_val, t_val)
        summary = F.classification_summary(y_val, t_val)

        # 結果の表示
        ret = 'epoch:{}, iteration:{}, loss(train):{}, loss(valid):{}, acc(train):{}, acc(valid):{}, precision0:{}, precision1:{}, recall0:{}, recall1:{}, f1score0:{}, f1score1:{}'.format(
            epoch, iteration, loss_train, loss_val.array, accuracy_train, accuracy_val.array, summary[0][0], summary[0][1], summary[1][0], summary[1][1], summary[2][0], summary[2][1])
        print(ret)

    chainer.serializers.save_npz('result' + str(pi) + '.net', net)
