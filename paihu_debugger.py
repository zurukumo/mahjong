def jp(c):
    return ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m',
            '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
            '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
            '東', '南', '西', '北', '白', '発', '中', '-'][c]


def jps(x):
    tmp = []
    for k, v in enumerate(x):
        if v == 1:
            tmp.append(k % 34)

    return ''.join([jp(pai) for pai in sorted(tmp)])


def debug(x, y):
    print("実際に切った牌:", jp(y))

    print("手牌:", jps(x[0 * 34:4 * 34]))
    print('赤5m:', sum(x[4 * 34:5 * 34]) == 34)
    print('赤5p:', sum(x[5 * 34:6 * 34]) == 34)
    print('赤5s:', sum(x[6 * 34:7 * 34]) == 34)
    print('河1:', '>'.join([jps(x[i * 34:(i + 1) * 34])for i in range(7, 27)]))
    print('河2:', '>'.join([jps(x[i * 34:(i + 1) * 34])for i in range(27, 47)]))
    print('河3:', '>'.join([jps(x[i * 34:(i + 1) * 34])for i in range(47, 67)]))
    print('河4:', '>'.join([jps(x[i * 34:(i + 1) * 34])for i in range(67, 87)]))
