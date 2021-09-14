import math
import matplotlib.pyplot as plt

def boxplots(ind_vars, df, subplot_cols=4, subplot_width=25):
	"""
	draw boxplot with auto subplot
	ind_vars : array - variable names
	df : DataFrame
	subplot_cols : int - column size of subplot
	subplot_width : int - width of subplot
	"""
	sp_cols = subplot_cols
	sp_rows = math.ceil(len(ind_vars)/sp_cols)
	sp_row_no = -1
	subplot_height = int((subplot_width * sp_rows) / 2.5)
	fig = plt.figure(figsize=(subplot_width, subplot_height))
	ax = fig.subplots(nrows=sp_rows, ncols=sp_cols)
	for idx, col in enumerate(ind_vars):
		if idx%sp_cols == 0:
			sp_row_no += 1
		if sp_rows > 1:
			this_ax = ax[sp_row_no][idx%sp_cols]
		else:
			this_ax = ax[idx%sp_cols]
		this_ax.boxplot(df[col])
		this_ax.set_title(col, fontsize=22)
	plt.show()