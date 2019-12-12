# 1列 0~33まで
# input -> sample.csv (2000半荘分)

import numpy as np
import pandas as pd
import csv
import chainer
import chainer.links as L
import chainer.functions as F
import sklearn.metrics

from sklearn.model_selection import train_test_split
from chainer import Sequential

file = open('sample1.csv', 'r')
f = csv.reader(file, delimiter=",")
t = []
x = []
for row in f :
    row = [int(r) for r in row]
    t_ = [0] * 34
    x_ = [0] * (74 + 296)
    for i, v in enumerate(row[:34]) :
        if v == 1 :
            t_[i] = 1
    for i in row[34:] :
        x_[i] = 1
        
    t.append(t_)
    x.append(x_)

t = np.array(t)
x = np.array(x)

x = x.astype('float32')
t = t.astype('int32')

print('loaded')

for pi in range(4, 5) :
    t_ = t[:, pi]
    x_train_val, x_test, t_train_val, t_test = train_test_split(x, t_, test_size=0.3, random_state=0)
    x_train, x_val, t_train, t_val = train_test_split(x_train_val, t_train_val, test_size=0.3, random_state=0)
    
    # net としてインスタンス化
    n_input = (74 + 296)
    n_hidden = 100
    n_output = 2

    net = Sequential(
        L.Linear(n_input, n_hidden), F.relu,
        L.Linear(n_hidden, n_hidden), F.relu,
        L.Linear(n_hidden, n_output)
    )
    
    optimizer = chainer.optimizers.SGD(lr=0.01)
    optimizer.setup(net)
    
    n_epoch = 30
    n_batchsize = 16
    
    iteration = 0

    # ログの保存用
    results_train = {
        'loss': [],
        'accuracy': []
    }
    results_valid = {
        'loss': [],
        'accuracy': []
    }


    for epoch in range(n_epoch):
        # データセット並べ替えた順番を取得
        order = np.random.permutation(range(len(x_train)))

        # 各バッチ毎の目的関数の出力と分類精度の保存用
        loss_list = []
        accuracy_list = []
        for i in range(0, len(order), n_batchsize):
            # バッチを準備
            index = order[i:i+n_batchsize]
            x_train_batch = x_train[index,:]
            t_train_batch = t_train[index]

            # 予測値を出力
            y_train_batch = net(x_train_batch)

            # 目的関数を適用し、分類精度を計算
            loss_train_batch = F.softmax_cross_entropy(y_train_batch, t_train_batch)
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

        with open('result1-' + str(pi) + '.txt', 'a') as f :
            # 結果の表示
            ret = 'epoch:{}, iteration:{}, loss(train):{}, loss(valid):{}, acc(train):{}, acc(valid):{}, precision0:{}, precision1:{}, recall0:{}, recall1:{}, f1score0:{}, f1score1:{}'.format(epoch, iteration, loss_train, loss_val.array, accuracy_train, accuracy_val.array, summary[0][0], summary[0][1], summary[1][0], summary[1][1], summary[2][0], summary[2][1])
            print(ret)
            f.write(ret + "\n")