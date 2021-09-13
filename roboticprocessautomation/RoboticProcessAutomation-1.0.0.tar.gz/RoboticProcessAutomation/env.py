import os

def clear_folder(path: str) -> bool:
    '''
    This function is to delete all files in provided folder.

    Args:
        path: (str) - oath to the folder to be cleared

    Returns:
        (bool) True if done, False if path not exists
    '''
    if os.path.isfile(path):
        for filename in os.listdir(path):
            os.remove(path + filename)
        return True
    else:
        return False


def kill_processes(processes: 'list[str]'):
    '''
    This function is to kill provided processes.

    Args: 
        processes: (list) - e.g. [process_1_name, (...), process_n_name]
    '''
    for p in processes:
         os.system(f"taskkill /f /im {p}")