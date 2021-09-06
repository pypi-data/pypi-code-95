#!/usr/bin/env python3
import json
import sys
from astersay.plugins.general_http_plugin import BaseHttpClient

# Считываем файл с данными для плагина.
filename = sys.argv[1]
with open(filename) as f:
    plugin_data = json.load(f)

result, data = False, {}
try:
    requester = BaseHttpClient(plugin_data['config'])
    result, data = requester.make_request(plugin_data['variables'])
except Exception as ex:
    plugin_data['log_error'] = [
        f"Ошибка при работе базового http плагина: {str(ex)}"
    ]

variables = plugin_data['variables']
variables.update(data)

plugin_data['result'] = result

print('variables:', plugin_data['variables'])
# Для других типов блок скриптов это переопределение никак не повлияет.


######################
# Конец вашего кода. #
######################

# Перезаписываем файл с данными для возврата в диалог.
# Вы можете закомментировать этот код, если ничего не нужно сообщать диалогу,
# ни логов, ни переменных, ничего...
with open(filename, 'w') as f:
    json.dump(plugin_data, f)

# Обязательно указываем, что плагин успешно завершён, чтобы не прервать диалог.
sys.exit()
