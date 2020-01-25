K = 251128 
C = [11197, 16025, 18803, 23186, 24534, 22956, 18736, 16216, 11291, 11242, 16092, 18803, 23061, 24189, 23039, 18713, 15922, 10986, 11021, 16012, 18390, 22690, 24171, 22854, 18454, 15964, 11057, 3689, 3698, 3070, 3270, 4173, 4143, 4164]

for i in range(34) :
  C[i] /= K

fmax = [0] * 34
prob = [0] * 34
e = 1e-9

for i in range(0, 101, 10) :
  for j in range(0, 1) :
    tp = (i / 100) * C[j]
    fp = (i / 100) * (1 - C[j])
    fn = (1 - i / 100) * C[j]
    tn = (1 - i / 100) * (1 - C[j])
    precision = tp / (tp + fp + e)
    recall = tp / (tp + fn + e)
    f1score = 2 * recall * precision / (recall + precision + e)
    print('予測:{:02d}, 確率:{}%, 種:1, precision:{:0.5f}, recall:{:0.5f}, f1score:{:0.5f}'.format(j, i, precision, recall, f1score))

    tp, fp, fn, tn = tn, fn, fp, tp
    precision = tp / (tp + fp + e)
    recall = tp / (tp + fn + e)
    f1score = 2 * recall * precision / (recall + precision + e)
    print('予測:{:02d}, 確率:{}%, 種:0, precision:{:0.5f}, recall:{:0.5f}, f1score:{:0.5f}'.format(j, i, precision, recall, f1score))
    print()
    # if f1score > fmax[j] :
    #   fmax[j] = f1score
    #   prob[j] = i

# for i in range(34) :
#   print('{} {}%: {:0.5f}'.format(i, prob[i], fmax[i]))