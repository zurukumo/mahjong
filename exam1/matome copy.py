with open('matome.txt', 'r') as fp1 :
  content = fp1.readlines()
  for line in content :
    ret = []
    a = map(float, line.split(','))
    for b in a :
      ret.append('{:.3f}'.format(b))
    with open('matome2.txt', 'a') as fp2 :
      fp2.write(', '.join(ret) + "\n")