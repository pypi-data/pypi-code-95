import time

def add(a,b):
    return a+b

def some_20s_running_task():
    for i in range(0,10):
        print(f"Returning sum as {i}th iteration")
        time.sleep(2)