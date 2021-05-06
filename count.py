
import csv

model = 'chi'

if model == 'dahai':
    file_name, n_output = model, 34
if model == 'richi':
    file_name, n_output = model, 2
if model == 'ankan':
    file_name, n_output = model, 2
if model == 'kakan':
    file_name, n_output = model, 2
if model == 'minkan':
    file_name, n_output = model, 2
if model == 'pon':
    file_name, n_output = model, 2
if model == 'chi':
    file_name, n_output = model, 4


t = [0] * n_output
with open(file_name + '.csv') as f:
    reader = csv.reader(f, delimiter=",")
    for row in reader:
        row = list(map(int, row))
        tt = row[0]
        t[tt] += 1

print(t)
