# Fibonacci numbers module

def fib(number:int):
	""" Prints the Fibonacci sequence up to limit of number """
	a, b = 0, 1
	while a < number:
		print(a, end=' ')
		a, b = b, a+b
	print()
	

def fib2(number:int) -> list:
	""" returns the Fibonacci sequence up to limit of number in a list """
	result = []
	a,b = 0, 1
	while a < number:
		result.append(a)
		a, b = b, a+b
	return result


def myname():
	"""Prints the name of the function """
	print(" Buffalo Bills")



	
