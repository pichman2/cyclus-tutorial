import numpy as np
import pandas as pd
d = pd.read_csv('cycle_used_fuel.csv',header=None)
df =  pd.DataFrame(d)
names = df[1]
times = df[2]
re1 = {}

for i in range(len(names)):
    j = names[i]
    re1[j] = times[i]
    