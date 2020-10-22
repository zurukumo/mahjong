import csv
INFILE = 'sample.csv'
COUNT = 60000


cnt = [[0] * 2 for _ in range(34)]
for i in range(9):
    cnt[i] = [COUNT, COUNT]
# for i in range(27, 34):
#     cnt[i] = [10000, 10000]

file = open(INFILE, 'r')
f = csv.reader(file, delimiter=",")
for row in f:
    row = [int(r) for r in row]
    t = row[:34]
    x = row[34:]

    for pi in range(9):
        with open('sample' + '-' + str(pi) + '.csv', 'a') as f:
            writer = csv.writer(f)
            if cnt[pi][t[pi]] > 0:
                writer.writerow([t[pi]] + x)
                cnt[pi][t[pi]] -= 1

    print(cnt)
    if sum(sum(cnt[i]) for i in range(34)) == 0:
        break
