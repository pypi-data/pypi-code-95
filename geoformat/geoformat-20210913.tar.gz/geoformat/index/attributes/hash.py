def create_attribute_index(geolayer, field_name):
    index_dict = {'type': 'hashtable', 'index': {}}

    # récupération de la valeur du champs à indexer
    for i_feat in geolayer['features']:
        feature = geolayer['features'][i_feat]

        # if feature is serialized
        if 'feature_serialize' in geolayer['metadata']:
            if geolayer['metadata']['feature_serialize']:
                feature = eval(feature)

        field_value = feature['attributes'][field_name]

        try:
            index_dict['index'][field_value].append(i_feat)
        except KeyError:
            index_dict['index'][field_value] = [i_feat]

    return index_dict
