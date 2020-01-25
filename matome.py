filename = 'result-?-?'

with open(filename + 'matome.txt', 'r') as mf :
  content = mf.readlines()
  for line in content :
    ret = []
    a = map(float, line.split(','))
    for b in a :
      ret.append('{:.3f}'.format(b))
    with open('matome2.txt', 'a') as fp2 :
      fp2.write(', '.join(ret) + "\n")