from nexoclom import Input
from MESSENGERuvvs import MESSENGERdata


data = MESSENGERdata('Ca', 'Orbit = 36')
data = data[0:-1]
inputs = Input('inputfiles/Ca.isotropic.maxwellian.50000.input')

# los0 = inputs.line_of_sight(data.data, 'radiance', version='test',
#                            overwrite=True)

los0 = inputs.line_of_sight(data.data, 'radiance', version='new',
                            overwrite=True)
# los1 = inputs.line_of_sight(data.data, 'radiance', version='old',
#                             overwrite=True)
import pickle
los1 = pickle.load(open('los1.pkl', 'rb'))

import matplotlib.pyplot as plt
plt.plot(los0.radiance)
plt.plot(los1.radiance, linestyle='--')
plt.show()
assert 0

