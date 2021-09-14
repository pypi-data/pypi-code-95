import re
import pandas as pd

#컬럼명이 숫자로 시작하면 ols에러 발생. 숫자로 시작하는 컬럼명 앞에 언더바를 붙여줌
def col_name_cleaning(df):
	org_col_list = []
	"""
	modify column name for OLS.
	df : DataFrame
	return : 3 outputs
		-> df with cleaned column names
		-> org -> new column name mapper (dict)
		-> new -> org column name mapper (dict)
	"""
	org_col_mapper = {}
	new_col_mapper = {}
	for col in df.columns:
		new_col = re.sub(r"[^a-zA-Z0-9]", "", col)
		if col[0:1] in [str(x) for x in range(0,10)]:
			new_col_name = "_"+new_col
		else:
			new_col_name = new_col

		org_col_mapper[new_col_name] = col
		new_col_mapper[col] = new_col_name

	cleaned_df = df.rename(columns=new_col_mapper)

	return cleaned_df, org_col_mapper, new_col_mapper

def get_outlier_df(df, target_vars=None, method="quantile"):
	"""
	check outliers and return outlier info.
	df : DataFrame
	target_vars : array - target variable(s)
	method : quantile method
	return : df with outlier info
	   - _outlier      : 1 or 0
	   - _outlier_from : array - outlier column(s)
	   - _over         : 1 or 0
	   - _under        : 1 or 0
	"""
	df_result = df.copy()
	df_result["_outlier"] = 0
	df_result["_outlier_from"] = ""
	df_result["_over"] = 0
	df_result["_under"] = 0
	
	cols = df.columns
	if target_vars:
		cols = target_vars
	for col in cols:
		q1 = df[col].quantile(.25)
		q3 = df[col].quantile(.75)
		iqr = q3-q1
		iqr_under = q1 - (iqr*1.5)
		iqr_over = q3 + (iqr*1.5)
		df_result.loc[(df[col] < iqr_under), "_outlier"] = 1
		df_result.loc[(df[col] < iqr_under), "_under"] = 1
		df_result.loc[(df[col] < iqr_under), "_outlier_from"] = df_result.loc[(df[col] < iqr_under), "_outlier_from"].values + col + "(under), "

		df_result.loc[(df[col] > iqr_over), "_outlier"] = 1
		df_result.loc[(df[col] > iqr_over), "_over"] = 1
		df_result.loc[(df[col] > iqr_over), "_outlier_from"] = df_result.loc[(df[col] > iqr_over), "_outlier_from"].values + col + "(over), "
	df_result.drop(index=df_result[(df_result["_outlier"] == 0)].index, inplace=True)
	return df_result

def handle_outlier(df, target_vars=None, method="quantile", handle="remove"):
	"""
	remove or substitute outliers.
	df : DataFrame
	target_vars : array - target variable(s)
	method : quantile method
	handle : "remove" or "substitute" - remove or subtitute by mean value
	return : df_result, deleted_index(array, in case of "remove")

	"""
	df_result = df.copy()
	df_result["_outlier"] = 0
	df_result["_outlier_from"] = ""
	df_result["_outlier_cate"] = ""
	deleted_index = None
	
	cols = df.columns
	if target_vars:
		cols = target_vars
	for col in cols:
		q1 = df[col].quantile(.25)
		q3 = df[col].quantile(.75)
		iqr = q3-q1
		iqr_under = q1 - (iqr*1.5)
		iqr_over = q3 + (iqr*1.5)
		if handle=="remove":
			df_result.loc[(df[col] < iqr_under), "_outlier"] = 1
			df_result.loc[(df[col] < iqr_under), "_outlier_from"] = col
			df_result.loc[(df[col] < iqr_under), "_outlier_cate"] = "under"
			df_result.loc[(df[col] > iqr_over), "_outlier"] = 1
			df_result.loc[(df[col] > iqr_over), "_outlier_from"] = col
			df_result.loc[(df[col] > iqr_over), "_outlier_cate"] = "over"
		elif handle=="substitute":
			df_result.loc[(df[col] < iqr_under) or (df[col] > iqr_over), col] = df[col].mean()
	if handle=="remove":
		deleted_index = df_result[(df_result["_outlier"] == 1)].index.to_list()
		df_result.drop(index=df_result[(df_result["_outlier"] == 1)].index, inplace=True)
	
	df_result.drop(columns=["_outlier", "_outlier_from", "_outlier_cate"], inplace=True)
	return df_result, deleted_index