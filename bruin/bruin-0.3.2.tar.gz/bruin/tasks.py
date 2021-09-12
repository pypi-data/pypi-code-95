import json
from pathlib import Path
from datetime import datetime
from termcolor import colored, cprint
from typing import Optional

_CURDIRT = Path(__file__).parent
_TASK_FILE = _CURDIRT / 'tasks.json'

"""
Structure of the json file:
{
    'todo':[
        {
            'name': str,
            'subject': str,
            'deadline': str
        },
        ...
    ],
    'review': [
        ...
    ],
    'daily': [
        {
            'name': str,
            'complete_date': str
        }
    ]
}
"""

def _print_list(task_list : list):
    """
    Print a list of task in column
    Parameters:
        task_list: a list of task objects
    """
    for i in range(len(task_list)):
        item = task_list[i]
        name = item['name']
        subject = item['subject']
        deadline = item['deadline']
        log_string = f'{i+1}. {name}({subject}) - {deadline}'
        date_obj = datetime.strptime(deadline, '%Y-%m-%d').date()
        if date_obj == datetime.today().date():
            print(colored(log_string, 'red', attrs=['bold']))
        else:
            print(log_string)

    print("")

def _print_daily_task_list(task_list: list):
    """
    Print a list of daily tasks
    Parameters:
        task_list: a list of task objects
    """
    def remove_completed(obj):
        today = datetime.now().date()
        if obj['complete_date'] != '':
            complete_date = datetime.strptime(obj['complete_date'], '%Y-%m-%d').date()
            if complete_date == today:
                return False
        return True
    
    filtered = filter(remove_completed, task_list)
    filtered_list = list(filtered)
    for i in range(len(filtered_list)):
        item = filtered_list[i]
        name = item['name']
        print(f'{i+1}. {name}')
    
    print("")


def read_tasks_and_print():
    """
    Read and print all tasks from the local
    json file created.
    """
    if not _TASK_FILE.is_file():
        print("No existing tasks! Try to add some.")
        return
    
    with open(_TASK_FILE) as f:
        task_dict = json.load(f)
        todo_list = task_dict['todo']
        review_list = task_dict['review']

        if 'daily' not in task_dict:
            task_dict['daily'] = []
        daily_list = task_dict['daily']

        cprint("Daily Tasks:", 'grey', 'on_yellow', end='\n')
        _print_daily_task_list(daily_list)

        cprint("Todos:", 'grey', 'on_green', end='\n')
        _print_list(todo_list)
        
        cprint("Reviews:", 'white', 'on_blue', end='\n')
        _print_list(review_list)

def _add_task(
    name: str,
    deadline: Optional[str] = None,
    subject: str = 'Misc',
    is_daily: bool = False,
):
    """
    Add a new task to the json file
    Parameter:
        name: title of the task
        deadline: deadline of the task
        subject: which course this assignment belongs to
    """
    data = {
        "todo": [],
        "review": [],
        "daily": []
    }
    if _TASK_FILE.is_file():
        with open(_TASK_FILE) as json_file:
            data = json.load(json_file)
    
    task = {}
    
    task['name'] = name

    if is_daily:
        task['complete_date'] = ''
        if 'daily' not in data:
            data['daily'] = []

        data['daily'].append(task)
    else:
        task['subject'] = subject
        task['deadline'] = deadline
        data['todo'].append(task)

    with open(_TASK_FILE, 'w') as json_file:
        json.dump(data, json_file)

def add_task_from_input():
    """
    Use console input prompts to get user data
    for adding a new task
    """
    daily = input("Is it a daily task? (Y/n)")
    name = input("Title of the task: ")

    if daily.lower() == 'y':
        _add_task(name, is_daily=True)
    else:
        subject = input("Which course? (default: Misc): ")
        if subject == "" or subject is None:
            subject = "Misc"
        
        valid_date = False

        while not valid_date:
            deadline = input("When should you finish it: ")
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
                valid_date = True
            except ValueError:
                print("Invalid deadline format: please use YYYY-MM-DD format!")

        _add_task(name, deadline, subject)

    print("Task added!")

def complete_task(index: int):
    """
    Complete a task and move it from Todo list
    to Review list

    Parameters:
        index: the index of the task in the todo list
    """
    if not _TASK_FILE.is_file():
        print("You don't have a task yet.")
    else:
        data = {}
        with open(_TASK_FILE) as json_file:
            data = json.load(json_file)
        todo_list : list = data['todo']
        if len(todo_list) >= index:
            data['review'].append(todo_list.pop(index-1))
            with open(_TASK_FILE, 'w') as json_file:
                json.dump(data, json_file)
            print("Task completed and wait for review later.")
        else:
            print("You typed a wrong task index")

def _terminate_task(type: str, index: int):
    """
    Terminate a task.

    Parameters:
        type: the bucket of the task
        index: which task inside the bucket
    """
    if not _TASK_FILE.is_file():
        print("You don't have a task yet.")
    else:
        data = {}
        with open(_TASK_FILE) as json_file:
            data = json.load(json_file)

        if type in data:
            task_list = data[type]
            if type == 'daily':
                today = datetime.now().date()
                date_string = datetime.strftime(today, '%Y-%m-%d')
                if len(task_list) >= index:
                    task_list[index-1]['complete_date'] = date_string
                    with open(_TASK_FILE, 'w') as json_file:
                        json.dump(data, json_file)
                    print("Complete a daily task!")
                else:
                    print("You typed a wrong task index")
                return

            if len(task_list) >= index:
                task_list.pop(index-1)
                with open(_TASK_FILE, 'w') as json_file:
                    json.dump(data, json_file)
                print("Task closed.")
            else:
                print("You typed a wrong task index")
        else:
            print("You can only close task from either TODO, REVIEW, or DAILY bucket.")

def _validate_index_string(index_string: str) -> bool:
    """
    Handle validation of index string from the argument. 
    a string should be in format 't{%d}' or 'r{%d}' or 'd{%d}'
    
    Parameters:
        index_string: the string we want to validate
    Returns:
        a boolean indicating whether the index string is valid
    """
    if len(index_string) < 2:
        print("Invalid index string length!")
        return False
    elif index_string[0] != 't' and index_string[0] != 'r' and index_string[0] != 'd':
        print("Invalid index string prefix!")
        return False
    elif not index_string[1:].isnumeric():
        print("Index need to have a number suffix!")
        return False
    else:
        return True

def terminate_task_by_string(index_string: str):
    """
    Terminate a task with a index string
    """
    if _validate_index_string(index_string):
        if index_string[0] == 't':
            list_type = 'todo'
        elif index_string[0] == 'r':
            list_type = 'review'
        else:
            list_type = 'daily'

        index = int(index_string[1:])
        _terminate_task(list_type, index)

def remove_daily_task(index: int):
    """
    Stop reiterating a daily task
    """
    if not _TASK_FILE.is_file():
        print("You don't have a task yet.")
    else:
        data = {}
        with open(_TASK_FILE) as json_file:
            data = json.load(json_file)
        
        if ('daily' not in data) or len(data['daily']) == 0:
            print("You don't have a daily task yet!")
            return
        
        daily_list = data['daily']
        if len(daily_list) >= index:
            daily_list.pop(index-1)
            with open(_TASK_FILE, 'w') as json_file:
                json.dump(data, json_file)
            print("Daily task removed.")
        else:
            print("You typed a wrong task index")