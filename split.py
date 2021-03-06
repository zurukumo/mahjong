IN_FILE = 'richi.csv'
OUT_FILE = 'richi-{}.csv'

N_SPLIT = 800000


count = 0
i = 0
with open(IN_FILE, mode='r') as fr:
    line = fr.readline()
    while line:
        with open(OUT_FILE.format(i), mode='a') as fw:
            fw.write(line)

        count += 1
        print(count)
        if count % N_SPLIT == 0:
            break
            i += 1

        line = fr.readline()
