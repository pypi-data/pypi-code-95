from geoformat.explore_data.print_data import (
    _get_features_data_table_line,
    _get_fields_metadata_table_line,
    print_features_data_table,
    print_metadata_field_table
)

from tests.data.geolayers import (
    geolayer_fr_dept_data_and_geometry,
    geolayer_fr_dept_data_only,
    geolayer_fr_dept_geometry_only
)

from test_all import test_function

get_features_data_table_line_parameters = {
    0: {
        "geolayer": geolayer_fr_dept_geometry_only,
        "field_name_list": None,
        "print_i_feat": True,
        "table_type": 'RST',
        "light": True,
        "display_geo_data": True,
        "max_width_coordinates_printing": 30,
        "limit": None,
        "header": True,
        "return_value": ('+--------+--------------+--------------------------------+', '| i_feat | type         | coordinates                    |', '+========+==============+================================+', '| 0      | Polygon      | [[[505760.0, 6248691.0] ...]]] |', '| 1      | Polygon      | [[[547193.0, 6388334.0] ...]]] |', '| 2      | Polygon      | [[[841110.0, 6468164.0] ...]]] |', '| 3      | Polygon      | [[[634422.0, 7101577.0] ...]]] |', '| 4      | Polygon      | [[[776081.0, 6923412.0] ...]]] |', '| 5      | Polygon      | [[[730707.0, 6810078.0] ...]]] |', '| 6      | Polygon      | [[[1009696.0, 6370071.0 ...]]] |', '| 7      | Polygon      | [[[753779.0, 6537018.0] ...]]] |', '| 8      | Polygon      | [[[505760.0, 6248691.0] ...]]] |', '| 9      | Polygon      | [[[806993.0, 6569822.0] ...]]] |', '| 10     | Polygon      | [[[399495.0, 6830885.0] ...]]] |', '| 11     | Polygon      | [[[459784.0, 6545825.0] ...]]] |', '| 12     | Polygon      | [[[417723.0, 6857101.0] ...]]] |', '| 13     | Polygon      | [[[590236.0, 6872273.0] ...]]] |', '| 14     | Polygon      | [[[986155.0, 6724947.0] ...]]] |', '| 15     | Polygon      | [[[904250.0, 6825381.0] ...]]] |', '| 16     | Polygon      | [[[486169.0, 6410676.0] ...]]] |', '| 17     | Polygon      | [[[503908.0, 6928958.0] ...]]] |', '| 18     | Polygon      | [[[915394.0, 6762341.0] ...]]] |', '| 19     | Polygon      | [[[642856.0, 6724786.0] ...]]] |', '| 20     | Polygon      | [[[779411.0, 6373918.0] ...]]] |', '| 21     | Polygon      | [[[776081.0, 6923412.0] ...]]] |', '| 22     | Polygon      | [[[334283.0, 6280551.0] ...]]] |', '| 23     | Polygon      | [[[642856.0, 6724786.0] ...]]] |', '| 24     | Polygon      | [[[1001023.0, 6834020.0 ...]]] |', '| 25     | Polygon      | [[[483517.0, 6558927.0] ...]]] |', '| 26     | Polygon      | [[[515635.0, 6515544.0] ...]]] |', '| 27     | Polygon      | [[[877344.0, 6596683.0] ...]]] |', '| 28     | Polygon      | [[[610874.0, 6360746.0] ...]]] |', '| 29     | Polygon      | [[[404251.0, 6660135.0] ...]]] |', '| 30     | Polygon      | [[[863140.0, 6525920.0] ...]]] |', '| 31     | Polygon      | [[[606642.0, 6924066.0] ...]]] |', '| 32     | Polygon      | [[[619220.0, 6339455.0] ...]]] |', '| 33     | Polygon      | [[[636090.0, 6591904.0] ...]]] |', '| 34     | Polygon      | [[[695265.0, 6784783.0] ...]]] |', '| 35     | Polygon      | [[[986052.0, 6752778.0] ...]]] |', '| 36     | Polygon      | [[[753779.0, 6537018.0] ...]]] |', '| 37     | Polygon      | [[[583992.0, 6314318.0] ...]]] |', '| 38     | Polygon      | [[[612314.0, 6962826.0] ...]]] |', '| 39     | Polygon      | [[[823302.0, 6827043.0] ...]]] |', '| 40     | Polygon      | [[[831641.0, 6353746.0] ...]]] |', '| 41     | Polygon      | [[[1011125.0, 6809400.0 ...]]] |', '| 42     | Polygon      | [[[719561.0, 6234874.0] ...]]] |', '| 43     | Polygon      | [[[695265.0, 6784783.0] ...]]] |', '| 44     | Polygon      | [[[706470.0, 6995042.0] ...]]] |', '| 45     | Polygon      | [[[708104.0, 6472781.0] ...]]] |', '| 46     | Polygon      | [[[776081.0, 6923412.0] ...]]] |', '| 47     | Polygon      | [[[428954.0, 6200122.0] ...]]] |', '| 48     | Polygon      | [[[547193.0, 6388334.0] ...]]] |', '| 49     | Polygon      | [[[992638.0, 6305621.0] ...]]] |', '| 50     | Polygon      | [[[521086.0, 6735350.0] ...]]] |', '| 51     | MultiPolygon | [[[[229520.0, 6710085. ...]]]] |', '| 52     | Polygon      | [[[539112.0, 6843338.0] ...]]] |', '| 53     | Polygon      | [[[1232225.0, 6105798.0 ...]]] |', '| 54     | Polygon      | [[[879041.0, 6935896.0] ...]]] |', '| 55     | Polygon      | [[[510545.0, 6875400.0] ...]]] |', '| 56     | Polygon      | [[[877344.0, 6596683.0] ...]]] |', '| 57     | Polygon      | [[[524704.0, 6194181.0] ...]]] |', '| 58     | Polygon      | [[[563452.0, 6484264.0] ...]]] |', '| 59     | Polygon      | [[[987691.0, 6753958.0] ...]]] |', '| 60     | Polygon      | [[[573297.0, 6677558.0] ...]]] |', '| 61     | Polygon      | [[[634422.0, 7101577.0] ...]]] |', '| 62     | Polygon      | [[[1010786.0, 6719537.0 ...]]] |', '| 63     | Polygon      | [[[382163.0, 6750361.0] ...]]] |', '| 64     | Polygon      | [[[698236.0, 6718784.0] ...]]] |', '| 65     | MultiPolygon | [[[[330825.0, 6841252. ...]]]] |', '| 66     | Polygon      | [[[334283.0, 6280551.0] ...]]] |', '| 67     | Polygon      | [[[210124.0, 6860562.0] ...]]] |', '| 68     | Polygon      | [[[995359.0, 6526975.0] ...]]] |', '| 69     | Polygon      | [[[605624.0, 6904387.0] ...]]] |', '| 70     | Polygon      | [[[598361.0, 6887345.0] ...]]] |', '| 71     | Polygon      | [[[783517.0, 6693799.0] ...]]] |', '| 72     | Polygon      | [[[871408.0, 6655745.0] ...]]] |', '| 73     | Polygon      | [[[643163.0, 6853168.0] ...]]] |', '| 74     | Polygon      | [[[483517.0, 6558927.0] ...]]] |', '| 75     | Polygon      | [[[306966.0, 6794650.0] ...]]] |', '| 76     | Polygon      | [[[702446.0, 6632753.0] ...]]] |', '| 77     | MultiPolygon | [[[[365341.0, 6575902. ...]]]] |', '| 78     | Polygon      | [[[728488.0, 6430309.0] ...]]] |', '| 79     | Polygon      | [[[664821.0, 6258302.0] ...]]] |', '| 80     | Polygon      | [[[921863.0, 6404787.0] ...]]] |', '| 81     | Polygon      | [[[600206.0, 6164532.0] ...]]] |', '| 82     | Polygon      | [[[956276.0, 6452799.0] ...]]] |', '| 83     | Polygon      | [[[921863.0, 6404787.0] ...]]] |', '| 84     | MultiPolygon | [[[[850837.0, 6364673. ...]]]] |', '| 85     | Polygon      | [[[636090.0, 6591904.0] ...]]] |', '| 86     | Polygon      | [[[1232225.0, 6105798.0 ...]]] |', '| 87     | Polygon      | [[[563452.0, 6484264.0] ...]]] |', '| 88     | MultiPolygon | [[[[297360.0, 6667914. ...]]]] |', '| 89     | Polygon      | [[[917346.0, 6234793.0] ...]]] |', '| 90     | Polygon      | [[[670056.0, 6856451.0] ...]]] |', '| 91     | Polygon      | [[[650942.0, 6857646.0] ...]]] |', '| 92     | Polygon      | [[[698547.0, 6393953.0] ...]]] |', '| 93     | Polygon      | [[[799607.0, 6263119.0] ...]]] |', '| 94     | Polygon      | [[[650942.0, 6857646.0] ...]]] |', '| 95     | Polygon      | [[[670056.0, 6856451.0] ...]]] |', '+--------+--------------+--------------------------------+')
    },
    1: {
        "geolayer": geolayer_fr_dept_data_only,
        "field_name_list": None,
        "print_i_feat": True,
        "table_type": 'RST',
        "light": True,
        "display_geo_data": True,
        "max_width_coordinates_printing": 30,
        "limit": None,
        "header": True,
        "return_value": ('+--------+-----------+-------------------------+', '| i_feat | CODE_DEPT | NOM_DEPT                |', '+========+===========+=========================+', '| 0      | 32        | GERS                    |', '| 1      | 47        | LOT-ET-GARONNE          |', '| 2      | 38        | ISERE                   |', '| 3      | 62        | PAS-DE-CALAIS           |', '| 4      | 08        | ARDENNES                |', '| 5      | 10        | AUBE                    |', '| 6      | 06        | ALPES-MARITIMES         |', '| 7      | 42        | LOIRE                   |', '| 8      | 31        | HAUTE-GARONNE           |', '| 9      | 71        | SAONE-ET-LOIRE          |', '| 10     | 53        | MAYENNE                 |', '| 11     | 16        | CHARENTE                |', '| 12     | 50        | MANCHE                  |', '| 13     | 78        | YVELINES                |', '| 14     | 25        | DOUBS                   |', '| 15     | 55        | MEUSE                   |', '| 16     | 33        | GIRONDE                 |', '| 17     | 14        | CALVADOS                |', '| 18     | 88        | VOSGES                  |', '| 19     | 18        | CHER                    |', '| 20     | 07        | ARDECHE                 |', '| 21     | 02        | AISNE                   |', '| 22     | 64        | PYRENEES-ATLANTIQUES    |', '| 23     | 41        | LOIR-ET-CHER            |', '| 24     | 57        | MOSELLE                 |', '| 25     | 86        | VIENNE                  |', '| 26     | 24        | DORDOGNE                |', '| 27     | 39        | JURA                    |', '| 28     | 82        | TARN-ET-GARONNE         |', '| 29     | 49        | MAINE-ET-LOIRE          |', '| 30     | 69        | RHONE                   |', '| 31     | 27        | EURE                    |', '| 32     | 12        | AVEYRON                 |', '| 33     | 23        | CREUSE                  |', '| 34     | 45        | LOIRET                  |', '| 35     | 70        | HAUTE-SAONE             |', '| 36     | 63        | PUY-DE-DOME             |', '| 37     | 81        | TARN                    |', '| 38     | 76        | SEINE-MARITIME          |', '| 39     | 52        | HAUTE-MARNE             |', '| 40     | 30        | GARD                    |', '| 41     | 67        | BAS-RHIN                |', '| 42     | 11        | AUDE                    |', '| 43     | 77        | SEINE-ET-MARNE          |', '| 44     | 80        | SOMME                   |', '| 45     | 43        | HAUTE-LOIRE             |', '| 46     | 51        | MARNE                   |', '| 47     | 65        | HAUTES-PYRENEES         |', '| 48     | 46        | LOT                     |', '| 49     | 04        | ALPES-DE-HAUTE-PROVENCE |', '| 50     | 72        | SARTHE                  |', '| 51     | 56        | MORBIHAN                |', '| 52     | 28        | EURE-ET-LOIR            |', '| 53     | 2A        | CORSE-DU-SUD            |', '| 54     | 54        | MEURTHE-ET-MOSELLE      |', '| 55     | 61        | ORNE                    |', '| 56     | 01        | AIN                     |', '| 57     | 09        | ARIEGE                  |', '| 58     | 19        | CORREZE                 |', '| 59     | 68        | HAUT-RHIN               |', '| 60     | 37        | INDRE-ET-LOIRE          |', '| 61     | 59        | NORD                    |', '| 62     | 90        | TERRITOIRE DE BELFORT   |', '| 63     | 44        | LOIRE-ATLANTIQUE        |', '| 64     | 89        | YONNE                   |', '| 65     | 35        | ILLE-ET-VILAINE         |', '| 66     | 40        | LANDES                  |', '| 67     | 29        | FINISTERE               |', '| 68     | 74        | HAUTE-SAVOIE            |', '| 69     | 60        | OISE                    |', "| 70     | 95        | VAL-D'OISE              |", '| 71     | 58        | NIEVRE                  |', "| 72     | 21        | COTE-D'OR               |", '| 73     | 91        | ESSONNE                 |', '| 74     | 79        | DEUX-SEVRES             |', "| 75     | 22        | COTES-D'ARMOR           |", '| 76     | 03        | ALLIER                  |', '| 77     | 17        | CHARENTE-MARITIME       |', '| 78     | 15        | CANTAL                  |', '| 79     | 34        | HERAULT                 |', '| 80     | 26        | DROME                   |', '| 81     | 66        | PYRENEES-ORIENTALES     |', '| 82     | 73        | SAVOIE                  |', '| 83     | 05        | HAUTES-ALPES            |', '| 84     | 84        | VAUCLUSE                |', '| 85     | 36        | INDRE                   |', '| 86     | 2B        | HAUTE-CORSE             |', '| 87     | 87        | HAUTE-VIENNE            |', '| 88     | 85        | VENDEE                  |', '| 89     | 83        | VAR                     |', '| 90     | 94        | VAL-DE-MARNE            |', '| 91     | 92        | HAUTS-DE-SEINE          |', '| 92     | 48        | LOZERE                  |', '| 93     | 13        | BOUCHES-DU-RHONE        |', '| 94     | 75        | PARIS                   |', '| 95     | 93        | SEINE-SAINT-DENIS       |', '+--------+-----------+-------------------------+')
    },
    2: {
        "geolayer": geolayer_fr_dept_data_and_geometry,
        "field_name_list": None,
        "print_i_feat": True,
        "table_type": 'RST',
        "light": True,
        "display_geo_data": True,
        "max_width_coordinates_printing": 30,
        "limit": None,
        "header": True,
        "return_value": ('+--------+-----------+-------------------------+--------------+--------------------------------+', '| i_feat | CODE_DEPT | NOM_DEPT                | type         | coordinates                    |', '+========+===========+=========================+==============+================================+', '| 0      | 32        | GERS                    | Polygon      | [[[505760.0, 6248691.0] ...]]] |', '| 1      | 47        | LOT-ET-GARONNE          | Polygon      | [[[547193.0, 6388334.0] ...]]] |', '| 2      | 38        | ISERE                   | Polygon      | [[[841110.0, 6468164.0] ...]]] |', '| 3      | 62        | PAS-DE-CALAIS           | Polygon      | [[[634422.0, 7101577.0] ...]]] |', '| 4      | 08        | ARDENNES                | Polygon      | [[[776081.0, 6923412.0] ...]]] |', '| 5      | 10        | AUBE                    | Polygon      | [[[730707.0, 6810078.0] ...]]] |', '| 6      | 06        | ALPES-MARITIMES         | Polygon      | [[[1009696.0, 6370071.0 ...]]] |', '| 7      | 42        | LOIRE                   | Polygon      | [[[753779.0, 6537018.0] ...]]] |', '| 8      | 31        | HAUTE-GARONNE           | Polygon      | [[[505760.0, 6248691.0] ...]]] |', '| 9      | 71        | SAONE-ET-LOIRE          | Polygon      | [[[806993.0, 6569822.0] ...]]] |', '| 10     | 53        | MAYENNE                 | Polygon      | [[[399495.0, 6830885.0] ...]]] |', '| 11     | 16        | CHARENTE                | Polygon      | [[[459784.0, 6545825.0] ...]]] |', '| 12     | 50        | MANCHE                  | Polygon      | [[[417723.0, 6857101.0] ...]]] |', '| 13     | 78        | YVELINES                | Polygon      | [[[590236.0, 6872273.0] ...]]] |', '| 14     | 25        | DOUBS                   | Polygon      | [[[986155.0, 6724947.0] ...]]] |', '| 15     | 55        | MEUSE                   | Polygon      | [[[904250.0, 6825381.0] ...]]] |', '| 16     | 33        | GIRONDE                 | Polygon      | [[[486169.0, 6410676.0] ...]]] |', '| 17     | 14        | CALVADOS                | Polygon      | [[[503908.0, 6928958.0] ...]]] |', '| 18     | 88        | VOSGES                  | Polygon      | [[[915394.0, 6762341.0] ...]]] |', '| 19     | 18        | CHER                    | Polygon      | [[[642856.0, 6724786.0] ...]]] |', '| 20     | 07        | ARDECHE                 | Polygon      | [[[779411.0, 6373918.0] ...]]] |', '| 21     | 02        | AISNE                   | Polygon      | [[[776081.0, 6923412.0] ...]]] |', '| 22     | 64        | PYRENEES-ATLANTIQUES    | Polygon      | [[[334283.0, 6280551.0] ...]]] |', '| 23     | 41        | LOIR-ET-CHER            | Polygon      | [[[642856.0, 6724786.0] ...]]] |', '| 24     | 57        | MOSELLE                 | Polygon      | [[[1001023.0, 6834020.0 ...]]] |', '| 25     | 86        | VIENNE                  | Polygon      | [[[483517.0, 6558927.0] ...]]] |', '| 26     | 24        | DORDOGNE                | Polygon      | [[[515635.0, 6515544.0] ...]]] |', '| 27     | 39        | JURA                    | Polygon      | [[[877344.0, 6596683.0] ...]]] |', '| 28     | 82        | TARN-ET-GARONNE         | Polygon      | [[[610874.0, 6360746.0] ...]]] |', '| 29     | 49        | MAINE-ET-LOIRE          | Polygon      | [[[404251.0, 6660135.0] ...]]] |', '| 30     | 69        | RHONE                   | Polygon      | [[[863140.0, 6525920.0] ...]]] |', '| 31     | 27        | EURE                    | Polygon      | [[[606642.0, 6924066.0] ...]]] |', '| 32     | 12        | AVEYRON                 | Polygon      | [[[619220.0, 6339455.0] ...]]] |', '| 33     | 23        | CREUSE                  | Polygon      | [[[636090.0, 6591904.0] ...]]] |', '| 34     | 45        | LOIRET                  | Polygon      | [[[695265.0, 6784783.0] ...]]] |', '| 35     | 70        | HAUTE-SAONE             | Polygon      | [[[986052.0, 6752778.0] ...]]] |', '| 36     | 63        | PUY-DE-DOME             | Polygon      | [[[753779.0, 6537018.0] ...]]] |', '| 37     | 81        | TARN                    | Polygon      | [[[583992.0, 6314318.0] ...]]] |', '| 38     | 76        | SEINE-MARITIME          | Polygon      | [[[612314.0, 6962826.0] ...]]] |', '| 39     | 52        | HAUTE-MARNE             | Polygon      | [[[823302.0, 6827043.0] ...]]] |', '| 40     | 30        | GARD                    | Polygon      | [[[831641.0, 6353746.0] ...]]] |', '| 41     | 67        | BAS-RHIN                | Polygon      | [[[1011125.0, 6809400.0 ...]]] |', '| 42     | 11        | AUDE                    | Polygon      | [[[719561.0, 6234874.0] ...]]] |', '| 43     | 77        | SEINE-ET-MARNE          | Polygon      | [[[695265.0, 6784783.0] ...]]] |', '| 44     | 80        | SOMME                   | Polygon      | [[[706470.0, 6995042.0] ...]]] |', '| 45     | 43        | HAUTE-LOIRE             | Polygon      | [[[708104.0, 6472781.0] ...]]] |', '| 46     | 51        | MARNE                   | Polygon      | [[[776081.0, 6923412.0] ...]]] |', '| 47     | 65        | HAUTES-PYRENEES         | Polygon      | [[[428954.0, 6200122.0] ...]]] |', '| 48     | 46        | LOT                     | Polygon      | [[[547193.0, 6388334.0] ...]]] |', '| 49     | 04        | ALPES-DE-HAUTE-PROVENCE | Polygon      | [[[992638.0, 6305621.0] ...]]] |', '| 50     | 72        | SARTHE                  | Polygon      | [[[521086.0, 6735350.0] ...]]] |', '| 51     | 56        | MORBIHAN                | MultiPolygon | [[[[229520.0, 6710085. ...]]]] |', '| 52     | 28        | EURE-ET-LOIR            | Polygon      | [[[539112.0, 6843338.0] ...]]] |', '| 53     | 2A        | CORSE-DU-SUD            | Polygon      | [[[1232225.0, 6105798.0 ...]]] |', '| 54     | 54        | MEURTHE-ET-MOSELLE      | Polygon      | [[[879041.0, 6935896.0] ...]]] |', '| 55     | 61        | ORNE                    | Polygon      | [[[510545.0, 6875400.0] ...]]] |', '| 56     | 01        | AIN                     | Polygon      | [[[877344.0, 6596683.0] ...]]] |', '| 57     | 09        | ARIEGE                  | Polygon      | [[[524704.0, 6194181.0] ...]]] |', '| 58     | 19        | CORREZE                 | Polygon      | [[[563452.0, 6484264.0] ...]]] |', '| 59     | 68        | HAUT-RHIN               | Polygon      | [[[987691.0, 6753958.0] ...]]] |', '| 60     | 37        | INDRE-ET-LOIRE          | Polygon      | [[[573297.0, 6677558.0] ...]]] |', '| 61     | 59        | NORD                    | Polygon      | [[[634422.0, 7101577.0] ...]]] |', '| 62     | 90        | TERRITOIRE DE BELFORT   | Polygon      | [[[1010786.0, 6719537.0 ...]]] |', '| 63     | 44        | LOIRE-ATLANTIQUE        | Polygon      | [[[382163.0, 6750361.0] ...]]] |', '| 64     | 89        | YONNE                   | Polygon      | [[[698236.0, 6718784.0] ...]]] |', '| 65     | 35        | ILLE-ET-VILAINE         | MultiPolygon | [[[[330825.0, 6841252. ...]]]] |', '| 66     | 40        | LANDES                  | Polygon      | [[[334283.0, 6280551.0] ...]]] |', '| 67     | 29        | FINISTERE               | Polygon      | [[[210124.0, 6860562.0] ...]]] |', '| 68     | 74        | HAUTE-SAVOIE            | Polygon      | [[[995359.0, 6526975.0] ...]]] |', '| 69     | 60        | OISE                    | Polygon      | [[[605624.0, 6904387.0] ...]]] |', "| 70     | 95        | VAL-D'OISE              | Polygon      | [[[598361.0, 6887345.0] ...]]] |", '| 71     | 58        | NIEVRE                  | Polygon      | [[[783517.0, 6693799.0] ...]]] |', "| 72     | 21        | COTE-D'OR               | Polygon      | [[[871408.0, 6655745.0] ...]]] |", '| 73     | 91        | ESSONNE                 | Polygon      | [[[643163.0, 6853168.0] ...]]] |', '| 74     | 79        | DEUX-SEVRES             | Polygon      | [[[483517.0, 6558927.0] ...]]] |', "| 75     | 22        | COTES-D'ARMOR           | Polygon      | [[[306966.0, 6794650.0] ...]]] |", '| 76     | 03        | ALLIER                  | Polygon      | [[[702446.0, 6632753.0] ...]]] |', '| 77     | 17        | CHARENTE-MARITIME       | MultiPolygon | [[[[365341.0, 6575902. ...]]]] |', '| 78     | 15        | CANTAL                  | Polygon      | [[[728488.0, 6430309.0] ...]]] |', '| 79     | 34        | HERAULT                 | Polygon      | [[[664821.0, 6258302.0] ...]]] |', '| 80     | 26        | DROME                   | Polygon      | [[[921863.0, 6404787.0] ...]]] |', '| 81     | 66        | PYRENEES-ORIENTALES     | Polygon      | [[[600206.0, 6164532.0] ...]]] |', '| 82     | 73        | SAVOIE                  | Polygon      | [[[956276.0, 6452799.0] ...]]] |', '| 83     | 05        | HAUTES-ALPES            | Polygon      | [[[921863.0, 6404787.0] ...]]] |', '| 84     | 84        | VAUCLUSE                | MultiPolygon | [[[[850837.0, 6364673. ...]]]] |', '| 85     | 36        | INDRE                   | Polygon      | [[[636090.0, 6591904.0] ...]]] |', '| 86     | 2B        | HAUTE-CORSE             | Polygon      | [[[1232225.0, 6105798.0 ...]]] |', '| 87     | 87        | HAUTE-VIENNE            | Polygon      | [[[563452.0, 6484264.0] ...]]] |', '| 88     | 85        | VENDEE                  | MultiPolygon | [[[[297360.0, 6667914. ...]]]] |', '| 89     | 83        | VAR                     | Polygon      | [[[917346.0, 6234793.0] ...]]] |', '| 90     | 94        | VAL-DE-MARNE            | Polygon      | [[[670056.0, 6856451.0] ...]]] |', '| 91     | 92        | HAUTS-DE-SEINE          | Polygon      | [[[650942.0, 6857646.0] ...]]] |', '| 92     | 48        | LOZERE                  | Polygon      | [[[698547.0, 6393953.0] ...]]] |', '| 93     | 13        | BOUCHES-DU-RHONE        | Polygon      | [[[799607.0, 6263119.0] ...]]] |', '| 94     | 75        | PARIS                   | Polygon      | [[[650942.0, 6857646.0] ...]]] |', '| 95     | 93        | SEINE-SAINT-DENIS       | Polygon      | [[[670056.0, 6856451.0] ...]]] |', '+--------+-----------+-------------------------+--------------+--------------------------------+')
    }
}

get_fields_metadata_table_line_parameters = {
    0: {
        "geolayer": geolayer_fr_dept_geometry_only,
        "field_name_list": None,
        "key_field_name": 'field name',
        "order_value": False,
        "table_type": 'RST',
        "light": True,
        "header": True,
        "return_value": ()
    },
    1: {
        "geolayer": geolayer_fr_dept_data_only,
        "field_name_list": None,
        "key_field_name": 'field name',
        "order_value": False,
        "table_type": 'RST',
        "light": True,
        "header": True,
        "return_value": ('+------------+--------+-------+-----------+-------+', '| field name | type   | width | precision | index |', '+============+========+=======+===========+=======+', '| CODE_DEPT  | String | 2     | None      | 0     |', '| NOM_DEPT   | String | 23    | None      | 1     |', '+------------+--------+-------+-----------+-------+')
    },
    2: {
        "geolayer": geolayer_fr_dept_data_and_geometry,
        "field_name_list": None,
        "key_field_name": 'field name',
        "order_value": False,
        "table_type": 'RST',
        "light": True,
        "header": True,
        "return_value": ('+------------+--------+-------+-----------+-------+', '| field name | type   | width | precision | index |', '+============+========+=======+===========+=======+', '| CODE_DEPT  | String | 2     | None      | 0     |', '| NOM_DEPT   | String | 23    | None      | 1     |', '+------------+--------+-------+-----------+-------+')
    },
}

print_features_data_table_parameters = {
    0: {
        "geolayer": geolayer_fr_dept_data_and_geometry,
        "field_name_list": None,
        "print_i_feat": True,
        "table_type": 'RST',
        "light": True,
        "display_geometry": True,
        "max_width_coordinates_printing": 30,
        "header": True,
        "return_value": """+--------+-----------+-------------------------+--------------+--------------------------------+
| i_feat | CODE_DEPT | NOM_DEPT                | type         | coordinates                    |
+========+===========+=========================+==============+================================+
| 0      | 32        | GERS                    | Polygon      | [[[505760.0, 6248691.0] ...]]] |
| 1      | 47        | LOT-ET-GARONNE          | Polygon      | [[[547193.0, 6388334.0] ...]]] |
| 2      | 38        | ISERE                   | Polygon      | [[[841110.0, 6468164.0] ...]]] |
| 3      | 62        | PAS-DE-CALAIS           | Polygon      | [[[634422.0, 7101577.0] ...]]] |
| 4      | 08        | ARDENNES                | Polygon      | [[[776081.0, 6923412.0] ...]]] |
| 5      | 10        | AUBE                    | Polygon      | [[[730707.0, 6810078.0] ...]]] |
| 6      | 06        | ALPES-MARITIMES         | Polygon      | [[[1009696.0, 6370071.0 ...]]] |
| 7      | 42        | LOIRE                   | Polygon      | [[[753779.0, 6537018.0] ...]]] |
| 8      | 31        | HAUTE-GARONNE           | Polygon      | [[[505760.0, 6248691.0] ...]]] |
| 9      | 71        | SAONE-ET-LOIRE          | Polygon      | [[[806993.0, 6569822.0] ...]]] |
| 10     | 53        | MAYENNE                 | Polygon      | [[[399495.0, 6830885.0] ...]]] |
| 11     | 16        | CHARENTE                | Polygon      | [[[459784.0, 6545825.0] ...]]] |
| 12     | 50        | MANCHE                  | Polygon      | [[[417723.0, 6857101.0] ...]]] |
| 13     | 78        | YVELINES                | Polygon      | [[[590236.0, 6872273.0] ...]]] |
| 14     | 25        | DOUBS                   | Polygon      | [[[986155.0, 6724947.0] ...]]] |
| 15     | 55        | MEUSE                   | Polygon      | [[[904250.0, 6825381.0] ...]]] |
| 16     | 33        | GIRONDE                 | Polygon      | [[[486169.0, 6410676.0] ...]]] |
| 17     | 14        | CALVADOS                | Polygon      | [[[503908.0, 6928958.0] ...]]] |
| 18     | 88        | VOSGES                  | Polygon      | [[[915394.0, 6762341.0] ...]]] |
| 19     | 18        | CHER                    | Polygon      | [[[642856.0, 6724786.0] ...]]] |
| 20     | 07        | ARDECHE                 | Polygon      | [[[779411.0, 6373918.0] ...]]] |
| 21     | 02        | AISNE                   | Polygon      | [[[776081.0, 6923412.0] ...]]] |
| 22     | 64        | PYRENEES-ATLANTIQUES    | Polygon      | [[[334283.0, 6280551.0] ...]]] |
| 23     | 41        | LOIR-ET-CHER            | Polygon      | [[[642856.0, 6724786.0] ...]]] |
| 24     | 57        | MOSELLE                 | Polygon      | [[[1001023.0, 6834020.0 ...]]] |
| 25     | 86        | VIENNE                  | Polygon      | [[[483517.0, 6558927.0] ...]]] |
| 26     | 24        | DORDOGNE                | Polygon      | [[[515635.0, 6515544.0] ...]]] |
| 27     | 39        | JURA                    | Polygon      | [[[877344.0, 6596683.0] ...]]] |
| 28     | 82        | TARN-ET-GARONNE         | Polygon      | [[[610874.0, 6360746.0] ...]]] |
| 29     | 49        | MAINE-ET-LOIRE          | Polygon      | [[[404251.0, 6660135.0] ...]]] |
| 30     | 69        | RHONE                   | Polygon      | [[[863140.0, 6525920.0] ...]]] |
| 31     | 27        | EURE                    | Polygon      | [[[606642.0, 6924066.0] ...]]] |
| 32     | 12        | AVEYRON                 | Polygon      | [[[619220.0, 6339455.0] ...]]] |
| 33     | 23        | CREUSE                  | Polygon      | [[[636090.0, 6591904.0] ...]]] |
| 34     | 45        | LOIRET                  | Polygon      | [[[695265.0, 6784783.0] ...]]] |
| 35     | 70        | HAUTE-SAONE             | Polygon      | [[[986052.0, 6752778.0] ...]]] |
| 36     | 63        | PUY-DE-DOME             | Polygon      | [[[753779.0, 6537018.0] ...]]] |
| 37     | 81        | TARN                    | Polygon      | [[[583992.0, 6314318.0] ...]]] |
| 38     | 76        | SEINE-MARITIME          | Polygon      | [[[612314.0, 6962826.0] ...]]] |
| 39     | 52        | HAUTE-MARNE             | Polygon      | [[[823302.0, 6827043.0] ...]]] |
| 40     | 30        | GARD                    | Polygon      | [[[831641.0, 6353746.0] ...]]] |
| 41     | 67        | BAS-RHIN                | Polygon      | [[[1011125.0, 6809400.0 ...]]] |
| 42     | 11        | AUDE                    | Polygon      | [[[719561.0, 6234874.0] ...]]] |
| 43     | 77        | SEINE-ET-MARNE          | Polygon      | [[[695265.0, 6784783.0] ...]]] |
| 44     | 80        | SOMME                   | Polygon      | [[[706470.0, 6995042.0] ...]]] |
| 45     | 43        | HAUTE-LOIRE             | Polygon      | [[[708104.0, 6472781.0] ...]]] |
| 46     | 51        | MARNE                   | Polygon      | [[[776081.0, 6923412.0] ...]]] |
| 47     | 65        | HAUTES-PYRENEES         | Polygon      | [[[428954.0, 6200122.0] ...]]] |
| 48     | 46        | LOT                     | Polygon      | [[[547193.0, 6388334.0] ...]]] |
| 49     | 04        | ALPES-DE-HAUTE-PROVENCE | Polygon      | [[[992638.0, 6305621.0] ...]]] |
| 50     | 72        | SARTHE                  | Polygon      | [[[521086.0, 6735350.0] ...]]] |
| 51     | 56        | MORBIHAN                | MultiPolygon | [[[[229520.0, 6710085. ...]]]] |
| 52     | 28        | EURE-ET-LOIR            | Polygon      | [[[539112.0, 6843338.0] ...]]] |
| 53     | 2A        | CORSE-DU-SUD            | Polygon      | [[[1232225.0, 6105798.0 ...]]] |
| 54     | 54        | MEURTHE-ET-MOSELLE      | Polygon      | [[[879041.0, 6935896.0] ...]]] |
| 55     | 61        | ORNE                    | Polygon      | [[[510545.0, 6875400.0] ...]]] |
| 56     | 01        | AIN                     | Polygon      | [[[877344.0, 6596683.0] ...]]] |
| 57     | 09        | ARIEGE                  | Polygon      | [[[524704.0, 6194181.0] ...]]] |
| 58     | 19        | CORREZE                 | Polygon      | [[[563452.0, 6484264.0] ...]]] |
| 59     | 68        | HAUT-RHIN               | Polygon      | [[[987691.0, 6753958.0] ...]]] |
| 60     | 37        | INDRE-ET-LOIRE          | Polygon      | [[[573297.0, 6677558.0] ...]]] |
| 61     | 59        | NORD                    | Polygon      | [[[634422.0, 7101577.0] ...]]] |
| 62     | 90        | TERRITOIRE DE BELFORT   | Polygon      | [[[1010786.0, 6719537.0 ...]]] |
| 63     | 44        | LOIRE-ATLANTIQUE        | Polygon      | [[[382163.0, 6750361.0] ...]]] |
| 64     | 89        | YONNE                   | Polygon      | [[[698236.0, 6718784.0] ...]]] |
| 65     | 35        | ILLE-ET-VILAINE         | MultiPolygon | [[[[330825.0, 6841252. ...]]]] |
| 66     | 40        | LANDES                  | Polygon      | [[[334283.0, 6280551.0] ...]]] |
| 67     | 29        | FINISTERE               | Polygon      | [[[210124.0, 6860562.0] ...]]] |
| 68     | 74        | HAUTE-SAVOIE            | Polygon      | [[[995359.0, 6526975.0] ...]]] |
| 69     | 60        | OISE                    | Polygon      | [[[605624.0, 6904387.0] ...]]] |
| 70     | 95        | VAL-D'OISE              | Polygon      | [[[598361.0, 6887345.0] ...]]] |
| 71     | 58        | NIEVRE                  | Polygon      | [[[783517.0, 6693799.0] ...]]] |
| 72     | 21        | COTE-D'OR               | Polygon      | [[[871408.0, 6655745.0] ...]]] |
| 73     | 91        | ESSONNE                 | Polygon      | [[[643163.0, 6853168.0] ...]]] |
| 74     | 79        | DEUX-SEVRES             | Polygon      | [[[483517.0, 6558927.0] ...]]] |
| 75     | 22        | COTES-D'ARMOR           | Polygon      | [[[306966.0, 6794650.0] ...]]] |
| 76     | 03        | ALLIER                  | Polygon      | [[[702446.0, 6632753.0] ...]]] |
| 77     | 17        | CHARENTE-MARITIME       | MultiPolygon | [[[[365341.0, 6575902. ...]]]] |
| 78     | 15        | CANTAL                  | Polygon      | [[[728488.0, 6430309.0] ...]]] |
| 79     | 34        | HERAULT                 | Polygon      | [[[664821.0, 6258302.0] ...]]] |
| 80     | 26        | DROME                   | Polygon      | [[[921863.0, 6404787.0] ...]]] |
| 81     | 66        | PYRENEES-ORIENTALES     | Polygon      | [[[600206.0, 6164532.0] ...]]] |
| 82     | 73        | SAVOIE                  | Polygon      | [[[956276.0, 6452799.0] ...]]] |
| 83     | 05        | HAUTES-ALPES            | Polygon      | [[[921863.0, 6404787.0] ...]]] |
| 84     | 84        | VAUCLUSE                | MultiPolygon | [[[[850837.0, 6364673. ...]]]] |
| 85     | 36        | INDRE                   | Polygon      | [[[636090.0, 6591904.0] ...]]] |
| 86     | 2B        | HAUTE-CORSE             | Polygon      | [[[1232225.0, 6105798.0 ...]]] |
| 87     | 87        | HAUTE-VIENNE            | Polygon      | [[[563452.0, 6484264.0] ...]]] |
| 88     | 85        | VENDEE                  | MultiPolygon | [[[[297360.0, 6667914. ...]]]] |
| 89     | 83        | VAR                     | Polygon      | [[[917346.0, 6234793.0] ...]]] |
| 90     | 94        | VAL-DE-MARNE            | Polygon      | [[[670056.0, 6856451.0] ...]]] |
| 91     | 92        | HAUTS-DE-SEINE          | Polygon      | [[[650942.0, 6857646.0] ...]]] |
| 92     | 48        | LOZERE                  | Polygon      | [[[698547.0, 6393953.0] ...]]] |
| 93     | 13        | BOUCHES-DU-RHONE        | Polygon      | [[[799607.0, 6263119.0] ...]]] |
| 94     | 75        | PARIS                   | Polygon      | [[[650942.0, 6857646.0] ...]]] |
| 95     | 93        | SEINE-SAINT-DENIS       | Polygon      | [[[670056.0, 6856451.0] ...]]] |
+--------+-----------+-------------------------+--------------+--------------------------------+
"""
    },
    1: {
        "geolayer": geolayer_fr_dept_data_only,
        "field_name_list": None,
        "print_i_feat": True,
        "table_type": 'RST',
        "light": True,
        "display_geometry": True,
        "max_width_coordinates_printing": 30,
        "header": True,
        "return_value": """+--------+-----------+-------------------------+
| i_feat | CODE_DEPT | NOM_DEPT                |
+========+===========+=========================+
| 0      | 32        | GERS                    |
| 1      | 47        | LOT-ET-GARONNE          |
| 2      | 38        | ISERE                   |
| 3      | 62        | PAS-DE-CALAIS           |
| 4      | 08        | ARDENNES                |
| 5      | 10        | AUBE                    |
| 6      | 06        | ALPES-MARITIMES         |
| 7      | 42        | LOIRE                   |
| 8      | 31        | HAUTE-GARONNE           |
| 9      | 71        | SAONE-ET-LOIRE          |
| 10     | 53        | MAYENNE                 |
| 11     | 16        | CHARENTE                |
| 12     | 50        | MANCHE                  |
| 13     | 78        | YVELINES                |
| 14     | 25        | DOUBS                   |
| 15     | 55        | MEUSE                   |
| 16     | 33        | GIRONDE                 |
| 17     | 14        | CALVADOS                |
| 18     | 88        | VOSGES                  |
| 19     | 18        | CHER                    |
| 20     | 07        | ARDECHE                 |
| 21     | 02        | AISNE                   |
| 22     | 64        | PYRENEES-ATLANTIQUES    |
| 23     | 41        | LOIR-ET-CHER            |
| 24     | 57        | MOSELLE                 |
| 25     | 86        | VIENNE                  |
| 26     | 24        | DORDOGNE                |
| 27     | 39        | JURA                    |
| 28     | 82        | TARN-ET-GARONNE         |
| 29     | 49        | MAINE-ET-LOIRE          |
| 30     | 69        | RHONE                   |
| 31     | 27        | EURE                    |
| 32     | 12        | AVEYRON                 |
| 33     | 23        | CREUSE                  |
| 34     | 45        | LOIRET                  |
| 35     | 70        | HAUTE-SAONE             |
| 36     | 63        | PUY-DE-DOME             |
| 37     | 81        | TARN                    |
| 38     | 76        | SEINE-MARITIME          |
| 39     | 52        | HAUTE-MARNE             |
| 40     | 30        | GARD                    |
| 41     | 67        | BAS-RHIN                |
| 42     | 11        | AUDE                    |
| 43     | 77        | SEINE-ET-MARNE          |
| 44     | 80        | SOMME                   |
| 45     | 43        | HAUTE-LOIRE             |
| 46     | 51        | MARNE                   |
| 47     | 65        | HAUTES-PYRENEES         |
| 48     | 46        | LOT                     |
| 49     | 04        | ALPES-DE-HAUTE-PROVENCE |
| 50     | 72        | SARTHE                  |
| 51     | 56        | MORBIHAN                |
| 52     | 28        | EURE-ET-LOIR            |
| 53     | 2A        | CORSE-DU-SUD            |
| 54     | 54        | MEURTHE-ET-MOSELLE      |
| 55     | 61        | ORNE                    |
| 56     | 01        | AIN                     |
| 57     | 09        | ARIEGE                  |
| 58     | 19        | CORREZE                 |
| 59     | 68        | HAUT-RHIN               |
| 60     | 37        | INDRE-ET-LOIRE          |
| 61     | 59        | NORD                    |
| 62     | 90        | TERRITOIRE DE BELFORT   |
| 63     | 44        | LOIRE-ATLANTIQUE        |
| 64     | 89        | YONNE                   |
| 65     | 35        | ILLE-ET-VILAINE         |
| 66     | 40        | LANDES                  |
| 67     | 29        | FINISTERE               |
| 68     | 74        | HAUTE-SAVOIE            |
| 69     | 60        | OISE                    |
| 70     | 95        | VAL-D'OISE              |
| 71     | 58        | NIEVRE                  |
| 72     | 21        | COTE-D'OR               |
| 73     | 91        | ESSONNE                 |
| 74     | 79        | DEUX-SEVRES             |
| 75     | 22        | COTES-D'ARMOR           |
| 76     | 03        | ALLIER                  |
| 77     | 17        | CHARENTE-MARITIME       |
| 78     | 15        | CANTAL                  |
| 79     | 34        | HERAULT                 |
| 80     | 26        | DROME                   |
| 81     | 66        | PYRENEES-ORIENTALES     |
| 82     | 73        | SAVOIE                  |
| 83     | 05        | HAUTES-ALPES            |
| 84     | 84        | VAUCLUSE                |
| 85     | 36        | INDRE                   |
| 86     | 2B        | HAUTE-CORSE             |
| 87     | 87        | HAUTE-VIENNE            |
| 88     | 85        | VENDEE                  |
| 89     | 83        | VAR                     |
| 90     | 94        | VAL-DE-MARNE            |
| 91     | 92        | HAUTS-DE-SEINE          |
| 92     | 48        | LOZERE                  |
| 93     | 13        | BOUCHES-DU-RHONE        |
| 94     | 75        | PARIS                   |
| 95     | 93        | SEINE-SAINT-DENIS       |
+--------+-----------+-------------------------+
"""
    },
    2: {
        "geolayer": geolayer_fr_dept_geometry_only,
        "field_name_list": None,
        "print_i_feat": True,
        "table_type": 'RST',
        "light": True,
        "display_geometry": True,
        "max_width_coordinates_printing": 30,
        "header": True,
        "return_value": """+--------+--------------+--------------------------------+
| i_feat | type         | coordinates                    |
+========+==============+================================+
| 0      | Polygon      | [[[505760.0, 6248691.0] ...]]] |
| 1      | Polygon      | [[[547193.0, 6388334.0] ...]]] |
| 2      | Polygon      | [[[841110.0, 6468164.0] ...]]] |
| 3      | Polygon      | [[[634422.0, 7101577.0] ...]]] |
| 4      | Polygon      | [[[776081.0, 6923412.0] ...]]] |
| 5      | Polygon      | [[[730707.0, 6810078.0] ...]]] |
| 6      | Polygon      | [[[1009696.0, 6370071.0 ...]]] |
| 7      | Polygon      | [[[753779.0, 6537018.0] ...]]] |
| 8      | Polygon      | [[[505760.0, 6248691.0] ...]]] |
| 9      | Polygon      | [[[806993.0, 6569822.0] ...]]] |
| 10     | Polygon      | [[[399495.0, 6830885.0] ...]]] |
| 11     | Polygon      | [[[459784.0, 6545825.0] ...]]] |
| 12     | Polygon      | [[[417723.0, 6857101.0] ...]]] |
| 13     | Polygon      | [[[590236.0, 6872273.0] ...]]] |
| 14     | Polygon      | [[[986155.0, 6724947.0] ...]]] |
| 15     | Polygon      | [[[904250.0, 6825381.0] ...]]] |
| 16     | Polygon      | [[[486169.0, 6410676.0] ...]]] |
| 17     | Polygon      | [[[503908.0, 6928958.0] ...]]] |
| 18     | Polygon      | [[[915394.0, 6762341.0] ...]]] |
| 19     | Polygon      | [[[642856.0, 6724786.0] ...]]] |
| 20     | Polygon      | [[[779411.0, 6373918.0] ...]]] |
| 21     | Polygon      | [[[776081.0, 6923412.0] ...]]] |
| 22     | Polygon      | [[[334283.0, 6280551.0] ...]]] |
| 23     | Polygon      | [[[642856.0, 6724786.0] ...]]] |
| 24     | Polygon      | [[[1001023.0, 6834020.0 ...]]] |
| 25     | Polygon      | [[[483517.0, 6558927.0] ...]]] |
| 26     | Polygon      | [[[515635.0, 6515544.0] ...]]] |
| 27     | Polygon      | [[[877344.0, 6596683.0] ...]]] |
| 28     | Polygon      | [[[610874.0, 6360746.0] ...]]] |
| 29     | Polygon      | [[[404251.0, 6660135.0] ...]]] |
| 30     | Polygon      | [[[863140.0, 6525920.0] ...]]] |
| 31     | Polygon      | [[[606642.0, 6924066.0] ...]]] |
| 32     | Polygon      | [[[619220.0, 6339455.0] ...]]] |
| 33     | Polygon      | [[[636090.0, 6591904.0] ...]]] |
| 34     | Polygon      | [[[695265.0, 6784783.0] ...]]] |
| 35     | Polygon      | [[[986052.0, 6752778.0] ...]]] |
| 36     | Polygon      | [[[753779.0, 6537018.0] ...]]] |
| 37     | Polygon      | [[[583992.0, 6314318.0] ...]]] |
| 38     | Polygon      | [[[612314.0, 6962826.0] ...]]] |
| 39     | Polygon      | [[[823302.0, 6827043.0] ...]]] |
| 40     | Polygon      | [[[831641.0, 6353746.0] ...]]] |
| 41     | Polygon      | [[[1011125.0, 6809400.0 ...]]] |
| 42     | Polygon      | [[[719561.0, 6234874.0] ...]]] |
| 43     | Polygon      | [[[695265.0, 6784783.0] ...]]] |
| 44     | Polygon      | [[[706470.0, 6995042.0] ...]]] |
| 45     | Polygon      | [[[708104.0, 6472781.0] ...]]] |
| 46     | Polygon      | [[[776081.0, 6923412.0] ...]]] |
| 47     | Polygon      | [[[428954.0, 6200122.0] ...]]] |
| 48     | Polygon      | [[[547193.0, 6388334.0] ...]]] |
| 49     | Polygon      | [[[992638.0, 6305621.0] ...]]] |
| 50     | Polygon      | [[[521086.0, 6735350.0] ...]]] |
| 51     | MultiPolygon | [[[[229520.0, 6710085. ...]]]] |
| 52     | Polygon      | [[[539112.0, 6843338.0] ...]]] |
| 53     | Polygon      | [[[1232225.0, 6105798.0 ...]]] |
| 54     | Polygon      | [[[879041.0, 6935896.0] ...]]] |
| 55     | Polygon      | [[[510545.0, 6875400.0] ...]]] |
| 56     | Polygon      | [[[877344.0, 6596683.0] ...]]] |
| 57     | Polygon      | [[[524704.0, 6194181.0] ...]]] |
| 58     | Polygon      | [[[563452.0, 6484264.0] ...]]] |
| 59     | Polygon      | [[[987691.0, 6753958.0] ...]]] |
| 60     | Polygon      | [[[573297.0, 6677558.0] ...]]] |
| 61     | Polygon      | [[[634422.0, 7101577.0] ...]]] |
| 62     | Polygon      | [[[1010786.0, 6719537.0 ...]]] |
| 63     | Polygon      | [[[382163.0, 6750361.0] ...]]] |
| 64     | Polygon      | [[[698236.0, 6718784.0] ...]]] |
| 65     | MultiPolygon | [[[[330825.0, 6841252. ...]]]] |
| 66     | Polygon      | [[[334283.0, 6280551.0] ...]]] |
| 67     | Polygon      | [[[210124.0, 6860562.0] ...]]] |
| 68     | Polygon      | [[[995359.0, 6526975.0] ...]]] |
| 69     | Polygon      | [[[605624.0, 6904387.0] ...]]] |
| 70     | Polygon      | [[[598361.0, 6887345.0] ...]]] |
| 71     | Polygon      | [[[783517.0, 6693799.0] ...]]] |
| 72     | Polygon      | [[[871408.0, 6655745.0] ...]]] |
| 73     | Polygon      | [[[643163.0, 6853168.0] ...]]] |
| 74     | Polygon      | [[[483517.0, 6558927.0] ...]]] |
| 75     | Polygon      | [[[306966.0, 6794650.0] ...]]] |
| 76     | Polygon      | [[[702446.0, 6632753.0] ...]]] |
| 77     | MultiPolygon | [[[[365341.0, 6575902. ...]]]] |
| 78     | Polygon      | [[[728488.0, 6430309.0] ...]]] |
| 79     | Polygon      | [[[664821.0, 6258302.0] ...]]] |
| 80     | Polygon      | [[[921863.0, 6404787.0] ...]]] |
| 81     | Polygon      | [[[600206.0, 6164532.0] ...]]] |
| 82     | Polygon      | [[[956276.0, 6452799.0] ...]]] |
| 83     | Polygon      | [[[921863.0, 6404787.0] ...]]] |
| 84     | MultiPolygon | [[[[850837.0, 6364673. ...]]]] |
| 85     | Polygon      | [[[636090.0, 6591904.0] ...]]] |
| 86     | Polygon      | [[[1232225.0, 6105798.0 ...]]] |
| 87     | Polygon      | [[[563452.0, 6484264.0] ...]]] |
| 88     | MultiPolygon | [[[[297360.0, 6667914. ...]]]] |
| 89     | Polygon      | [[[917346.0, 6234793.0] ...]]] |
| 90     | Polygon      | [[[670056.0, 6856451.0] ...]]] |
| 91     | Polygon      | [[[650942.0, 6857646.0] ...]]] |
| 92     | Polygon      | [[[698547.0, 6393953.0] ...]]] |
| 93     | Polygon      | [[[799607.0, 6263119.0] ...]]] |
| 94     | Polygon      | [[[650942.0, 6857646.0] ...]]] |
| 95     | Polygon      | [[[670056.0, 6856451.0] ...]]] |
+--------+--------------+--------------------------------+
"""
    },
    3: {
        "geolayer": geolayer_fr_dept_data_and_geometry,
        "field_name_list": ['NOM_DEPT'],
        "print_i_feat": True,
        "table_type": 'RST',
        "light": True,
        "display_geometry": True,
        "max_width_coordinates_printing": 30,
        "header": True,
        "return_value": """+--------+-------------------------+--------------+--------------------------------+
| i_feat | NOM_DEPT                | type         | coordinates                    |
+========+=========================+==============+================================+
| 0      | GERS                    | Polygon      | [[[505760.0, 6248691.0] ...]]] |
| 1      | LOT-ET-GARONNE          | Polygon      | [[[547193.0, 6388334.0] ...]]] |
| 2      | ISERE                   | Polygon      | [[[841110.0, 6468164.0] ...]]] |
| 3      | PAS-DE-CALAIS           | Polygon      | [[[634422.0, 7101577.0] ...]]] |
| 4      | ARDENNES                | Polygon      | [[[776081.0, 6923412.0] ...]]] |
| 5      | AUBE                    | Polygon      | [[[730707.0, 6810078.0] ...]]] |
| 6      | ALPES-MARITIMES         | Polygon      | [[[1009696.0, 6370071.0 ...]]] |
| 7      | LOIRE                   | Polygon      | [[[753779.0, 6537018.0] ...]]] |
| 8      | HAUTE-GARONNE           | Polygon      | [[[505760.0, 6248691.0] ...]]] |
| 9      | SAONE-ET-LOIRE          | Polygon      | [[[806993.0, 6569822.0] ...]]] |
| 10     | MAYENNE                 | Polygon      | [[[399495.0, 6830885.0] ...]]] |
| 11     | CHARENTE                | Polygon      | [[[459784.0, 6545825.0] ...]]] |
| 12     | MANCHE                  | Polygon      | [[[417723.0, 6857101.0] ...]]] |
| 13     | YVELINES                | Polygon      | [[[590236.0, 6872273.0] ...]]] |
| 14     | DOUBS                   | Polygon      | [[[986155.0, 6724947.0] ...]]] |
| 15     | MEUSE                   | Polygon      | [[[904250.0, 6825381.0] ...]]] |
| 16     | GIRONDE                 | Polygon      | [[[486169.0, 6410676.0] ...]]] |
| 17     | CALVADOS                | Polygon      | [[[503908.0, 6928958.0] ...]]] |
| 18     | VOSGES                  | Polygon      | [[[915394.0, 6762341.0] ...]]] |
| 19     | CHER                    | Polygon      | [[[642856.0, 6724786.0] ...]]] |
| 20     | ARDECHE                 | Polygon      | [[[779411.0, 6373918.0] ...]]] |
| 21     | AISNE                   | Polygon      | [[[776081.0, 6923412.0] ...]]] |
| 22     | PYRENEES-ATLANTIQUES    | Polygon      | [[[334283.0, 6280551.0] ...]]] |
| 23     | LOIR-ET-CHER            | Polygon      | [[[642856.0, 6724786.0] ...]]] |
| 24     | MOSELLE                 | Polygon      | [[[1001023.0, 6834020.0 ...]]] |
| 25     | VIENNE                  | Polygon      | [[[483517.0, 6558927.0] ...]]] |
| 26     | DORDOGNE                | Polygon      | [[[515635.0, 6515544.0] ...]]] |
| 27     | JURA                    | Polygon      | [[[877344.0, 6596683.0] ...]]] |
| 28     | TARN-ET-GARONNE         | Polygon      | [[[610874.0, 6360746.0] ...]]] |
| 29     | MAINE-ET-LOIRE          | Polygon      | [[[404251.0, 6660135.0] ...]]] |
| 30     | RHONE                   | Polygon      | [[[863140.0, 6525920.0] ...]]] |
| 31     | EURE                    | Polygon      | [[[606642.0, 6924066.0] ...]]] |
| 32     | AVEYRON                 | Polygon      | [[[619220.0, 6339455.0] ...]]] |
| 33     | CREUSE                  | Polygon      | [[[636090.0, 6591904.0] ...]]] |
| 34     | LOIRET                  | Polygon      | [[[695265.0, 6784783.0] ...]]] |
| 35     | HAUTE-SAONE             | Polygon      | [[[986052.0, 6752778.0] ...]]] |
| 36     | PUY-DE-DOME             | Polygon      | [[[753779.0, 6537018.0] ...]]] |
| 37     | TARN                    | Polygon      | [[[583992.0, 6314318.0] ...]]] |
| 38     | SEINE-MARITIME          | Polygon      | [[[612314.0, 6962826.0] ...]]] |
| 39     | HAUTE-MARNE             | Polygon      | [[[823302.0, 6827043.0] ...]]] |
| 40     | GARD                    | Polygon      | [[[831641.0, 6353746.0] ...]]] |
| 41     | BAS-RHIN                | Polygon      | [[[1011125.0, 6809400.0 ...]]] |
| 42     | AUDE                    | Polygon      | [[[719561.0, 6234874.0] ...]]] |
| 43     | SEINE-ET-MARNE          | Polygon      | [[[695265.0, 6784783.0] ...]]] |
| 44     | SOMME                   | Polygon      | [[[706470.0, 6995042.0] ...]]] |
| 45     | HAUTE-LOIRE             | Polygon      | [[[708104.0, 6472781.0] ...]]] |
| 46     | MARNE                   | Polygon      | [[[776081.0, 6923412.0] ...]]] |
| 47     | HAUTES-PYRENEES         | Polygon      | [[[428954.0, 6200122.0] ...]]] |
| 48     | LOT                     | Polygon      | [[[547193.0, 6388334.0] ...]]] |
| 49     | ALPES-DE-HAUTE-PROVENCE | Polygon      | [[[992638.0, 6305621.0] ...]]] |
| 50     | SARTHE                  | Polygon      | [[[521086.0, 6735350.0] ...]]] |
| 51     | MORBIHAN                | MultiPolygon | [[[[229520.0, 6710085. ...]]]] |
| 52     | EURE-ET-LOIR            | Polygon      | [[[539112.0, 6843338.0] ...]]] |
| 53     | CORSE-DU-SUD            | Polygon      | [[[1232225.0, 6105798.0 ...]]] |
| 54     | MEURTHE-ET-MOSELLE      | Polygon      | [[[879041.0, 6935896.0] ...]]] |
| 55     | ORNE                    | Polygon      | [[[510545.0, 6875400.0] ...]]] |
| 56     | AIN                     | Polygon      | [[[877344.0, 6596683.0] ...]]] |
| 57     | ARIEGE                  | Polygon      | [[[524704.0, 6194181.0] ...]]] |
| 58     | CORREZE                 | Polygon      | [[[563452.0, 6484264.0] ...]]] |
| 59     | HAUT-RHIN               | Polygon      | [[[987691.0, 6753958.0] ...]]] |
| 60     | INDRE-ET-LOIRE          | Polygon      | [[[573297.0, 6677558.0] ...]]] |
| 61     | NORD                    | Polygon      | [[[634422.0, 7101577.0] ...]]] |
| 62     | TERRITOIRE DE BELFORT   | Polygon      | [[[1010786.0, 6719537.0 ...]]] |
| 63     | LOIRE-ATLANTIQUE        | Polygon      | [[[382163.0, 6750361.0] ...]]] |
| 64     | YONNE                   | Polygon      | [[[698236.0, 6718784.0] ...]]] |
| 65     | ILLE-ET-VILAINE         | MultiPolygon | [[[[330825.0, 6841252. ...]]]] |
| 66     | LANDES                  | Polygon      | [[[334283.0, 6280551.0] ...]]] |
| 67     | FINISTERE               | Polygon      | [[[210124.0, 6860562.0] ...]]] |
| 68     | HAUTE-SAVOIE            | Polygon      | [[[995359.0, 6526975.0] ...]]] |
| 69     | OISE                    | Polygon      | [[[605624.0, 6904387.0] ...]]] |
| 70     | VAL-D'OISE              | Polygon      | [[[598361.0, 6887345.0] ...]]] |
| 71     | NIEVRE                  | Polygon      | [[[783517.0, 6693799.0] ...]]] |
| 72     | COTE-D'OR               | Polygon      | [[[871408.0, 6655745.0] ...]]] |
| 73     | ESSONNE                 | Polygon      | [[[643163.0, 6853168.0] ...]]] |
| 74     | DEUX-SEVRES             | Polygon      | [[[483517.0, 6558927.0] ...]]] |
| 75     | COTES-D'ARMOR           | Polygon      | [[[306966.0, 6794650.0] ...]]] |
| 76     | ALLIER                  | Polygon      | [[[702446.0, 6632753.0] ...]]] |
| 77     | CHARENTE-MARITIME       | MultiPolygon | [[[[365341.0, 6575902. ...]]]] |
| 78     | CANTAL                  | Polygon      | [[[728488.0, 6430309.0] ...]]] |
| 79     | HERAULT                 | Polygon      | [[[664821.0, 6258302.0] ...]]] |
| 80     | DROME                   | Polygon      | [[[921863.0, 6404787.0] ...]]] |
| 81     | PYRENEES-ORIENTALES     | Polygon      | [[[600206.0, 6164532.0] ...]]] |
| 82     | SAVOIE                  | Polygon      | [[[956276.0, 6452799.0] ...]]] |
| 83     | HAUTES-ALPES            | Polygon      | [[[921863.0, 6404787.0] ...]]] |
| 84     | VAUCLUSE                | MultiPolygon | [[[[850837.0, 6364673. ...]]]] |
| 85     | INDRE                   | Polygon      | [[[636090.0, 6591904.0] ...]]] |
| 86     | HAUTE-CORSE             | Polygon      | [[[1232225.0, 6105798.0 ...]]] |
| 87     | HAUTE-VIENNE            | Polygon      | [[[563452.0, 6484264.0] ...]]] |
| 88     | VENDEE                  | MultiPolygon | [[[[297360.0, 6667914. ...]]]] |
| 89     | VAR                     | Polygon      | [[[917346.0, 6234793.0] ...]]] |
| 90     | VAL-DE-MARNE            | Polygon      | [[[670056.0, 6856451.0] ...]]] |
| 91     | HAUTS-DE-SEINE          | Polygon      | [[[650942.0, 6857646.0] ...]]] |
| 92     | LOZERE                  | Polygon      | [[[698547.0, 6393953.0] ...]]] |
| 93     | BOUCHES-DU-RHONE        | Polygon      | [[[799607.0, 6263119.0] ...]]] |
| 94     | PARIS                   | Polygon      | [[[650942.0, 6857646.0] ...]]] |
| 95     | SEINE-SAINT-DENIS       | Polygon      | [[[670056.0, 6856451.0] ...]]] |
+--------+-------------------------+--------------+--------------------------------+
"""
    },
    4: {
        "geolayer": geolayer_fr_dept_data_only,
        "field_name_list": ['NOM_DEPT'],
        "print_i_feat": True,
        "table_type": 'RST',
        "light": True,
        "display_geometry": True,
        "max_width_coordinates_printing": 30,
        "header": True,
        "return_value": """+--------+-------------------------+
| i_feat | NOM_DEPT                |
+========+=========================+
| 0      | GERS                    |
| 1      | LOT-ET-GARONNE          |
| 2      | ISERE                   |
| 3      | PAS-DE-CALAIS           |
| 4      | ARDENNES                |
| 5      | AUBE                    |
| 6      | ALPES-MARITIMES         |
| 7      | LOIRE                   |
| 8      | HAUTE-GARONNE           |
| 9      | SAONE-ET-LOIRE          |
| 10     | MAYENNE                 |
| 11     | CHARENTE                |
| 12     | MANCHE                  |
| 13     | YVELINES                |
| 14     | DOUBS                   |
| 15     | MEUSE                   |
| 16     | GIRONDE                 |
| 17     | CALVADOS                |
| 18     | VOSGES                  |
| 19     | CHER                    |
| 20     | ARDECHE                 |
| 21     | AISNE                   |
| 22     | PYRENEES-ATLANTIQUES    |
| 23     | LOIR-ET-CHER            |
| 24     | MOSELLE                 |
| 25     | VIENNE                  |
| 26     | DORDOGNE                |
| 27     | JURA                    |
| 28     | TARN-ET-GARONNE         |
| 29     | MAINE-ET-LOIRE          |
| 30     | RHONE                   |
| 31     | EURE                    |
| 32     | AVEYRON                 |
| 33     | CREUSE                  |
| 34     | LOIRET                  |
| 35     | HAUTE-SAONE             |
| 36     | PUY-DE-DOME             |
| 37     | TARN                    |
| 38     | SEINE-MARITIME          |
| 39     | HAUTE-MARNE             |
| 40     | GARD                    |
| 41     | BAS-RHIN                |
| 42     | AUDE                    |
| 43     | SEINE-ET-MARNE          |
| 44     | SOMME                   |
| 45     | HAUTE-LOIRE             |
| 46     | MARNE                   |
| 47     | HAUTES-PYRENEES         |
| 48     | LOT                     |
| 49     | ALPES-DE-HAUTE-PROVENCE |
| 50     | SARTHE                  |
| 51     | MORBIHAN                |
| 52     | EURE-ET-LOIR            |
| 53     | CORSE-DU-SUD            |
| 54     | MEURTHE-ET-MOSELLE      |
| 55     | ORNE                    |
| 56     | AIN                     |
| 57     | ARIEGE                  |
| 58     | CORREZE                 |
| 59     | HAUT-RHIN               |
| 60     | INDRE-ET-LOIRE          |
| 61     | NORD                    |
| 62     | TERRITOIRE DE BELFORT   |
| 63     | LOIRE-ATLANTIQUE        |
| 64     | YONNE                   |
| 65     | ILLE-ET-VILAINE         |
| 66     | LANDES                  |
| 67     | FINISTERE               |
| 68     | HAUTE-SAVOIE            |
| 69     | OISE                    |
| 70     | VAL-D'OISE              |
| 71     | NIEVRE                  |
| 72     | COTE-D'OR               |
| 73     | ESSONNE                 |
| 74     | DEUX-SEVRES             |
| 75     | COTES-D'ARMOR           |
| 76     | ALLIER                  |
| 77     | CHARENTE-MARITIME       |
| 78     | CANTAL                  |
| 79     | HERAULT                 |
| 80     | DROME                   |
| 81     | PYRENEES-ORIENTALES     |
| 82     | SAVOIE                  |
| 83     | HAUTES-ALPES            |
| 84     | VAUCLUSE                |
| 85     | INDRE                   |
| 86     | HAUTE-CORSE             |
| 87     | HAUTE-VIENNE            |
| 88     | VENDEE                  |
| 89     | VAR                     |
| 90     | VAL-DE-MARNE            |
| 91     | HAUTS-DE-SEINE          |
| 92     | LOZERE                  |
| 93     | BOUCHES-DU-RHONE        |
| 94     | PARIS                   |
| 95     | SEINE-SAINT-DENIS       |
+--------+-------------------------+
"""
    },
    5: {
        "geolayer": geolayer_fr_dept_geometry_only,
        "field_name_list": ['NOM_DEPT'],
        "print_i_feat": True,
        "table_type": 'RST',
        "light": True,
        "display_geometry": True,
        "max_width_coordinates_printing": 30,
        "header": True,
        "return_value": """+--------+--------------+--------------------------------+
| i_feat | NOM_DEPT     | type                           |
+========+==============+================================+
| 0      | Polygon      | [[[505760.0, 6248691.0] ...]]] |
| 1      | Polygon      | [[[547193.0, 6388334.0] ...]]] |
| 2      | Polygon      | [[[841110.0, 6468164.0] ...]]] |
| 3      | Polygon      | [[[634422.0, 7101577.0] ...]]] |
| 4      | Polygon      | [[[776081.0, 6923412.0] ...]]] |
| 5      | Polygon      | [[[730707.0, 6810078.0] ...]]] |
| 6      | Polygon      | [[[1009696.0, 6370071.0 ...]]] |
| 7      | Polygon      | [[[753779.0, 6537018.0] ...]]] |
| 8      | Polygon      | [[[505760.0, 6248691.0] ...]]] |
| 9      | Polygon      | [[[806993.0, 6569822.0] ...]]] |
| 10     | Polygon      | [[[399495.0, 6830885.0] ...]]] |
| 11     | Polygon      | [[[459784.0, 6545825.0] ...]]] |
| 12     | Polygon      | [[[417723.0, 6857101.0] ...]]] |
| 13     | Polygon      | [[[590236.0, 6872273.0] ...]]] |
| 14     | Polygon      | [[[986155.0, 6724947.0] ...]]] |
| 15     | Polygon      | [[[904250.0, 6825381.0] ...]]] |
| 16     | Polygon      | [[[486169.0, 6410676.0] ...]]] |
| 17     | Polygon      | [[[503908.0, 6928958.0] ...]]] |
| 18     | Polygon      | [[[915394.0, 6762341.0] ...]]] |
| 19     | Polygon      | [[[642856.0, 6724786.0] ...]]] |
| 20     | Polygon      | [[[779411.0, 6373918.0] ...]]] |
| 21     | Polygon      | [[[776081.0, 6923412.0] ...]]] |
| 22     | Polygon      | [[[334283.0, 6280551.0] ...]]] |
| 23     | Polygon      | [[[642856.0, 6724786.0] ...]]] |
| 24     | Polygon      | [[[1001023.0, 6834020.0 ...]]] |
| 25     | Polygon      | [[[483517.0, 6558927.0] ...]]] |
| 26     | Polygon      | [[[515635.0, 6515544.0] ...]]] |
| 27     | Polygon      | [[[877344.0, 6596683.0] ...]]] |
| 28     | Polygon      | [[[610874.0, 6360746.0] ...]]] |
| 29     | Polygon      | [[[404251.0, 6660135.0] ...]]] |
| 30     | Polygon      | [[[863140.0, 6525920.0] ...]]] |
| 31     | Polygon      | [[[606642.0, 6924066.0] ...]]] |
| 32     | Polygon      | [[[619220.0, 6339455.0] ...]]] |
| 33     | Polygon      | [[[636090.0, 6591904.0] ...]]] |
| 34     | Polygon      | [[[695265.0, 6784783.0] ...]]] |
| 35     | Polygon      | [[[986052.0, 6752778.0] ...]]] |
| 36     | Polygon      | [[[753779.0, 6537018.0] ...]]] |
| 37     | Polygon      | [[[583992.0, 6314318.0] ...]]] |
| 38     | Polygon      | [[[612314.0, 6962826.0] ...]]] |
| 39     | Polygon      | [[[823302.0, 6827043.0] ...]]] |
| 40     | Polygon      | [[[831641.0, 6353746.0] ...]]] |
| 41     | Polygon      | [[[1011125.0, 6809400.0 ...]]] |
| 42     | Polygon      | [[[719561.0, 6234874.0] ...]]] |
| 43     | Polygon      | [[[695265.0, 6784783.0] ...]]] |
| 44     | Polygon      | [[[706470.0, 6995042.0] ...]]] |
| 45     | Polygon      | [[[708104.0, 6472781.0] ...]]] |
| 46     | Polygon      | [[[776081.0, 6923412.0] ...]]] |
| 47     | Polygon      | [[[428954.0, 6200122.0] ...]]] |
| 48     | Polygon      | [[[547193.0, 6388334.0] ...]]] |
| 49     | Polygon      | [[[992638.0, 6305621.0] ...]]] |
| 50     | Polygon      | [[[521086.0, 6735350.0] ...]]] |
| 51     | MultiPolygon | [[[[229520.0, 6710085. ...]]]] |
| 52     | Polygon      | [[[539112.0, 6843338.0] ...]]] |
| 53     | Polygon      | [[[1232225.0, 6105798.0 ...]]] |
| 54     | Polygon      | [[[879041.0, 6935896.0] ...]]] |
| 55     | Polygon      | [[[510545.0, 6875400.0] ...]]] |
| 56     | Polygon      | [[[877344.0, 6596683.0] ...]]] |
| 57     | Polygon      | [[[524704.0, 6194181.0] ...]]] |
| 58     | Polygon      | [[[563452.0, 6484264.0] ...]]] |
| 59     | Polygon      | [[[987691.0, 6753958.0] ...]]] |
| 60     | Polygon      | [[[573297.0, 6677558.0] ...]]] |
| 61     | Polygon      | [[[634422.0, 7101577.0] ...]]] |
| 62     | Polygon      | [[[1010786.0, 6719537.0 ...]]] |
| 63     | Polygon      | [[[382163.0, 6750361.0] ...]]] |
| 64     | Polygon      | [[[698236.0, 6718784.0] ...]]] |
| 65     | MultiPolygon | [[[[330825.0, 6841252. ...]]]] |
| 66     | Polygon      | [[[334283.0, 6280551.0] ...]]] |
| 67     | Polygon      | [[[210124.0, 6860562.0] ...]]] |
| 68     | Polygon      | [[[995359.0, 6526975.0] ...]]] |
| 69     | Polygon      | [[[605624.0, 6904387.0] ...]]] |
| 70     | Polygon      | [[[598361.0, 6887345.0] ...]]] |
| 71     | Polygon      | [[[783517.0, 6693799.0] ...]]] |
| 72     | Polygon      | [[[871408.0, 6655745.0] ...]]] |
| 73     | Polygon      | [[[643163.0, 6853168.0] ...]]] |
| 74     | Polygon      | [[[483517.0, 6558927.0] ...]]] |
| 75     | Polygon      | [[[306966.0, 6794650.0] ...]]] |
| 76     | Polygon      | [[[702446.0, 6632753.0] ...]]] |
| 77     | MultiPolygon | [[[[365341.0, 6575902. ...]]]] |
| 78     | Polygon      | [[[728488.0, 6430309.0] ...]]] |
| 79     | Polygon      | [[[664821.0, 6258302.0] ...]]] |
| 80     | Polygon      | [[[921863.0, 6404787.0] ...]]] |
| 81     | Polygon      | [[[600206.0, 6164532.0] ...]]] |
| 82     | Polygon      | [[[956276.0, 6452799.0] ...]]] |
| 83     | Polygon      | [[[921863.0, 6404787.0] ...]]] |
| 84     | MultiPolygon | [[[[850837.0, 6364673. ...]]]] |
| 85     | Polygon      | [[[636090.0, 6591904.0] ...]]] |
| 86     | Polygon      | [[[1232225.0, 6105798.0 ...]]] |
| 87     | Polygon      | [[[563452.0, 6484264.0] ...]]] |
| 88     | MultiPolygon | [[[[297360.0, 6667914. ...]]]] |
| 89     | Polygon      | [[[917346.0, 6234793.0] ...]]] |
| 90     | Polygon      | [[[670056.0, 6856451.0] ...]]] |
| 91     | Polygon      | [[[650942.0, 6857646.0] ...]]] |
| 92     | Polygon      | [[[698547.0, 6393953.0] ...]]] |
| 93     | Polygon      | [[[799607.0, 6263119.0] ...]]] |
| 94     | Polygon      | [[[650942.0, 6857646.0] ...]]] |
| 95     | Polygon      | [[[670056.0, 6856451.0] ...]]] |
+--------+--------------+--------------------------------+
"""
    }
}


print_metadata_field_table_parameters = {
    0: {
        "geolayer": geolayer_fr_dept_data_and_geometry,
        "field_name_list": None,
        "key_field_name":'field name',
        "order_value": False,
        "table_type": 'RST',
        "light": True,
        "header": True,
        "return_value": """+------------+--------+-------+-----------+-------+
| field name | type   | width | precision | index |
+============+========+=======+===========+=======+
| CODE_DEPT  | String | 2     | None      | 0     |
| NOM_DEPT   | String | 23    | None      | 1     |
+------------+--------+-------+-----------+-------+
"""
    },
}


def test_all():

    # _get_features_data_table_line
    print(test_function(_get_features_data_table_line, get_features_data_table_line_parameters))

    # _get_fields_metadata_table_line
    print(test_function(_get_fields_metadata_table_line, get_fields_metadata_table_line_parameters))

    # print_features_data_table
    print(test_function(print_features_data_table, print_features_data_table_parameters))

    # print_metadata_field_table
    print(test_function(print_metadata_field_table, print_metadata_field_table_parameters))


if __name__ == '__main__':
    test_all()

