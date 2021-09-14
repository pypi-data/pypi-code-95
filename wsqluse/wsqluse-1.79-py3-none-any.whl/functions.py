def zip_dicts(unsend, col_names):
    # Собирает словарь из значений и ключей, добавляет в список и возврашает
    listname = []
    for report in unsend:
        a = dict(zip(col_names, report))
        listname.append(a)
    return listname


def get_execute_result(*args, **kwargs):
    # Создает и возвращает словарь из передаваемых параметров
    response = {}
    for k, v in kwargs.items():
        response[k] = v
    return response
