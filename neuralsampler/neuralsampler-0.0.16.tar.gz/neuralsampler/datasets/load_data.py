import numpy as np 
import matplotlib.pyplot as plt 

a = np.loadtxt("data.txt")

X_new = a[-int(1e5):]

# Generate some test data
_x = X_new[:, 0]
_y = X_new[:, 1]

heatmap, xedges, yedges = np.histogram2d(_x, _y, bins=100)
extent = [-2.0, 1.0, -0.5, 2.5]

plt.imshow(heatmap.T, extent=extent, origin='lower')
plt.show()

plt.scatter(a[:, 0], a[:, 1])
plt.show()

