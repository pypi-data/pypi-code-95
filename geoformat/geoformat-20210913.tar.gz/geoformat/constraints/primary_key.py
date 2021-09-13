from geoformat.conf.error_messages import non_unique_values
from geoformat.conversion.feature_conversion import feature_deserialize
from geoformat.conf.format_data import value_to_iterable_value
from geoformat.conf.error_messages import missing_field


def create_pk(geolayer, pk_field_name):
    """
    Return pk dictionary

    :param geolayer: geolayer
    :param pk_field_name: field that we want add constraint
    :return: pk dictionary
    """
    # chek if field exist in geolayer
    field_exists = False
    if 'fields' in geolayer['metadata']:
        field_exists = geolayer['metadata']['fields'].get(pk_field_name, False)

    if field_exists:
        # create empty dictionary
        pk_dictionary = {}

        # get value to index
        for i_feat in geolayer['features']:
            feature = geolayer['features'][i_feat]

            # deserialize feature if serialized
            if 'feature_serialize' in geolayer['metadata']:
                if geolayer['metadata']['feature_serialize']:
                    feature = feature_deserialize(serialized_feature=feature, bbox=False)

            pk_field_value = feature['attributes'][pk_field_name]

            # if pk_field_value is list we have to transform to tuple
            if isinstance(pk_field_value, list):
                pk_field_value = value_to_iterable_value(value=pk_field_value, output_iterable_type=tuple)

            # check if value is unique or not
            if pk_field_value in pk_dictionary:
                raise Exception(non_unique_values.format(field_name=pk_field_name))
            else:
                # save i_feat in pk dictionary
                pk_dictionary[pk_field_value] = i_feat

        return pk_dictionary
    else:
        raise Exception(missing_field.format(field_name=pk_field_name))
