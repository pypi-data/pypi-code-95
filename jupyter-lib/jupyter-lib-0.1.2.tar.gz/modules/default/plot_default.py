import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
mpl.rcParams['figure.facecolor'] = "w"
plt.rcParams['axes.axisbelow'] = True  # grid behind plot

import plotly
import plotly.express as px
plotly.offline.init_notebook_mode()

import seaborn as sns
#sns.set(color_codes=False)

from statsmodels.graphics.gofplots import qqplot
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from scipy.stats import probplot

import time


# SEABORN COLORS        
blue = sns.color_palette("muted", desat=0.9)[0]
green = sns.color_palette("muted", desat=0.9)[2]
red = sns.color_palette("muted", desat=0.9)[3]
grey = sns.color_palette("muted", desat=0.9)[7]


