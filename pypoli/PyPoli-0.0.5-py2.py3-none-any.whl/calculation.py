#coding:gbk

def addition():
    try:
        number = eval(input("输入数字1："))
        numbers = eval(input("输入数字2："))
        additions = number + numbers
        print(additions)
    except:
        print("请输入数字")
def multiplication():
    number = eval(input("输入数字1："))
    numbers = eval(input("输入数字2："))
    multiplications = number * numbers
    print(multiplications)
def division():
    number_c = eval(input("输入数字1："))
    numbers_c = eval(input("输入数字2："))
    divisions = number_c/numbers_c
    divisionr = number_c//numbers_c
    print(divisions)
    print(divisionr)