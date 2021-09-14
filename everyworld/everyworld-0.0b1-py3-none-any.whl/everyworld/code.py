def min_of(massive):
	minimal = 1000000000000000000000000000
	try:
		for i in massive:
			if i < 0:
				minimal = i
		return minimal
	except:
		print("[Everyworld.code] Error!")
		return None
def max_of(massive):
	maximal = 0
	try:
		for i in massive:
			if i > 0:
				maximal = i
		return maximal
	except:
		print("[Everyworld.code] Error!")
		return None