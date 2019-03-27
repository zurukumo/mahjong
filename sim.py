import exp
from agari import *
import shanten
import random

PAI = ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m', '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p', '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', '東', '南', '西', '北', '白', '発', '中']

# 配牌ランダム
while True :
	jun = [0 for i in range(34)]
	rest = [4 for i in range(34)]
	
	yama = [i // 4 for i in range(4 * 34)]
	random.shuffle(yama)

	for i in range(13) :
		jun[yama[i]] += 1
		rest[yama[i]] -= 1
		
	if shanten.calc_shanten(jun) <= 2 :
	
		break

# 配牌指定	
# haipai = [1, 1, 1, 4, 5, 6, 11, 12, 13, 20, 20, 23, 23, 24]
# yama = []

# for i in haipai :
	# rest[i] -= 1
	
# for i in range(34) :
	# for j in range(rest[i]) :
		# yama.append(i)

# random.shuffle(yama)
# yama = haipai + yama

# for i in range(13) :
	# jun[yama[i]] += 1
	
print('配牌', ''.join([PAI[i] * jun[i] for i in range(34)]))

for i in range(18) :
	tsumo = yama[13 + i]
	jun[tsumo] += 1
	rest[tsumo] -= 1
	print(i + 1, '順目', shanten.calc_shanten(jun), '向聴')
	print('摸', PAI[tsumo], ''.join([PAI[i] * jun[i] for i in range(34)]))
	
	if shanten.calc_shanten(jun) == -1 :
		print(Agari(jun, [], [0, 0, 0, 0, 0], [1 if i <= 1 else 0 for i in range(55)]).get_ten(tsumo)[0])
		break
	
	max_k = []
	max_v = 0
	
	E = exp.Exp(jun, rest, i + 1)
	
	for i in range(34) :
		if E.exp[i] > -10000  and E.exp[i] != 0 :
			print(PAI[i], E.exp[i])
	
	for k in range(34) :
		v = E.exp[k]
		if v >= max_v :
			max_k = [k]
			max_v = v
		elif max_v == v :
			max_k.append(k)
			
	random.shuffle(max_k)
	print([PAI[i] for i in max_k])
	dahai = max_k[0]
	jun[dahai] -= 1
	print('打', PAI[dahai], ''.join([PAI[i] * jun[i] for i in range(34)]))
	print()