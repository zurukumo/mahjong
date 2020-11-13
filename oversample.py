import csv
INFILE = 'sample.csv'
COUNT = 500


cnt = [[COUNT] * 2 for _ in range(34)]

file = open(INFILE, 'r')
f = csv.reader(file, delimiter=",")
for row in f:
    row = [int(r) for r in row]
    t = row[:34]
    x = row[34:]

    for pi in range(34):
        with open('sample-mini-' + str(pi) + '.csv', 'a') as f:
            writer = csv.writer(f)
            if cnt[pi][t[pi]] > 0:
                writer.writerow([t[pi]] + x)
                cnt[pi][t[pi]] -= 1

    print([c[1] for c in cnt])
    if sum(sum(cnt[i]) for i in range(34)) == 0:
        break
