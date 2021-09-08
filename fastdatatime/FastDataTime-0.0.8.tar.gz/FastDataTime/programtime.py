import timeit

def get_program(com, get_stmt, get_number, re, get_print):
    if com == 'it':
        try:
            get_time = timeit.timeit(stmt=get_stmt, number=int(get_number))
            print(f"{get_time}")
        except:
            print("参数错误！")
            print("Parameter error!")
    if com == 'at':
        try:
            get_time2 = timeit.repeat(stmt=get_stmt, repeat=int(re), number=int(get_number))
            if str(get_print) == 'zero':
                print(get_time2[0])
            if str(get_print) == 'list':
                print(get_time2[0:])
            if str(get_print) == "N_one":
                print(get_time2[-1])
        except:
            print("参数错误！")
            print("Parameter error!")
    else:
        print("错误无效命令！")
        print("Error: invalid command!")
