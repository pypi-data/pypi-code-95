def alchemy_default_to_dict(params, data):
    data_list = []
    key_list = []
    for arg in params:
        key_list.append(str(arg).split(".")[-1])
    if isinstance(data, list):
        for d in data:
            dict_data = dict(zip(key_list, d))
            data_list.append(dict_data)
        return data_list
    else:
        if data:
            return dict(zip(key_list, data))
        else:
            return {}


def sqlalchemy_paging(Query, limit_number, offset_number):
    data_list = Query.limit(limit_number).offset(offset_number).all()
    data_count = 0
    if offset_number == 0:
        data_count = Query.count()
    return {"count": data_count, "dataSource": data_list}
