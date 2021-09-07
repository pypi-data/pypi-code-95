# Import(s)
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

# Set base theme
sns.set()
sns.set_style("ticks")

# Use custom font
dirname = os.path.dirname(os.path.realpath(__file__))
font_files = mpl.font_manager.findSystemFonts(fontpaths=dirname + "/fonts/")
font_files = list(sorted(font_files))
for font_file in font_files:
    mpl.font_manager.fontManager.addfont(font_file)
    pass

# Customise theme
linewidth = 0.8
mpl.rcParams['figure.dpi'] = 120
mpl.rcParams['figure.figsize'] = [6.0, 4.0]
mpl.rcParams['savefig.dpi'] = 300

mpl.rcParams['axes.linewidth'] = linewidth
mpl.rcParams['axes.labelcolor'] = '.15'
mpl.rcParams['axes.edgecolor'] = '.15'
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['font.sans-serif'].insert(0, 'Inter')
mpl.rcParams['font.serif'].insert(0, 'Playfair Display')
mpl.rcParams['hist.bins'] = 50
mpl.rcParams['legend.frameon'] = False
mpl.rcParams['xtick.direction'] = 'out'
mpl.rcParams['ytick.direction'] = 'out'
mpl.rcParams['xtick.major.size'] = 3.
mpl.rcParams['ytick.major.size'] = 3.
mpl.rcParams['xtick.major.pad'] = 5.
mpl.rcParams['ytick.major.pad'] = 5.
mpl.rcParams['xtick.major.width'] = linewidth
mpl.rcParams['ytick.major.width'] = linewidth

# Colours
base = "#22203B"
colours = [base, "#2d4eeb", "#eb2d2d", "#2deb6c",
           "#cb2deb", "#ebcb2d", "#2debeb", "#eb2dcb"]
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=colours)

# Image
# images = {
#     'normal':   plt.imread(dirname + '/images/halfspace.png'),
#     'inverted': plt.imread(dirname + '/images/halfspace_inverted.png')
# }
pad = 10
# images = {key: im[85 - pad:165 + pad, 85 - pad:435 + pad, :]
#           for key, im in images.items()}
