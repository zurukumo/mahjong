import numpy as np
from sklearn.svm import SVC

# テストデータ準備
print('テストデータ読み込み')
test = np.loadtxt('sample.csv', delimiter=',')
test = test[np.random.choice(test.shape[0], 50000, replace=False), :]
t_test_all, x_test = test[:, :34], test[:, 34:]
t_test_all = t_test_all.astype('int32')
x_test = x_test.astype('float32')
print(test[0])
print(test[1])
print(test[2])


print('学習開始')
for pi in range(9):
    print('牌:', pi)
    f = np.loadtxt('sample-mini-{}.csv'.format(pi), delimiter=',')
    t_train, x_train = f[:, 0], f[:, 1:]
    t_train = t_train.astype('int32')
    x_train = x_train.astype('float32')

    print('fit')
    model = SVC(kernel='linear', random_state=None)
    model.fit(x_train, t_train)

    print('stats')
    t_test = t_test_all[:, pi]
    # tp, fp, fn, tn
    result = [[0] * 4 for _ in range(34)]
    # pos[(t, y)]
    pos = dict()
    pos[(0, 0)] = 3  # tn
    pos[(0, 1)] = 2  # fn
    pos[(1, 0)] = 1  # fp
    pos[(1, 1)] = 0  # tp
    for tt, yy in zip(t_test, model.predict(x_test)):
        result[pi][pos[tt, yy]] += 1

    e = 1e-10
    with open('stats.txt', 'a') as f:
        tp, fp, fn, tn = result[pi]
        pre = tp / (tp + fp + e)
        rec = tp / (tp + fn + e)
        f1 = 2 * rec * pre / (rec + pre + e)
        f.write('{} {} {} {} {} {} {} {}\n'.format(
            pi, tp, fp, fn, tn, pre, rec, f1
        ))
        print(pi, tp, fp, fn, tn, pre, rec, f1)
