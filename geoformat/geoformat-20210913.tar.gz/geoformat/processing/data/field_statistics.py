
def field_statistics(geolayer, statistic_field, bessel_correction=True):
    """
    This function return a dictionary with statistics result in it.

        statistic_key : SUM, MEAN, MIN, MAX, RANGE, STD, COUNT, FIRST, LAST, VARIANCE, WEIGHTED_MEAN, COVARIANCE

    INPUT / OUTPUT field type table :
         One field is required :
            SUM : if original field type is real or integer       | output original field type
            MEAN : if original field type is real or integer      | output real
            MIN : if original field type is real or integer       | output original field type
            MAX : if original field type is real or integer       | output original field type
            RANGE : if original field type is real or integer     | output original field type
            STD : if original field type is real or integer       | output real
            COUNT :  original field type doesn't matter           | output integer
            FIRST : original field type doesn't matter            | output original field type
            LAST : original field type doesn't matter             | output original field type
            VARIANCE : if original field type is real or integer  | output real

        Two fields are required :
            WEIGHTED_MEAN : fields type is real or integer        | output real
            COVARIANCE : fields type is real or integer           | output real


    statistic_fields :
        structure example [(field_name_A, statistic_key),
                           ((field_name_a, field_name_c), statistic_key),
                           (...),
                           (field_name_X, statistic_key_1),
                           (field_name_X, statistic_key_2)]

    bassel_correction : if True in case of STD or VARIANCE calculation apply bessel correction :
        https://en.wikipedia.org/wiki/Bessel%27s_correction

    output structure : dict
        output example : {  field_name_a: {statistic_key: statistic value}
                            (field_name_a, field_name_c) : {statistic_key: statistic value}
                            field_name_x {statistic_key_1: statistic value,
                                         {statistic_key_2: statistic value}
                        }

    :param geolayer: input geolayer that contains data
    :param statistic_field:
    :param bessel_correction: if True in case of STD or VARIANCE calculation apply bessel correction
    :return: dict
    """

    valid_field_type = {'Integer', 'IntegerList', 'Real', 'RealList', 'Date', 'Time', 'DateTime'}
    statistic_keys = {'SUM', 'MEAN', 'MIN', 'MAX', 'RANGE', 'STD', 'COUNT', 'FIRST', 'LAST', 'VARIANCE',
                      'WEIGHTED_MEAN', 'COVARIANCE'}

    # test if field in statistic_field are valid
    for i_stat, (field_value, statistic_type) in enumerate(statistic_field):
        if isinstance(field_value, str):
            if 'fields' in geolayer['metadata']:
                field_name_type = geolayer["metadata"]['fields'][field_value]['type']
                if field_name_type not in valid_field_type or statistic_type not in statistic_keys:
                    statistic_field[i_stat] = None
        elif isinstance(field_value, (list, tuple, set)):
            for field_name in field_value:
                if isinstance(field_name, str):
                    if 'fields' in geolayer['metadata']:
                        field_name_type = geolayer["metadata"]['fields'][field_name]['type']
                        if field_name_type not in valid_field_type or statistic_type not in statistic_keys:
                            statistic_field[i_stat] = None
        else:
            print('error : field_name type is not correct')

    statistic_field = [value for value in statistic_field if value is not None]

    statistic_result = [0] * len(statistic_field)

    for fid, i_feat in enumerate(geolayer['features']):
        feature = geolayer['features'][i_feat]

        # if feature is serialized
        if 'feature_serialize' in geolayer['metadata']:
            if geolayer['metadata']['feature_serialize']:
                feature = eval(feature)

        for i, (field_name, statistic_type) in enumerate(statistic_field):

            if statistic_type.upper() == 'SUM':
                statistic_result[i] += feature['attributes'][field_name]
            elif statistic_type.upper() == 'MEAN':
                if fid == 0:
                    statistic_result[i] = feature['attributes'][field_name]
                else:
                    statistic_result[i] = (statistic_result[i] * fid + feature['attributes'][field_name]) / (
                            fid + 1)
            elif statistic_type.upper() == 'WEIGHTED_MEAN':
                (field_name_a, field_name_b) = field_name
                value_field_a = feature['attributes'][field_name_a]
                value_field_b = feature['attributes'][field_name_b]
                if fid == 0:
                    statistic_result[i] = (value_field_a * value_field_b, value_field_b)
                else:
                    statistic_result[i] = (statistic_result[i][0] + value_field_a * value_field_b, statistic_result[i][1] +value_field_b)
                # last iteration
                if fid == len(geolayer['features']) - 1:
                    statistic_result[i] = statistic_result[i][0] / statistic_result[i][1]
            elif statistic_type.upper() == 'COVARIANCE':
                (field_name_a, field_name_b) = field_name
                value_a = feature['attributes'][field_name_a]
                value_b = feature['attributes'][field_name_b]
                if fid == 0:
                    product_sum = 0.
                    means = field_statistics(geolayer, [(field_name_a, 'MEAN'), (field_name_b, 'MEAN')])
                    mean_a = means[field_name_a]['MEAN']
                    mean_b = means[field_name_b]['MEAN']
                product = (value_a - mean_a) * (value_b - mean_b)
                product_sum += product

                # if last iteration
                if fid == len(geolayer['features']) - 1:
                    result_value = product_sum / (len(geolayer['features']))
                    statistic_result[i] = result_value

            elif statistic_type.upper() == 'MIN':
                if fid == 0:
                    statistic_result[i] = feature['attributes'][field_name]
                statistic_result[i] = min(statistic_result[i], feature['attributes'][field_name])
            elif statistic_type.upper() == 'MAX':
                if fid == 0:
                    statistic_result[i] = feature['attributes'][field_name]
                statistic_result[i] = max(statistic_result[i], feature['attributes'][field_name])
            elif statistic_type.upper() == 'RANGE':
                if fid == 0:
                    save_min = feature['attributes'][field_name]
                    save_max = feature['attributes'][field_name]
                save_min = min(save_min, feature['attributes'][field_name])
                save_max = max(save_max, feature['attributes'][field_name])
                statistic_result[i] = save_max - save_min

            elif statistic_type.upper() in ['STD', 'VARIANCE']:
                if fid == 0:
                    # saving values in a list
                    statistic_result[i] = [0] * len(geolayer['features'])
                    statistic_result[i][0] = feature['attributes'][field_name]
                else:
                    statistic_result[i][fid] = feature['attributes'][field_name]
                # if last iteration
                if fid == len(geolayer['features']) - 1:
                    nb_value = len(statistic_result[i])
                    mean_value = sum(statistic_result[i]) / nb_value
                    mean_deviation = [(value - mean_value) ** 2 for value in statistic_result[i]]

                    if bessel_correction:
                        result_value = sum(mean_deviation) / (nb_value - 1)
                    else:
                        result_value = sum(mean_deviation) / nb_value

                    if statistic_type.upper() == 'STD':
                        result_value = result_value ** 0.5

                    statistic_result[i] = result_value

            # for all field type
            if statistic_type.upper() == 'COUNT':
                statistic_result[i] += 1
            elif statistic_type.upper() == 'FIRST':
                if fid == 0:
                    statistic_result[i] = feature['attributes'][field_name]
            elif statistic_type.upper() == 'LAST':
                statistic_result[i] = feature['attributes'][field_name]

    # write results in dico result
    dico_result = {}
    for i_stat, (field_name, statistic_type) in enumerate(statistic_field):
        try:
            dico_result[field_name][statistic_type] = statistic_result[i_stat]
        except KeyError:
            dico_result[field_name] = {statistic_type: statistic_result[i_stat]}

    return dico_result