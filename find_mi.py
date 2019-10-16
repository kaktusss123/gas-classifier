import re

with open('classifiers.log', encoding='cp1251') as f:
    data = f.read()

error = list(map(lambda x: float(x), re.findall(r'\d+.\d+(?=%)', data)))
min = 100
min_i = 0
for i, e in enumerate(error):
    if e < min:
        min = e
        min_i = i
print(min, min_i)