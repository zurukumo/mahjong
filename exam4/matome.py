path = '/Users/shinji/mahjong/exam4'
in_file = path + '/sp-10/result2-sp-'
for i in range(34) :
  with open(in_file + str(i) + '.txt', 'r') as fp1 :
    last = fp1.readlines()[-1]
    with open(path + '/matome-sp-10.txt', 'a') as fp2 :
      fp2.write(str(i) + ',' + last)
