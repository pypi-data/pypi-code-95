#coding:utf-8
import datetime
import time
import schedule

def print_time():
        im = datetime.datetime.now()
        print("%s" % im)

def run_time(number_run=''):
    if number_run == '':
        eval_number_run = 0
    else:
        eval_number_run = eval(number_run)
    try:
        numbers = eval_number_run
        def run_sch():
            schedule.every(numbers).seconds.do(print_time)
            while True:
                schedule.run_pending()
        run_sch()
    except:
        print("错误！请检查代码！或检查输入值是否为数字或浮点数 ！")
        print("Wrong! Please check the code! Or check whether the input value is a number or floating point number !")

#run_time('timeing_time', '')
#run_tim('f', '5', 'fert')
#run_time()
