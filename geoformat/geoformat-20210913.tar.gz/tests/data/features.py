import copy
import datetime

from tests.data.geometries import (
    POINT,
    POINT_EMPTY,
    MULTIPOINT,
    MULTIPOINT_EMPTY,
    LINESTRING,
    LINESTRING_EMPTY,
    MULTILINESTRING,
    MULTILINESTRING_EMPTY,
    POLYGON,
    POLYGON_EMPTY,
    MULTIPOLYGON,
    MULTIPOLYGON_EMPTY,
    GEOMETRYCOLLECTION,
    GEOMETRYCOLLECTION_EMPTY,
    GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES,
    POINT_WKB_BIG_ENDIAN,
    GEOMETRYCOLLECTION_WKB_BIG_ENDIAN,
    POINT_WKB_HEX_BIG_ENDIAN,
    GEOMETRYCOLLECTION_WKB_HEX_BIG_ENDIAN
)

from geoformat.conversion.geometry_conversion import geometry_to_wkb

date_time_value = datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10, microsecond=999)
date_value = date_time_value.date()
time_value = date_time_value.time()

# FEATURE ATTRIBUTES ONLY
feature_attributes_only = {
    "attributes":
        {
            "field_integer": 586,
            "field_integer_list": [5879, 8557],
            "field_real": 8789.97568,
            "field_real_list": [89798.3654, 8757.97568],
            "field_string": "salut",
            "field_string_list": ["bonjour", "monsieur"],
            "field_none": None,
            "field_date": date_value,
            "field_time": time_value,
            "field_datetime": date_time_value,
            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
            "field_boolean": True
        }
}

feature_attributes_only_without_none_field = copy.deepcopy(feature_attributes_only)
del feature_attributes_only_without_none_field['attributes']["field_none"]

feature_attributes_only_boolean_false = {
    "attributes":
        {
            "field_integer": 0,
            "field_integer_list": [],
            "field_real": 0.,
            "field_real_list": [],
            "field_string": "False",
            "field_string_list": [],
            "field_none": None,
            "field_date": date_value,
            "field_time": time_value,
            "field_datetime": date_time_value,
            "field_binary": b'',
            "field_boolean": False
        }
}


# 3 FEATURES WITH SAME ATTRIBUTES STRUCTURE (NAMED ALFA)
feature_structure_alpha_1 = {"attributes": {
            "field_integer": 586.,  # 0
            "field_integer_list": "[5879, 8557]",  # 1
            "field_real": "8789.98",  # 2
            "field_real_list": "[89798.3654, 8757.]",  # 3
            "field_string": None,  # 4
            # missing intentionaly field_string_list  # 10
            "field_date": date_value,  # 5
            "field_time": '18:41:04',  # 6
            # missing intentionaly date_time  # 11
            "field_binary": "b'\\x00\\x00\\x00\\x00\\x04\\x00\\x00\\x00\\x02\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00'",  # 7
            "field_boolean": True,  # 8
            "field_none": None,  # 9
        }
}

feature_structure_alpha_2 = {"attributes": {
            "field_integer": 1466.,
            "field_integer_list": [987, 2345.],
            "field_real": 8789,
            "field_real_list": [2, 5],
            "field_string": "salut",
            "field_string_list": "['hi', 'mister']",
            # missing intentionaly field_date
            "field_time": time_value,
            "field_datetime": date_time_value,
            "field_binary": b'\x00\x00\x00\x00\x01@\xef\xf3k\n=p\xa4@\xbd\xe6\x8b\x02\x0cI\xba',
            "field_boolean": False,
            "field_none": None,
        }
}

feature_structure_alpha_3 = {
    "attributes": {
            "field_integer": 149.,
            "field_integer_list": [987, 2345.],
            "field_real": 8789,
            "field_real_list": [2, 5],
            "field_string": date_time_value,
            "field_string_list": "['hi', 'mister']",
            # missing intentionaly field_date
            "field_time": time_value,
            "field_datetime": date_value,
            "field_binary": '000000000140eff36b0a3d70a440bde68b020c49ba',
            "field_boolean": 1,
            "field_none": "NULL",
    }
}

# feature date, time datetime
feature_date_time_datetime_str = {"attributes": {'field_date': '2020-03-31', 'field_time': '11:22:10.000999', 'field_datetime': '2020-03-31 11:22:10.000999'}}
feature_date_time_datetime_lib = {"attributes": {'field_date': date_value, 'field_time': time_value, 'field_datetime': date_time_value}}

# FEATURE GEOMETRY ONLY
feature_dpt_data_only_a = {"attributes": {"CODE_DEPT": "53", "NOM_DEPT": "MAYENNE"}}
feature_dpt_data_only_b = {"attributes": {"CODE_DEPT": "02", "NOM_DEPT": "AISNE"}}
feature_dpt_data_only_c = {"attributes": {"CODE_DEPT": "95", "NOM_DEPT": "VAL-D'OISE"}}
feature_dpt_data_only_d = {"attributes": {"CODE_DEPT": "56", "NOM_DEPT": "MORBIHAN"}}

feature_dpt_geometry_only_a = {
            "geometry": {
                "type": "Polygon",
                "bbox": (382932.0, 6743442.0, 474394.0, 6833996.0),
                "coordinates": [
                    [
                        [399495.0, 6830885.0],
                        [398130.0, 6822559.0],
                        [400321.0, 6810723.0],
                        [395852.0, 6803336.0],
                        [398626.0, 6784333.0],
                        [400465.0, 6781914.0],
                        [400197.0, 6773697.0],
                        [394099.0, 6773357.0],
                        [390140.0, 6770978.0],
                        [386941.0, 6760260.0],
                        [382932.0, 6754022.0],
                        [389872.0, 6749698.0],
                        [393110.0, 6750366.0],
                        [402067.0, 6747685.0],
                        [404251.0, 6751414.0],
                        [412442.0, 6746090.0],
                        [419671.0, 6744167.0],
                        [429458.0, 6743442.0],
                        [440863.0, 6746201.0],
                        [446732.0, 6745443.0],
                        [446459.0, 6750432.0],
                        [442128.0, 6753611.0],
                        [448124.0, 6758669.0],
                        [447308.0, 6764356.0],
                        [455060.0, 6767070.0],
                        [451057.0, 6776681.0],
                        [459373.0, 6778102.0],
                        [460615.0, 6783387.0],
                        [458409.0, 6789055.0],
                        [466280.0, 6794064.0],
                        [465298.0, 6799724.0],
                        [467628.0, 6811401.0],
                        [473893.0, 6813452.0],
                        [474394.0, 6821359.0],
                        [467262.0, 6822174.0],
                        [466087.0, 6830999.0],
                        [463434.0, 6833996.0],
                        [457920.0, 6827997.0],
                        [451256.0, 6826715.0],
                        [446687.0, 6829012.0],
                        [441174.0, 6828584.0],
                        [437568.0, 6825109.0],
                        [429868.0, 6822252.0],
                        [422197.0, 6821752.0],
                        [414934.0, 6829326.0],
                        [407934.0, 6831360.0],
                        [404267.0, 6828490.0],
                        [399495.0, 6830885.0],
                    ]
                ],
            }
        }  # i_feat 10 in geolayer_geometry_only

feature_dpt_geometry_only_b = {
            "geometry": {
                "type": "Polygon",
                "bbox": (698137.0, 6861428.0, 790134.0, 6997000.0),
                "coordinates": [
                    [
                        [776081.0, 6923412.0],
                        [775403.0, 6934852.0],
                        [777906.0, 6941851.0],
                        [774574.0, 6946610.0],
                        [779463.0, 6948255.0],
                        [781387.0, 6953785.0],
                        [790134.0, 6962730.0],
                        [787172.0, 6965431.0],
                        [789845.0, 6973793.0],
                        [788558.0, 6985051.0],
                        [781905.0, 6987282.0],
                        [778060.0, 6986162.0],
                        [770359.0, 6988977.0],
                        [766237.0, 6992385.0],
                        [753505.0, 6995276.0],
                        [751253.0, 6997000.0],
                        [744014.0, 6992056.0],
                        [739058.0, 6995179.0],
                        [735248.0, 6991264.0],
                        [725313.0, 6993104.0],
                        [720100.0, 6990781.0],
                        [716534.0, 6992565.0],
                        [712391.0, 6990404.0],
                        [713833.0, 6986563.0],
                        [708480.0, 6979518.0],
                        [705667.0, 6969289.0],
                        [708546.0, 6956332.0],
                        [707064.0, 6950845.0],
                        [709520.0, 6938240.0],
                        [706939.0, 6934901.0],
                        [711648.0, 6928031.0],
                        [706805.0, 6926038.0],
                        [706929.0, 6919738.0],
                        [698137.0, 6911415.0],
                        [701957.0, 6908433.0],
                        [704672.0, 6899225.0],
                        [710189.0, 6894765.0],
                        [705248.0, 6890863.0],
                        [712067.0, 6888882.0],
                        [712559.0, 6879371.0],
                        [722321.0, 6872132.0],
                        [724211.0, 6867685.0],
                        [729581.0, 6862815.0],
                        [735603.0, 6861428.0],
                        [738742.0, 6868146.0],
                        [744067.0, 6871735.0],
                        [747254.0, 6882494.0],
                        [743801.0, 6891376.0],
                        [745398.0, 6894771.0],
                        [751361.0, 6898188.0],
                        [747051.0, 6913033.0],
                        [761575.0, 6918670.0],
                        [767112.0, 6923360.0],
                        [775242.0, 6918312.0],
                        [776081.0, 6923412.0],
                    ]
                ],
            }
        }  # i_feat 21 in geolayer_geometry_only

feature_dpt_geometry_only_c = {
            "geometry": {
                "type": "Polygon",
                "bbox": (698137.0, 6861428.0, 790134.0, 6997000.0),
                "coordinates": [
                    [
                        [598361.0, 6887345.0],
                        [603102.0, 6887292.0],
                        [606678.0, 6883543.0],
                        [614076.0, 6886919.0],
                        [622312.0, 6880731.0],
                        [628641.0, 6878089.0],
                        [633062.0, 6879807.0],
                        [641836.0, 6872490.0],
                        [641404.0, 6867928.0],
                        [648071.0, 6872567.0],
                        [653619.0, 6875101.0],
                        [660416.0, 6872923.0],
                        [667303.0, 6878971.0],
                        [670084.0, 6886723.0],
                        [659205.0, 6894147.0],
                        [652314.0, 6895981.0],
                        [649761.0, 6898738.0],
                        [645465.0, 6895048.0],
                        [633020.0, 6901508.0],
                        [626847.0, 6897876.0],
                        [618689.0, 6896449.0],
                        [612180.0, 6899061.0],
                        [608283.0, 6898554.0],
                        [605624.0, 6904387.0],
                        [603501.0, 6902160.0],
                        [601892.0, 6893098.0],
                        [598361.0, 6887345.0],
                    ]
                ],
            }
        }  # i_feat 70 in geolayer_geometry_only


feature_dpt_geometry_only_d = {
            "geometry": {
                "type": "MultiPolygon",
                "bbox": (202166.0, 6704696.0, 322365.0, 6807535.0),
                "coordinates": [
                    [
                        [
                            [229520.0, 6710085.0],
                            [240383.0, 6704696.0],
                            [240163.0, 6708285.0],
                            [235835.0, 6713741.0],
                            [229006.0, 6716339.0],
                            [229520.0, 6710085.0],
                        ]
                    ],
                    [
                        [
                            [212687.0, 6770001.0],
                            [211559.0, 6762660.0],
                            [216528.0, 6752538.0],
                            [224759.0, 6753321.0],
                            [234540.0, 6747533.0],
                            [234220.0, 6745025.0],
                            [240082.0, 6736634.0],
                            [251238.0, 6736509.0],
                            [260889.0, 6740570.0],
                            [266327.0, 6740184.0],
                            [271833.0, 6736526.0],
                            [269308.0, 6731426.0],
                            [263161.0, 6733044.0],
                            [258643.0, 6731063.0],
                            [263631.0, 6725691.0],
                            [274085.0, 6728424.0],
                            [283689.0, 6728526.0],
                            [290663.0, 6724762.0],
                            [288997.0, 6719519.0],
                            [300067.0, 6720583.0],
                            [315995.0, 6726944.0],
                            [317487.0, 6738014.0],
                            [315562.0, 6748257.0],
                            [318803.0, 6749864.0],
                            [322365.0, 6758359.0],
                            [317839.0, 6765781.0],
                            [320890.0, 6769878.0],
                            [317014.0, 6776765.0],
                            [309516.0, 6779524.0],
                            [306739.0, 6782705.0],
                            [310549.0, 6787938.0],
                            [306966.0, 6794650.0],
                            [300637.0, 6793781.0],
                            [298204.0, 6799128.0],
                            [291749.0, 6798375.0],
                            [285132.0, 6789099.0],
                            [280665.0, 6785525.0],
                            [277875.0, 6787107.0],
                            [279762.0, 6794931.0],
                            [270150.0, 6795768.0],
                            [252150.0, 6805897.0],
                            [246074.0, 6807146.0],
                            [242780.0, 6802066.0],
                            [233945.0, 6800703.0],
                            [229439.0, 6804532.0],
                            [212675.0, 6807535.0],
                            [202658.0, 6804638.0],
                            [202166.0, 6798131.0],
                            [205220.0, 6785800.0],
                            [211608.0, 6786141.0],
                            [216607.0, 6782805.0],
                            [223352.0, 6780867.0],
                            [221788.0, 6771592.0],
                            [212687.0, 6770001.0],
                        ]
                    ],
                ],
            }
        }  # i_feat 51 in geolayer_geometry_only

feature_dpt_data_and_geometry_a = {
    "attributes": {"CODE_DEPT": "53", "NOM_DEPT": "MAYENNE"},
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [399495.0, 6830885.0],
                [398130.0, 6822559.0],
                [400321.0, 6810723.0],
                [395852.0, 6803336.0],
                [398626.0, 6784333.0],
                [400465.0, 6781914.0],
                [400197.0, 6773697.0],
                [394099.0, 6773357.0],
                [390140.0, 6770978.0],
                [386941.0, 6760260.0],
                [382932.0, 6754022.0],
                [389872.0, 6749698.0],
                [393110.0, 6750366.0],
                [402067.0, 6747685.0],
                [404251.0, 6751414.0],
                [412442.0, 6746090.0],
                [419671.0, 6744167.0],
                [429458.0, 6743442.0],
                [440863.0, 6746201.0],
                [446732.0, 6745443.0],
                [446459.0, 6750432.0],
                [442128.0, 6753611.0],
                [448124.0, 6758669.0],
                [447308.0, 6764356.0],
                [455060.0, 6767070.0],
                [451057.0, 6776681.0],
                [459373.0, 6778102.0],
                [460615.0, 6783387.0],
                [458409.0, 6789055.0],
                [466280.0, 6794064.0],
                [465298.0, 6799724.0],
                [467628.0, 6811401.0],
                [473893.0, 6813452.0],
                [474394.0, 6821359.0],
                [467262.0, 6822174.0],
                [466087.0, 6830999.0],
                [463434.0, 6833996.0],
                [457920.0, 6827997.0],
                [451256.0, 6826715.0],
                [446687.0, 6829012.0],
                [441174.0, 6828584.0],
                [437568.0, 6825109.0],
                [429868.0, 6822252.0],
                [422197.0, 6821752.0],
                [414934.0, 6829326.0],
                [407934.0, 6831360.0],
                [404267.0, 6828490.0],
                [399495.0, 6830885.0],
            ]
        ],
    },
}
feature_dpt_data_and_geometry_b = {
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [776081.0, 6923412.0],
                        [775403.0, 6934852.0],
                        [777906.0, 6941851.0],
                        [774574.0, 6946610.0],
                        [779463.0, 6948255.0],
                        [781387.0, 6953785.0],
                        [790134.0, 6962730.0],
                        [787172.0, 6965431.0],
                        [789845.0, 6973793.0],
                        [788558.0, 6985051.0],
                        [781905.0, 6987282.0],
                        [778060.0, 6986162.0],
                        [770359.0, 6988977.0],
                        [766237.0, 6992385.0],
                        [753505.0, 6995276.0],
                        [751253.0, 6997000.0],
                        [744014.0, 6992056.0],
                        [739058.0, 6995179.0],
                        [735248.0, 6991264.0],
                        [725313.0, 6993104.0],
                        [720100.0, 6990781.0],
                        [716534.0, 6992565.0],
                        [712391.0, 6990404.0],
                        [713833.0, 6986563.0],
                        [708480.0, 6979518.0],
                        [705667.0, 6969289.0],
                        [708546.0, 6956332.0],
                        [707064.0, 6950845.0],
                        [709520.0, 6938240.0],
                        [706939.0, 6934901.0],
                        [711648.0, 6928031.0],
                        [706805.0, 6926038.0],
                        [706929.0, 6919738.0],
                        [698137.0, 6911415.0],
                        [701957.0, 6908433.0],
                        [704672.0, 6899225.0],
                        [710189.0, 6894765.0],
                        [705248.0, 6890863.0],
                        [712067.0, 6888882.0],
                        [712559.0, 6879371.0],
                        [722321.0, 6872132.0],
                        [724211.0, 6867685.0],
                        [729581.0, 6862815.0],
                        [735603.0, 6861428.0],
                        [738742.0, 6868146.0],
                        [744067.0, 6871735.0],
                        [747254.0, 6882494.0],
                        [743801.0, 6891376.0],
                        [745398.0, 6894771.0],
                        [751361.0, 6898188.0],
                        [747051.0, 6913033.0],
                        [761575.0, 6918670.0],
                        [767112.0, 6923360.0],
                        [775242.0, 6918312.0],
                        [776081.0, 6923412.0],
                    ]
                ],
            },
            "attributes": {"CODE_DEPT": "02", "NOM_DEPT": "AISNE"},
        }
feature_dpt_data_and_geometry_c = {
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [598361.0, 6887345.0],
                        [603102.0, 6887292.0],
                        [606678.0, 6883543.0],
                        [614076.0, 6886919.0],
                        [622312.0, 6880731.0],
                        [628641.0, 6878089.0],
                        [633062.0, 6879807.0],
                        [641836.0, 6872490.0],
                        [641404.0, 6867928.0],
                        [648071.0, 6872567.0],
                        [653619.0, 6875101.0],
                        [660416.0, 6872923.0],
                        [667303.0, 6878971.0],
                        [670084.0, 6886723.0],
                        [659205.0, 6894147.0],
                        [652314.0, 6895981.0],
                        [649761.0, 6898738.0],
                        [645465.0, 6895048.0],
                        [633020.0, 6901508.0],
                        [626847.0, 6897876.0],
                        [618689.0, 6896449.0],
                        [612180.0, 6899061.0],
                        [608283.0, 6898554.0],
                        [605624.0, 6904387.0],
                        [603501.0, 6902160.0],
                        [601892.0, 6893098.0],
                        [598361.0, 6887345.0],
                    ]
                ],
            },
            "attributes": {"CODE_DEPT": "95", "NOM_DEPT": "VAL-D'OISE"},
        }
feature_dpt_data_and_geometry_d = {
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [229520.0, 6710085.0],
                            [240383.0, 6704696.0],
                            [240163.0, 6708285.0],
                            [235835.0, 6713741.0],
                            [229006.0, 6716339.0],
                            [229520.0, 6710085.0],
                        ]
                    ],
                    [
                        [
                            [212687.0, 6770001.0],
                            [211559.0, 6762660.0],
                            [216528.0, 6752538.0],
                            [224759.0, 6753321.0],
                            [234540.0, 6747533.0],
                            [234220.0, 6745025.0],
                            [240082.0, 6736634.0],
                            [251238.0, 6736509.0],
                            [260889.0, 6740570.0],
                            [266327.0, 6740184.0],
                            [271833.0, 6736526.0],
                            [269308.0, 6731426.0],
                            [263161.0, 6733044.0],
                            [258643.0, 6731063.0],
                            [263631.0, 6725691.0],
                            [274085.0, 6728424.0],
                            [283689.0, 6728526.0],
                            [290663.0, 6724762.0],
                            [288997.0, 6719519.0],
                            [300067.0, 6720583.0],
                            [315995.0, 6726944.0],
                            [317487.0, 6738014.0],
                            [315562.0, 6748257.0],
                            [318803.0, 6749864.0],
                            [322365.0, 6758359.0],
                            [317839.0, 6765781.0],
                            [320890.0, 6769878.0],
                            [317014.0, 6776765.0],
                            [309516.0, 6779524.0],
                            [306739.0, 6782705.0],
                            [310549.0, 6787938.0],
                            [306966.0, 6794650.0],
                            [300637.0, 6793781.0],
                            [298204.0, 6799128.0],
                            [291749.0, 6798375.0],
                            [285132.0, 6789099.0],
                            [280665.0, 6785525.0],
                            [277875.0, 6787107.0],
                            [279762.0, 6794931.0],
                            [270150.0, 6795768.0],
                            [252150.0, 6805897.0],
                            [246074.0, 6807146.0],
                            [242780.0, 6802066.0],
                            [233945.0, 6800703.0],
                            [229439.0, 6804532.0],
                            [212675.0, 6807535.0],
                            [202658.0, 6804638.0],
                            [202166.0, 6798131.0],
                            [205220.0, 6785800.0],
                            [211608.0, 6786141.0],
                            [216607.0, 6782805.0],
                            [223352.0, 6780867.0],
                            [221788.0, 6771592.0],
                            [212687.0, 6770001.0],
                        ]
                    ],
                ],
            },
            "attributes": {"CODE_DEPT": "56", "NOM_DEPT": "MORBIHAN"},
        }


feature_dpt_data_and_geometry_a_serialized = {
    "attributes": str(feature_dpt_data_and_geometry_a['attributes']),
    "geometry": geometry_to_wkb(feature_dpt_data_and_geometry_a['geometry'])
}
feature_dpt_data_and_geometry_b_serialized = {
    "attributes": str(feature_dpt_data_and_geometry_b['attributes']),
    "geometry": geometry_to_wkb(feature_dpt_data_and_geometry_b['geometry'])
}
feature_dpt_data_and_geometry_c_serialized = {
    "attributes": str(feature_dpt_data_and_geometry_c['attributes']),
    "geometry": geometry_to_wkb(feature_dpt_data_and_geometry_c['geometry'])
}
feature_dpt_data_and_geometry_d_serialized = {
    "attributes": str(feature_dpt_data_and_geometry_d['attributes']),
    "geometry": geometry_to_wkb(feature_dpt_data_and_geometry_d['geometry'])
}

feature_geometry_only_point = {"geometry": POINT}
feature_geometry_only_point_empty = {"geometry": POINT_EMPTY}
feature_geometry_only_linestring = {"geometry": LINESTRING}
feature_geometry_only_linestring_empty = {"geometry": LINESTRING_EMPTY}
feature_geometry_only_polygon = {"geometry": POLYGON}
feature_geometry_only_polygon_empty = {"geometry": POLYGON_EMPTY}
feature_geometry_only_multipoint = {"geometry": MULTIPOINT}
feature_geometry_only_multipoint_empty = {"geometry": MULTIPOINT_EMPTY}
feature_geometry_only_multilinestring = {"geometry": MULTILINESTRING}
feature_geometry_only_multilinestring_empty = {"geometry": MULTILINESTRING_EMPTY}
feature_geometry_only_multipolygon = {"geometry": MULTIPOLYGON}
feature_geometry_only_multipolygon_empty = {"geometry": MULTIPOLYGON_EMPTY}
feature_geometry_only_collection = {"geometry": GEOMETRYCOLLECTION}
feature_geometry_only_collection_empty = {"geometry": GEOMETRYCOLLECTION_EMPTY}
feature_geometry_only_collection_with_empty_geometries = {"geometry": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES}

feature_attributes_bytes_only_a = {"attributes": {
    "field_bytes": POINT_WKB_BIG_ENDIAN,
    "field_hexa_a": None,
    "field_hexa_b": POINT_WKB_HEX_BIG_ENDIAN,
    "field_bytes_hexa_a": POINT_WKB_HEX_BIG_ENDIAN,
    "field_bytes_hexa_b": "hello world"}}
feature_attributes_bytes_only_b = {"attributes": {
    "field_bytes": None,
    "field_hexa_a": POINT_WKB_HEX_BIG_ENDIAN,
    "field_hexa_b": 'hello world',
    "field_bytes_hexa_a": None,
    "field_bytes_hexa_b": POINT_WKB_BIG_ENDIAN}}
feature_attributes_bytes_only_c = {"attributes": {
    "field_bytes": GEOMETRYCOLLECTION_WKB_BIG_ENDIAN,
    "field_hexa_a": GEOMETRYCOLLECTION_WKB_HEX_BIG_ENDIAN,
    "field_hexa_b": GEOMETRYCOLLECTION_WKB_HEX_BIG_ENDIAN,
    "field_bytes_hexa_a":GEOMETRYCOLLECTION_WKB_BIG_ENDIAN ,
    "field_bytes_hexa_b": GEOMETRYCOLLECTION_WKB_HEX_BIG_ENDIAN}}

# FEATURES LIST
feature_list_attribute_only = [feature_attributes_only]

feature_list_geometry_only = [
    feature_dpt_geometry_only_a,
    feature_dpt_geometry_only_b,
    feature_dpt_geometry_only_c,
    feature_dpt_geometry_only_d
]

feature_list_data_and_geometry = [
    feature_dpt_data_and_geometry_a,
    feature_dpt_data_and_geometry_b,
    feature_dpt_data_and_geometry_c,
    feature_dpt_data_and_geometry_d
]

feature_list_geometry_only_with_all_geometries = [
    feature_geometry_only_point,
    feature_geometry_only_point_empty,
    feature_geometry_only_linestring,
    feature_geometry_only_linestring_empty,
    feature_geometry_only_polygon,
    feature_geometry_only_polygon_empty,
    feature_geometry_only_multipoint,
    feature_geometry_only_multipoint_empty,
    feature_geometry_only_multilinestring,
    feature_geometry_only_multilinestring_empty,
    feature_geometry_only_multipolygon,
    feature_geometry_only_multipolygon_empty,
    feature_geometry_only_collection,
    feature_geometry_only_collection_empty,
    feature_geometry_only_collection_with_empty_geometries
]
feature_list_structure_alpha = [feature_structure_alpha_1, feature_structure_alpha_2, feature_structure_alpha_3]

feature_list_bytes_attributes = [
    feature_attributes_bytes_only_a,
    feature_attributes_bytes_only_b,
    feature_attributes_bytes_only_c
]

feature_list_date_time_datetime_attributes_lib = [feature_date_time_datetime_lib]
feature_list_date_time_datetime_attributes_str = [feature_date_time_datetime_str]
