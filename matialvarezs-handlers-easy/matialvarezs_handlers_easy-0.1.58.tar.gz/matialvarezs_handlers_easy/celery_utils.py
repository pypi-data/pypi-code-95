from celery.result import AsyncResult
import time,json
from django_celery_results.models import TaskResult
def get_result_task_1(result):
    value = None
    for item in result.collect():
        #print("item", item, item[1])
        value = item[1]
    return value


def get_result_task_2(result):
    for item in result.collect():
        pass
    return result.result


def get_result_task_3(result):
    return result.get(timeout=None)


def get_result_task_4(result):
    return AsyncResult(result).ready()

def get_task_result_while_wait_ready(result):
    while not result.ready():
     time.sleep(1)
    result_obj = TaskResult.objects.get(task_id=result.task_id)
    print("RESULTADO DESDE LA TABLA",result_obj,result_obj.result)
    data = TaskResult.objects.get(task_id=result).result
    if data:
        return json.loads(data)
    else:
        return None