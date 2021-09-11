def print_lol(the_list):			# 自己定义函数print_lol
	'''这个函数去一个位置参数，名为"the_list",这可以是任何python列表
	（也可以是包含嵌套列表的列表）。所指定的列表中的每一个数据项会
	（递归的）输出到屏幕上，各数据各占一行'''

	for i in the_list:				# 遍历参数
		if isinstance(i,list):		# if 判断元素是否为列表
			print_lol(i)			# 如果参数中的元素有列表，再次调用print_lol函数
		else:
			print(i)				# else 打印输出非列表的元素
