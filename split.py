IN_FILE = 'data2scp.csv'
OUT_FILE = 'data-{}.csv'
N_SPLIT = 1000000

count = 0
i = 0
with open(IN_FILE, mode='r') as fr:
    line = fr.readline()
    while line:
        with open(OUT_FILE.format(i), mode='a') as fw:
            fw.write(line)

        count += 1
        if count % N_SPLIT == 0:
            i += 1

        line = fr.readline()
