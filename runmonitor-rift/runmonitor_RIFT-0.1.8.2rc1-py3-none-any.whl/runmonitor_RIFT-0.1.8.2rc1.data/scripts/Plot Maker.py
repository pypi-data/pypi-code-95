
from matplotlib import pyplot as plt

file = "posterior_samples-5.dat"
bins_list = list(range(30,45))
parameter = "m1"

param_to_column = {"m1": 0, "m2": 1, "a1x": 2, "a1y": 3, "a1z": 4, "a2x": 5, "a2y": 6, "a2z": 7, "mc": 8, "eta": 9,
                       "indx": 10, "Npts": 11, "ra": 12, "dec": 13, "tref": 14, "phiorb": 15, "incl": 16, "psi": 17,
                       "dist": 18, "p": 19, "ps": 20, "lnL": 21, "mtotal": 22, "q": 23}

#read data

handler = open(file)
handler.readline()
lines = handler.readlines()
handler.close()

#plot posterior

param_values = []

for line in lines:
    param_values.append(float(line.split()[param_to_column[parameter]]))


plt.hist(param_values, bins=bins_list)
plt.title("Posterior")
plt.xlabel(parameter)
plt.show()

#compute cdf:

param_values_sorted = sorted(param_values)
len_of_params = len(param_values)

cdf_x = []
cdf_y = []


for (index,value) in enumerate(param_values_sorted):
    cdf_x.append(value)
    cdf_y.append(index/len_of_params)

plt.scatter(cdf_x,cdf_y)
plt.title("CDF")
plt.xlabel(parameter)
plt.show()


