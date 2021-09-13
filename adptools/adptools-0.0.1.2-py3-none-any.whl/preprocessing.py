import re
import pandas as pd

#컬럼명이 숫자로 시작하면 ols에러 발생. 숫자로 시작하는 컬럼명 앞에 언더바를 붙여줌
def col_name_cleaning(df):
	org_col_list = []
	"""
	cleaning column name for OLS
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