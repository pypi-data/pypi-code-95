""" Здесь содержатся функции, необходимые для выполнения основного функционала
WServer (methods.py) """

import ast
import base64
import datetime
import os
import inspect
import uuid
from wtas.operators import WTA
from wserver_compound import settings


def format_wsqluse_response(func):
    """ Декоратор, цель которого - отформатировать ответ от выполенния SQL
        комманды через фреймвор WSQLuse
    :param func: Метод WServer, который возвращает ответ фреймворка WSQLuse
    :return:
        Если response позитивный:
            {'status': True, info: *id: int*}
        Если response негативный:
            {'status': False, info: Python Traceback}
    """

    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        new_response = response
        if response['status'] == 'success':
            new_response['info'] = response['info'][0][0]
            new_response['status'] = True

        else:
            new_response['info'] = response['info']
            new_response['status'] = False
        return new_response

    return wrapper


def operate_mask(sql_shell, mask: str, table_name: str, record_id: int):
    """
    Обрабатывает получившуюся маску.

    :param sql_shell: Объект типа WSQluse для работы с БД.
    :param mask: Маска ("name='some', foo='bar'" или же просто "")
    :param table_name: Имя таблицы.
    :param record_id: ID записи, которую надо менять согласно маске.
    :return:
    """
    if not mask:
        return {'status': 'failed', 'info': 'Укажите, что изменить.'}
    mask = mask[:-1]
    command = "UPDATE {} SET {} WHERE id={}".format(table_name, mask,
                                                    record_id)
    return sql_shell.update_record(command)


def format_act_time(time, time_mask='%Y.%m.%d %H:%M:%S'):
    """ Получает дату-время, в виде строки, конвертирует его в объект
        datetime.datetime и возвращает результат.

    :param time: Время
    :param time_mask: Маска времени"""
    return datetime.datetime.strptime(time, time_mask)


def save_record_photo(record, photo_obj, photo_type):
    pass


def generate_photo_name(record_id=None):
    """
    Генерирует название фотографии. Добавляет к названию рандомный uuid4.
    :param record_id: ID заезда
    :return:
    """
    photo_name = '___'.join((str(record_id), str(uuid.uuid4())))
    full_photo_name = os.path.join(settings.PHOTOS_DIR, photo_name)
    full_photo_name = full_photo_name + '.png'
    return full_photo_name


def save_photo(photo_obj, photo_path):
    """ Сохранить фотографию по указанному пути
    :param photo_obj: Объект фотографии в кодировке base64
    :param photo_path: Путь, по которому сохранить фото"""
    with open(photo_path, 'wb') as fobj:
        photo_obj = ast.literal_eval(photo_obj)
        fobj.write(base64.decodebytes(photo_obj))
    return photo_path


def save_photo_database(sql_shell, record: int, photo_path, photo_type: int):
    command = """INSERT INTO act_photos 
                (record, photo_path, photo_type)
                VALUES (%s, %s, %s)"""
    values = (record, photo_path, photo_type)
    response = sql_shell.try_execute_double(command, values)
    return response


def encode_photo(photo_path):
    """ Кодирует фото в base64
    :param photo_path: Абсолютный путь до фото
    :return: Последовательность в кодировке base64"""
    with open(photo_path, 'rb') as fobj:
        photo_data = base64.b64encode(fobj.read())
    return photo_data


def get_user_ip(sql_shell, user_id: int,
                ip_contain_column: str = "last_ip"):
    """
    Получить IP адрес пользователя (полигона, по его БД).
    :param sql_shell: - экземпляр WSQluse для работы с БД.
    :param user_id: - ID пользователя в базе данных.
    :param ip_contain_column: - название поля, содержащего IP.
    :return:
        В случае успеха:
            IP адрес в строков представлении (str)
        Если же под таким ID пользователя нет, то:
            None
    """
    command = "SELECT {} FROM users WHERE id={}"
    command = command.format(ip_contain_column, user_id)
    response = sql_shell.try_execute_get(command)
    if response:
        return response[0][0]


def send_data_to_core(data_type):
    """
    Отправить новые данные на целевой полигон. (Новое авто, весовщик и т.д)
    :param data_type: Здесь указывается вид данных (operator, auto etc),
        согласно типу вызывается соответствующий метод QDK, который доставляет
        данные в QPI GCore.
    :return:
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            if response['status'] == 'success':
                all_args = collect_args(func, *args, **kwargs)
                polygon = all_args['polygon']
                if not polygon:
                    all_polygons = get_all_polygon_ids(all_args['sql_shell'])
                else:
                    all_polygons = [polygon]
                for polygon in all_polygons:
                    wta = WTA(data_type, 'gdb', 'watchman', 'hect0r1337',
                              '192.168.100.118', polygon)
                    response = wta.deliver(wserver_id=response['info'][0][0],
                                           **all_args)
            return response

        return wrapper

    return decorator


def get_all_polygon_ids(sql_shell):
    """
    Вернуть ID всех полигонов.

    :param sql_shell: Объект WSqluse для доступа к GDB.
    :return:
    """
    command = "SELECT polygon FROM duo_polygons WHERE duo_role=1"
    response = sql_shell.try_execute_get(command)
    if response:
        return [x[0] for x in response]


def collect_args(func, *args, **kwargs):
    """ Собирает все аргументы функции в словарь.
    :param func: функция, которую необходимо изучить и извлечь аргументы
    :return: возвращает словарь. """
    argspec = inspect.getfullargspec(func).args
    default_values = {
        k: v.default
        for k, v in inspect.signature(func).parameters.items()
        if v.default is not inspect.Parameter.empty
    }
    all_args = dict(zip(argspec, locals()['args']))
    all_args.update(kwargs)
    all_args.update(default_values)
    return all_args


def set_record_unactive(sql_shell, table_name, record_id, active=False):
    """
    Сделать запись неактивной. (Выставить значение поля column=False).

    :param sql_shell: Экземлпяр класса WSQluse для работы с БД.
    :param table_name: имя таблицы.
    :param record_id: ID записи.
    :return:
    """
    command = "UPDATE {} SET active={} WHERE id={}"
    command = command.format(table_name, active, record_id)
    return sql_shell.try_execute(command)
