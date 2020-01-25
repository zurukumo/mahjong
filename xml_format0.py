# 0列用

COUNT = 30000

import os, re, csv
from shanten import get_yuko

out = [0] * 34
K = 0

def xml_parse(filename) :
  with open(filename, 'r') as xml :
    for elem, attr in re.findall(r'<(.*?)[ /](.*?)/?>', xml.read()) :
      attr = dict(re.findall(r'\s?(.*?)="(.*?)"', attr))

      if elem == 'AGARI' :
        global K
        K += 1
        tehai = [0 for _ in range(34)]
        machi = int(attr['machi'])
        for i in map(int, attr['hai'].split(',')) :
          if i != machi :
            tehai[i // 4] += 1

        for i in get_yuko(tehai, [4] * 34, 0) :
          out[i] += 1

def xml_format(year, output_file_name='output.json') :
    file_dir = './xml' + str(year)
    count = 0
    for filename in os.listdir(file_dir) :
        count += 1
        print(count, filename)
        xml_parse(file_dir + '/' + filename)
        if count == COUNT :
            break

xml_format(2017)

print(K, out)