from geoformat.conversion.geolayer_conversion import create_geolayer_from_i_feat_list

####
#
# CLAUSE
#
# The CLAUSE functions return a directly a list of i_feat or a dict with a list associates to each key of i_feat
###

def clause_where(geolayer, field_name, predicate, values):
    # transform values to iterate variable
    if not isinstance(values, (list, tuple)):
        if isinstance(values, tuple):
            values = list(values)
        else:
            values = [values]
    # init result list
    i_feat_list = []
    # loop on geolayer
    for i_feat in geolayer['features']:
        feature = geolayer['features'][i_feat]
        feature_value = feature['attributes'][field_name]

        # save feature_value in list by default
        if isinstance(feature_value, (list, tuple, set)):
            feature_value_list = feature_value
        else:
            feature_value_list = [feature_value]

        save_i_feat = False
        # loop on feature_value_list
        for feature_value in feature_value_list:
            if '=' in predicate or 'IN' in predicate or predicate == 'LIKE' or predicate == 'BETWEEN':
                if feature_value in values:
                    save_i_feat = True
                    break

            if predicate in '<>' or predicate == 'BETWEEN':
                if predicate == '<>':
                    if feature_value not in values:
                        save_i_feat = True
                else:
                    if (predicate == '>' or predicate == 'BETWEEN') and feature_value > values[0]:
                        save_i_feat = True
                    if (predicate == '<' or predicate == 'BETWEEN') and feature_value < values[-1]:
                        save_i_feat = True

            if predicate == 'IS':
                if feature_value in values:
                    feature_value = True
                if 'NOT' in predicate and feature_value is True:
                    save_i_feat = False


        if save_i_feat:
            i_feat_list.append(i_feat)

    return i_feat_list


def clause_where_combination(geolayer, clause_where_dict):
    """
    WATCH OUT THIS FUNCTION IS DEPRECATED PLEASE USE clause_where AND MAKE YOUR COMBINATION BY YOURSELF

    example for clause_where_dict :
           clause_where_dict= {'field_predicate': {
                                    'foo_field_name': {
                                        'predicate': '=',
                                        'values': [0, 1, 2]
                                    }
                                }
                            }


    :param geolayer:
    :param clause_where_dict:
    :param field_combination:
    :return:
    """

    def field_predicate(geolayer, field_predicate_dict, field_combination=None):

        i_feat_predicate = {}
        for field_name in field_predicate_dict['field_predicate']:
            field_predicate = field_predicate_dict['field_predicate'][field_name]
            predicate = field_predicate['predicate'].upper()
            if 'values' in field_predicate.keys():
                values = field_predicate['values']
                if not isinstance(values, (list, tuple)):
                    if isinstance(values, tuple):
                        values = list(values)
                    else:
                        values = [field_predicate['values']]

            i_feat_list = []

            for i_feat in geolayer['features']:
                feature = geolayer['features'][i_feat]
                feature_value = feature['attributes'][field_name]

                # save feature_value in list by default
                if isinstance(feature_value, (list, tuple, set)):
                    feature_value_list = feature_value
                else:
                    feature_value_list = [feature_value]

                save_i_feat = False
                # loop on feature_value_list
                for feature_value in feature_value_list:
                    if '=' in predicate or 'IN' in predicate or predicate == 'LIKE' or predicate == 'BETWEEN':
                        if feature_value in values:
                            save_i_feat = True
                            break

                    if predicate in '<>' or predicate == 'BETWEEN':
                        if predicate == '<>':
                            if feature_value not in values:
                                save_i_feat = True
                        else:
                            if (predicate == '>' or predicate == 'BETWEEN') and feature_value > values[0]:
                                save_i_feat = True
                            if (predicate == '<' or predicate == 'BETWEEN') and feature_value < values[-1]:
                                save_i_feat = True

                    if 'IS' in predicate:
                        if 'NOT' in predicate:
                            if feature_value:
                                save_i_feat = True
                        else:
                            if not feature_value:
                                save_i_feat = True

                if save_i_feat:
                    i_feat_list.append(i_feat)

            # save i_feat
            i_feat_predicate[field_name] = i_feat_list

        if field_combination:
            final_i_feat_set = set([])
            for field_name in i_feat_predicate:
                field_name_i_feat_set = set(i_feat_predicate[field_name])
                if field_combination == 'OR':
                    final_i_feat_set.update(field_name_i_feat_set)
                if field_combination == 'AND':
                    if len(final_i_feat_set) == 0:
                        final_i_feat_set = field_name_i_feat_set
                    else:
                        final_i_feat_set.intersection_update(field_name_i_feat_set)

            final_i_feat_list = list(final_i_feat_set)
            return final_i_feat_list
        else:
            return i_feat_list

    if 'field_combination' in clause_where_dict.keys():
        if isinstance(clause_where_dict['field_combination'], str):
            field_combination = clause_where_dict['field_combination']
            i_feat_list = field_predicate(geolayer, clause_where_dict, field_combination)

    # just field_predicate in  clause_where_dict
    else:
        i_feat_list = field_predicate(geolayer, clause_where_dict)

    return i_feat_list


def clause_group_by(geolayer, field_name_list):
    """
    Return a dictionnary with field name list as key and i_feat list from geolayer
    """

    if isinstance(field_name_list, str):
        field_name_list = [field_name_list]

    result_dico = {}
    for i_feat in geolayer['features']:
        feature = geolayer['features'][i_feat]

        # if feature is serialized
        if 'feature_serialize' in geolayer['metadata']:
            if geolayer['metadata']['feature_serialize']:
                feature = eval(feature)

        field_value_tuple = tuple(
            [feature['attributes'][field_name] if field_name in feature['attributes'] else None for field_name in
             field_name_list])

        # convert list value to tuple (if exists) very rare
        field_value_tuple = tuple([tuple(value) if isinstance(value, list) else value for value in field_value_tuple])

        if field_value_tuple in result_dico:
            result_dico[field_value_tuple].append(i_feat)
        else:
            result_dico[field_value_tuple] = [i_feat]

    return result_dico


def clause_order_by(geolayer, order_parameters):
    """
    Send i_feat list in order define in order_parameters

    order_parameters format : 3 poosibilities :
        order_parameters = 'field_name' (order by default is ASC)
        order_parameters = ('field_name', 'ASC' or 'DESC')
        order_parameter = [('field_name_a', 'ASC' or 'DESC'), ('field_name_b', 'ASC' or 'DESC'), ..., ('field_name_n', 'ASC' or 'DESC'
    """

    def insert_in_order_list_by_split(value, i_feat_list, order_by_list):
        # try to insert at extremity of list
        # value is lower of last value in order_by_list
        if value <= order_by_list[0][0]:
            if value == order_by_list[0][0]:
                order_by_list[0][1] = order_by_list[0][0] + i_feat_list
            else:
                order_by_list = [(value, i_feat_list)] + order_by_list
            return order_by_list
        # value is upper of last value in order_by_list
        elif value >= order_by_list[-1][0]:
            if value == order_by_list[-1][0]:
                order_by_list[-1][1] = order_by_list[-1][0] + i_feat_list
            else:
                order_by_list = order_by_list + [(value, i_feat_list)]
            return order_by_list

        # if no insertion we have to split in two
        list_cuter_idx = int(len(order_by_list) / 2)
        if value <= order_by_list[list_cuter_idx-1][0]:
            if value == order_by_list[list_cuter_idx-1][0]:
                order_by_list[list_cuter_idx - 1][1] += i_feat_list
                return order_by_list
            else:
                order_by_list_splited = order_by_list[:list_cuter_idx]
                result = insert_in_order_list_by_split(value, i_feat_list, order_by_list_splited)
                return result + order_by_list[list_cuter_idx:]

        if value >= order_by_list[list_cuter_idx][0]:
            if value == order_by_list[list_cuter_idx][0]:
                order_by_list[list_cuter_idx][1] += i_feat_list
                return order_by_list
            else:
                order_by_list_splited = order_by_list[list_cuter_idx:]
                result = insert_in_order_list_by_split(value, i_feat_list, order_by_list_splited)
                return order_by_list[:list_cuter_idx] + result

        return order_by_list[:list_cuter_idx] + [(value, i_feat_list)] + order_by_list[list_cuter_idx:]


    def order_values(dico_value, field_order):
        """
            This function ordered value in function of field order
        """
        order_by_list = None
        none_value_i_feat = []
        for value in dico_value:
            i_feat_list = dico_value[value]
            if None in value:
                none_value_i_feat += i_feat_list
            else:
                # first iteration
                if not order_by_list:
                    order_by_list = [(value, i_feat_list)]
                else:
                    order_by_list = insert_in_order_list_by_split(value, i_feat_list, order_by_list)

        # reverse order if we are DESC
        if field_order.upper() == 'DESC' and order_by_list:
            order_by_list = sorted(order_by_list, reverse=True)

        # add none value (if exists) in function of order_fields
        if len(none_value_i_feat) > 0:
            if order_by_list:
                if field_order.upper() == 'ASC':
                    order_by_list += [((None,), none_value_i_feat)]
                else:
                    order_by_list = [((None,), none_value_i_feat)] + order_by_list
            else:
                order_by_list = [(None, none_value_i_feat)]

        return order_by_list


    def field_group_by_then_order(geolayer, order_parameters):
        """
        This function is used to realise first a group by and reorder result
        Then it recall it if there is an other field_order_paramenters
        """
        (field_name, field_order) = order_parameters[0]
        gb_field_name = clause_group_by(geolayer, field_name)
        gb_field_name_ordered = order_values(gb_field_name, field_order)
        result_i_feat_list = []
        for value, i_feat_list in gb_field_name_ordered:
            if len(i_feat_list) > 1:
                if len(order_parameters) > 1:
                    new_order_parameters = order_parameters[1:]
                    new_geolayer = create_geolayer_from_i_feat_list(geolayer, i_feat_list, reset_i_feat=False)
                    result_i_feat_list += field_group_by_then_order(new_geolayer, new_order_parameters)
                else:
                    result_i_feat_list += i_feat_list
            else:
                result_i_feat_list += i_feat_list

        return result_i_feat_list

    # verification enters parameters
    if isinstance(order_parameters, (list, tuple)):
        authorised_order_value = set(['ASC', 'DESC'])
        for i_field, field in enumerate(order_parameters):
            if len(field) == 1:
                order_parameters[i_field] = (field, 'ASC')
            elif len(field) == 2:
                if field[1].upper() not in authorised_order_value:
                    raise Exception('error you must add "ASC" or "DESC" key in second position')
            else:
                raise Exception('error')
    elif isinstance(order_parameters, str):
        order_parameters = [(order_parameters, 'ASC')]
    else:
        raise Exception("error: order_parameters must be a list / tuple or str value")

    for (field_name, order_value) in order_parameters:
        if field_name not in geolayer['metadata']['fields']:
            print('error : {field_name} does not exists in geolayer'.format(field_name))

    return field_group_by_then_order(geolayer, order_parameters)

