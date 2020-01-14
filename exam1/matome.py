for i in range(34) :
  with open('result0-' + str(i) + '.txt', 'r') as fp1 :
    last = fp1.readlines()[-1]
    with open('matome.txt', 'a') as fp2 :
      fp2.write(str(i) + ',' + last)
