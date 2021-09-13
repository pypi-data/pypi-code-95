from dbstream.tools.dck_infos import generate_dck_info


def unest_data(row_data, k):
    result = []
    for r in row_data:
        if r.get(k):
            for rk in r[k].keys():
                r[k + '_' + rk] = r[k].get(rk)
        r.pop(k, None)
        result.append(r)
    return result


def treat_json_data(data, list_of_tables_to_send=None, list_of_pop_fields=None):
    table_name = data['table_name']
    row_data = data['data']
    data['data'] = generate_dck_info(row_data)
    if not list_of_tables_to_send:
        list_of_tables_to_send = []
    if not list_of_pop_fields:
        list_of_pop_fields = {table_name: []}
    if not list_of_pop_fields.get(table_name):
        list_of_pop_fields[table_name] = []
    for row in row_data:
        row_keys = list(row.keys())
        for k in row_keys:
            k_table_name = table_name + '_' + k
            if k_table_name in [t['table_name'] for t in list_of_tables_to_send]:
                continue
            if k in list_of_pop_fields[table_name]:
                continue
            if isinstance(row[k], dict):
                row_data = unest_data(row_data, k)
                list_of_pop_fields[table_name].append(k)
                list_of_tables_to_send, list_of_pop_fields = treat_json_data(
                    {'table_name': table_name, 'data': row_data},
                    list_of_tables_to_send=list_of_tables_to_send,
                    list_of_pop_fields=list_of_pop_fields)
            elif isinstance(row[k], list):
                k_row_data = []
                for r in row_data:
                    if r.get(k):
                        for i in range(len(r[k])):
                            rr = r[k][i]
                            if not isinstance(rr, dict):
                                rr = {'value': rr}
                            rr['__' + table_name.split('.')[1] + '__dck_id___'] = r['__dck_id___']
                            rr['__' + table_name.split('.')[1] + '__dck_id___' + 'order'] = i
                            k_row_data.append(rr)
                        r.pop(k, None)
                list_of_pop_fields[table_name].append(k)
                k_row_data = generate_dck_info(k_row_data)
                k_data = {'table_name': k_table_name, 'data': k_row_data}
                list_of_tables_to_send.append(k_data)
                list_of_tables_to_send, list_of_pop_fields = treat_json_data(k_data,
                                                                             list_of_tables_to_send=list_of_tables_to_send,
                                                                             list_of_pop_fields=list_of_pop_fields)
    if not list_of_tables_to_send:
        list_of_tables_to_send = [{'table_name': table_name, 'data': row_data}]
    elif table_name not in [t['table_name'] for t in list_of_tables_to_send]:
        list_of_tables_to_send.append({'table_name': table_name, 'data': row_data})
    return list_of_tables_to_send, list_of_pop_fields
