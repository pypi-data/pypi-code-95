import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np


from IPython.display import Image 
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


# PLOTTING
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.dates as dates
plt.rcParams['axes.axisbelow'] = True  # grid behind plot
mpl.rcParams['figure.facecolor'] = "w"

import seaborn as sns
#sns.set(color_codes=False)

import plotly
import plotly.express as px
plotly.offline.init_notebook_mode()


