K = 251128 
C = [11197, 16025, 18803, 23186, 24534, 22956, 18736, 16216, 11291, 11242, 16092, 18803, 23061, 24189, 23039, 18713, 15922, 10986, 11021, 16012, 18390, 22690, 24171, 22854, 18454, 15964, 11057, 3689, 3698, 3070, 3270, 4173, 4143, 4164]

for i in range(34) :
  C[i] /= K

fmax = [0] * 34
prob = [0] * 34
e = 1e-9

for i in range(100, 101) :
  for j in range(34) :
    tp = (i / 100) * C[j]
    fp = (i / 100) * (1 - C[j])
    fn = (1 - i / 100) * C[j]
    tn = (1 - i / 100) * (1 - C[j])
    precision = tp / (tp + fp + e)
    recall = tp / (tp + fn + e)
    f1score = 2 * recall * precision / (recall + precision + e)

    print('{} {} {} {} {}'.format(j, C[j], precision, recall, f1score))