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
    print('副露1:', jps(x[87 * 34:91 * 34]))
    print('副露2:', jps(x[91 * 34:95 * 34]))
    print('副露3:', jps(x[95 * 34:99 * 34]))
    print('副露4:', jps(x[99 * 34:103 * 34]))
    print("ドラ:", jps(x[103 * 34:107 * 34]))
    print('リーチ1:', sum(x[107 * 34:108 * 34]) == 34)
    print('リーチ2:', sum(x[108 * 34:109 * 34]) == 34)
    print('リーチ3:', sum(x[109 * 34:110 * 34]) == 34)
    print('リーチ4:', sum(x[110 * 34:111 * 34]) == 34)
    print('東1:', sum(x[111 * 34:112 * 34]) == 34)
    print('東2:', sum(x[112 * 34:113 * 34]) == 34)
    print('東3:', sum(x[113 * 34:114 * 34]) == 34)
    print('東4:', sum(x[114 * 34:115 * 34]) == 34)
    print('南1:', sum(x[115 * 34:116 * 34]) == 34)
    print('南2:', sum(x[116 * 34:117 * 34]) == 34)
    print('南3:', sum(x[117 * 34:118 * 34]) == 34)
    print('南4:', sum(x[118 * 34:119 * 34]) == 34)
    print('西1:', sum(x[119 * 34:120 * 34]) == 34)
    print('西2:', sum(x[120 * 34:121 * 34]) == 34)
    print('西3:', sum(x[121 * 34:122 * 34]) == 34)
    print('西4:', sum(x[122 * 34:123 * 34]) == 34)
