def jp(c):
    return ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m',
            '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
            '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
            '東', '南', '西', '北', '白', '発', '中', '-'][c]


def debug(x, y):
    print("実際に切った牌:", jp(y))
    for i in range(len(x) // 34):
        if i == 0:
            print('手牌')
        if i == 4:
            print('赤牌')
        if i == 7:
            print('河1')
        if i == 27:
            print('河2')
        if i == 47:
            print('河3')
        if i == 67:
            print('河4')

        print(x[i * 34:(i + 1) * 34])
