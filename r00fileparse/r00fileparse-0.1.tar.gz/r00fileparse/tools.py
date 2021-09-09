import os
from typing import Union


def recur(path, include: Union[list, None]=None) -> list:
    """Поиск файлов во всех папках\n
    path: Путь до папки\n
    include: Искать файлы с определенным расширением ['.jpg', '.exe'...]
    return: list[ filepath, filepath.. ]\n
    """
    result = []
    def inner():
        for curdir, folders, files in os.walk(path):
            for file in files:
                filepath = os.path.join(curdir, file)
                if isinstance(include, list):
                    for extension in include:
                        if file.lower().endswith(extension):
                            result.append(filepath)
                            break
                else:
                    result.append(filepath)

            for folder in folders:
                if folder != '_backup':
                    dirpath = os.path.join(curdir, folder)
                    recur(dirpath)
        return result
    return inner()