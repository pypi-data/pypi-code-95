from tasks.scheduler import Scheduler
import random
len = 100
inputs =[]
def get_one_number():
    return random.randint(0, 500)
for _ in range(0, len):
    inputs.append((get_one_number(), get_one_number()))
for a,b in inputs:
    Scheduler(signature="add").queue(a, b)

for i in range(0, len):
    Scheduler(signature="some_20s_running_task").queue()