import math
import matplotlib.pyplot as plt

def boxplots(ind_vars, df, subplot_cols=5, figsize=(25, 60)):
	sp_cols = subplot_cols
	sp_rows = math.ceil(len(ind_vars)/sp_cols)
	sp_row_no = -1
	fig = plt.figure(figsize=figsize)
	ax = fig.subplots(nrows=sp_rows, ncols=sp_cols)
	for idx, col in enumerate(ind_vars):
	    if idx%sp_cols == 0:
	        sp_row_no += 1
	    ax[sp_row_no][idx%sp_cols].boxplot(df[col])
	    ax[sp_row_no][idx%sp_cols].set_title(col)

	plt.show()