def debug(x):
    for i in range(len(x) // 34):
        if i == 0:
            print('手牌')
        if i == 4:
            print('赤牌')

        print(x[i * 34:(i + 1) * 34])
