import csv
ret = [0] * 2
with open('richi.csv') as f:
    reader = csv.reader(f, delimiter=",")
    for row in reader:
        row = list(map(int, row))
        t = row[0]
        ret[t] += 1

print(ret)
