in_file = 'sample2-sp-0-inf.csv'
COUNT = 40000

import pandas as pd
import csv

cnt = [[COUNT] * 2 for _ in range(27)]

file = open(in_file, 'r')
f = csv.reader(file, delimiter=",")
for row in f :
  row = [int(r) for r in row]
  t = row[:34]
  x = row[34:]

  for i in range(27) :
    with open('sample2-sp-0-' + str(i) + '.csv', 'a') as f :
      writer = csv.writer(f)
      if t[i] == 0 and cnt[i][0] > 0 :
        writer.writerow([0] + x)
        cnt[i][0] -= 1
      elif t[i] == 1 and cnt[i][1] > 0 :
        writer.writerow([1] + x)
        cnt[i][1] -= 1

  print(cnt)
  if sum(sum(cnt[i]) for i in range(27)) == 0 :
    break