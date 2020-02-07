COMB = 2
LEN = 10
in_file = 'sample' + str(COMB) + '-sp-' + str(LEN) + '-inf.csv'
COUNT = 40000

import csv

cnt = [[COUNT] * 2 for _ in range(34)]
for i in range(27, 34) :
  cnt[i] = [10000, 10000]

file = open(in_file, 'r')
f = csv.reader(file, delimiter=",")
for row in f :
  row = [int(r) for r in row]
  t = row[:34]
  x = row[34:]

  for i in range(34) :
    with open('sample' + str(COMB) + '-sp-' + str(LEN) + '-' + str(i) + '.csv', 'a') as f :
      writer = csv.writer(f)
      if t[i] == 0 and cnt[i][0] > 0 :
        writer.writerow([0] + x)
        cnt[i][0] -= 1
      elif t[i] == 1 and cnt[i][1] > 0 :
        writer.writerow([1] + x)
        cnt[i][1] -= 1

  print(cnt)
  if sum(sum(cnt[i]) for i in range(34)) == 0 :
    break