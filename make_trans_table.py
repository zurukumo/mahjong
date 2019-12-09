import csv
l = []

def pai_name(x) :
    ret = ''
    if x < 37 :
        ret += 'h'
    else :
        ret += 't'
        x -= 37

    if 0 <= x <= 8 :
        ret += str(x + 1) + 'm'
    elif 9 <= x <= 17 :
        ret += str(x - 8) + 'p'
    elif 18 <= x <= 26 :
        ret += str(x - 17) + 's'
    elif 27 <= x <= 33 :
        ret += '東南西北白発中'[x-27]
    elif 34 <= x <= 36 :
        ret += 'r5' + 'mps'[x-34]

    return ret

for i in range(74) :
    for j in range(74) :
        l.append(pai_name(i)+pai_name(j))

with open('table.csv', 'a') as f :
    writer = csv.writer(f)
    writer.writerow(l)
