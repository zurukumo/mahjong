import os, re, csv
from shanten import get_yuko

def pai_transform(x) :
    if x == 16 : return 34
    elif x == 52 : return 35
    elif x == 88 : return 36
    else : return x // 4

def bit_sum(m) :
    return sum([m[i] * (2 ** i) for i in range(len(m))])

def huro_transform(m) :
    CHI = 2 * 3 * 21
    PON = 2 * 34
    b = []
    for i in range(0, 16) :
        b.append(m % 2)
        m = m // 2
	
    who = b[0] + b[1] * 2
	
    if who == 0 :		
		#暗槓
        return CHI + PON + bit_sum(b[8:16]) // 3
		
    else :
        #順子
        if b[2] == 1 :
            ret = 0
            tmp = bit_sum(b[10:16])
            ret += tmp
            tmp = (tmp // 3) % 7
            # 赤あり
            if tmp == 2 and bit_sum(b[7:9]) == 0 :
                ret += 63
            elif tmp == 3 and bit_sum(b[5:7]) == 0 :
                ret += 63
            elif tmp == 4 and bit_sum(b[3:5]) == 0 :
                ret += 63

            return ret
			
        #明刻
        elif b[3] == 1 :
            ret = CHI
            tmp = bit_sum(b[9:16]) // 3
            ret += tmp
            # 赤あり
            if tmp in [4, 13, 22] and bit_sum(b[5:7]) != 0 :
                ret += 34
            return ret
		
        #加槓
        elif b[4] == 1 :
            return CHI + PON + 34 + bit_sum(b[9:16]) // 3
			
        #明槓
        else :
            return CHI + PON + 68 + bit_sum(b[8:16]) // 4

def xml_parse(filename) :
    with open(filename, 'r') as xml :
        for elem, attr in re.findall(r'<(.*?)[ /](.*?)/?>', xml.read()) :
            attr = dict(re.findall(r'\s?(.*?)="(.*?)"', attr))
            if elem == 'INIT' :
                tsumo = [[] for _ in range(4)]
                dahai = [[] for _ in range(4)]
                huro = [[] for _ in range(4)]
                kyoku, honba, kyotaku, _, _, dora = map(int, attr['seed'].split(','))
                oya = attr['oya']
                # print()
                # print('INIT')
            
            # ツモ情報
            elif re.match(r'[T|U|V|W][0-9]+', elem) :
                idx = {'T': 0, 'U': 1, 'V': 2, 'W': 3}
                who = idx[elem[0]]
                pai = int(elem[1:])
                tsumo[who].append(pai_transform(pai))

            # 打牌情報
            elif re.match(r'[D|E|F|G][0-9]+', elem) :
                idx = {'D': 0, 'E': 1, 'F': 2, 'G': 3}
                who = idx[elem[0]]
                pai = int(elem[1:])
                if len(tsumo[who]) == 0 or tsumo[who][-1] != pai :
                    dahai[who].append(pai_transform(pai))
                else :
                    dahai[who].append(pai_transform(pai) + 37)

            elif elem == 'AGARI' :
                who = int(attr['who'])
                tehai = [0 for _ in range(34)]
                machi = int(attr['machi'])
                for i in map(int, attr['hai'].split(',')) :
                    if i != machi :
                        tehai[i // 4] += 1
                
                in1 = [0] * (74 * 74) # 打牌順序
                in2 = [0] * (2 * 3 * 21 + 2 * 34 + 3 * 34) # 副露
                out1 = [0] * 34 # 当たり牌

                for i in range(len(dahai[who])) :
                    for j in range(i + 1, len(dahai[who])) :
                        in1[dahai[who][i] * 37 + dahai[who][j]] = 1
                
                if 'm' in attr :
                    for i in map(int, attr['m'].split(',')) :
                        in2[huro_transform(i)] = 1

                for i in get_yuko(tehai, [4] * 34, 0) :
                    out1[i] = 1

                with open('sample.csv', 'a') as f :
                    writer = csv.writer(f)
                    writer.writerow(in1 + in2 + out1)
                # DEBUG用
                # print('手牌', tehai)
                # print('上がり牌', [pai_name(i) for i in all_machi])
                # print('打牌', dahai[who])

            elif elem == 'RYUUKYOKU' :
                # print('RYUKYOKU')
                continue

def xml_format(year, output_file_name='output.json') :
    file_dir = './xml' + str(year)
    count = 0
    for filename in os.listdir(file_dir) :
        print(filename)
        xml_parse(file_dir + '/' + filename)
        count += 1
        if count == 10000 :
            break

xml_format(2017)