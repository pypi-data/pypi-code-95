import warnings
import pandas as pd
import statsmodels.formula.api as smf
from adptools.preprocessing import col_name_cleaning

warnings.filterwarnings("ignore")

class VariableSelector:
	"""
	x_vars_name : array - x variables column list (e.g. - ['age', 'name', 'gender'])
	y_var_name : string - y variable name (e.g. - 'score')
	df : original DataFrame of x, y
	"""
	def __init__(self, x_vars_name, y_var_name, df):
		if len(x_vars_name) >= 30:
			print("Alert! Too many x variables! (less than 30 variables are recommended)")
			print("It will may occur some errors!\n\n")

		self.df, self.org_col_list, self.new_col_list = col_name_cleaning(df)
		self.x_vars_name = self.__convert_to_col_name(x_vars_name, "from_old_to_new")
		self.y_var_name = y_var_name
	
	def __convert_to_col_name(self, col_name_list, cate="from_new_to_old"):
		ret_col_name_list = []
		if cate == "from_new_to_old":
			for col in col_name_list:
				if col in self.org_col_list:
					ret_col_name_list.append(self.org_col_list[col])
				else:
					ret_col_name_list.append(col)
		elif cate == "from_old_to_new":
			for col in col_name_list:
				if col in self.new_col_list:
					ret_col_name_list.append(self.new_col_list[col])
				else:
					ret_col_name_list.append(col)

		return ret_col_name_list

	def backward_elimination(self, alpha = 0.05, select_criteria = "AIC", return_case = "s"):
		"""
		alpha : float. p-value level for var. selection
		select_criteria : string. "AIC" or "rsquared_adj"
		return_case : original DataFrame of x, y
		"""
		retval = None
		selected_vars = self.x_vars_name.copy()
		eliminated_vars = []
		done = False
		
		while done is False:
			#step1 : 변수 하나씩을 제외한 n개의 모델을 만들어낸다. (n : 변수 갯수)
			model_result_list = []
			for var in selected_vars:
				var_list = self.x_vars_name.copy()
				if len(eliminated_vars)>0:
					for el_var in eliminated_vars:
						var_list.remove(el_var)
				var_list.remove(var)
				this_x_vars_name_str = "+".join(var_list)
				this_model_fit = smf.ols(self.y_var_name+" ~ "+this_x_vars_name_str, data=self.df).fit()

				this_result = {
					"selected var" : this_x_vars_name_str,
					"eliminated var" : var,			
					"AIC" : this_model_fit.aic,
					"rsquared_adj" : this_model_fit.rsquared_adj
				}
				model_result_list.append(this_result)
			result = pd.DataFrame(model_result_list)

			#step2 : n개 모델들 중 가장 좋은 결과를 보인 모델을 선택하고, 제외 후보 변수를 찾는다.
			ascending = True
			if select_criteria == "rsquared_adj":
				ascending = False
			result.sort_values(by=select_criteria, ascending=ascending, inplace=True)
			candidate_var = result.iloc[0, [1]].values[0]

			#step3 : 제외 후보 변수로 fitting하여 p-value를 알아보고 유의하다면 종료한다.
			candidate_model_fit = smf.ols(self.y_var_name+" ~ "+candidate_var, data=self.df).fit()
			if candidate_model_fit.pvalues[candidate_var] > alpha: #유의하지 않다면
				eliminated_vars.append(candidate_var) #제거확정
				selected_vars.remove(candidate_var)
				print("{} 변수를 제거합니다.".format(candidate_var))
			else: #유의하다면 종료한다
				done = True

		if return_case == "s":
			print("후보 독립변수들 : \n{}\n\n".format(self.x_vars_name))
			print("후진제거법에 의해 선택된 최종 변수들 : \n{}\n\n".format(selected_vars))
			retval = selected_vars
		elif return_case == "e":
			retval = eliminated_vars

		retval = self.__convert_to_col_name(retval, "from_new_to_old")

		return retval
		
	#전진 선택법 (단계적 선택법도 옵션에 포함)
	def forward_selection(self, alpha = 0.05, select_criteria = "AIC", stepwise=False):
		if stepwise:
			#후진제거법으로 제거되는 변수를 먼저 찾아 놓는다.
			eliminated_vars = self.backward_elimination(return_case = "e")
		candidate_vars = self.x_vars_name.copy()
		selected_vars = [] #전진선택법으로 선택된 변수들
		
		while len(candidate_vars) > 0: #후보 변수 리스트가 모두 소거될 때까지 반복한다.
			candidate_vars_reg_result = []
			for candidate in candidate_vars:
				#새로운 변수가 추가되었을 때 회귀모형의 AIC와 r-square값을 구해본다.
				this_x_vars_name_str = candidate
				if len(selected_vars) > 0:
					this_x_vars_name_str = " + ".join(selected_vars) + " + " + candidate
				this_model_fit = smf.ols(self.y_var_name+" ~ "+this_x_vars_name_str, data=self.df).fit()
				this_result = {
					"var" : candidate,
					"AIC" : this_model_fit.aic,
					"rsquared_adj" : this_model_fit.rsquared_adj,
					"p-value" : this_model_fit.pvalues[candidate]
				}
				candidate_vars_reg_result.append(this_result)
			result = pd.DataFrame(candidate_vars_reg_result)
			ascending = True
			if select_criteria == "rsquared_adj":
				ascending = False
			result.sort_values(by=select_criteria, ascending=ascending, inplace=True)
			selected_var = result.iloc[0,[0]].values[0]
			selected_var_pvalue = result.iloc[0,[3]].values[0]
			if selected_var_pvalue > alpha:
				break
			selected_vars.append(selected_var)
			candidate_vars.remove(selected_var)
			if stepwise:
				#selected_vars 중에 eliminated_var에 해당하는 것이 있다면 제거한다
				if len(selected_vars) > 2 and len(eliminated_vars) > 0:
					for ev in eliminated_vars:
						if ev in selected_vars:
							selected_vars.remove(ev)
		print("후보 독립변수들 : \n{}\n\n".format(self.x_vars_name))
		if stepwise:
			print("단계적 선택법 선택변수 : \n{}\n\n".format(selected_vars))
		else:
			print("전진선택법 선택변수 : \n{}\n\n".format(selected_vars))

		retval = self.__convert_to_col_name(selected_vars, "from_new_to_old")

		return retval

	def stepwise_selection(self, alpha = 0.05, select_criteria = "AIC"):
		retval = self.forward_selection(alpha, select_criteria, stepwise=True)

		return retval