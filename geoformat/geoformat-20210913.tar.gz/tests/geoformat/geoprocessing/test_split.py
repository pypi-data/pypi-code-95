
from test_all import test_function


from geoformat.geoprocessing.split import (
    segment_split_by_point,
    linestring_split_by_point
)

from tests.data.segments import (
    segment_a,
    segment_g,
    segment_h
)

segment_split_by_point_parameters = {
    0: {
        "segment": segment_a,
        "point": [-5, -5],
        "tolerance": None,
        "return_value": ()
    },
    1: {
        "segment": segment_a,
        "point": [0, 0],
        "tolerance": None,
        "return_value": ()
    },
    2: {
        "segment": segment_a,
        "point": [0, 1],
        "tolerance": None,
        "return_value": ()
    },
    3: {
        "segment": segment_a,
        "point": [0, 0.5],
        "tolerance": None,
        "return_value": (([0, 0], [0, 0.5]), ([0, 0.5], [0, 1]))
    },
    4: {
        "segment": segment_h,
        "point": [-5, -5],
        "tolerance": None,
        "return_value": ()
    },
    5: {
        "segment": segment_h,
        "point": [-1, -1],
        "tolerance": None,
        "return_value": ()
    },
    6: {
        "segment": segment_h,
        "point": [-1, 1],
        "tolerance": None,
        "return_value": ()
    },
    7: {
        "segment": segment_h,
        "point": [-1, 0],
        "tolerance": None,
        "return_value": (([-1, -1], [-1, 0]), ([-1, 0], [-1, 1]))
    },
    8: {
        "segment": segment_g,
        "point": [-5, -5],
        "tolerance": None,
        "return_value": ()
    },
    9: {
        "segment": segment_g,
        "point": [1, -1],
        "tolerance": None,
        "return_value": ()
    },
    10: {
        "segment": segment_g,
        "point": [-1, 1],
        "tolerance": None,
        "return_value": ()
    },
    11: {
        "segment": segment_g,
        "point": [0, 0],
        "tolerance": None,
        "return_value": (([1, -1], [0, 0]), ([0, 0], [-1, 1]))
    },
    12: {
        "segment": segment_a,
        "point": [0.1, 0.5],
        "tolerance": 0.1,
        "return_value": (([0, 0], [0.1, 0.5]), ([0.1, 0.5], [0, 1]))
    },
    13: {
        "segment": segment_a,
        "point": [0.1, 0.45],
        "tolerance": 0.01,
        "return_value": ()
    },
    14: {
        "segment": segment_g,
        "point": [1, -0.9],
        "tolerance": 0.1,
        "return_value": ()
    },
    15: {
        "segment": segment_g,
        "point": [1, -0.9],
        "tolerance": 0.01,
        "return_value": ()
    },
    16: {
        "segment": segment_h,
        "point": [-1, 1.1],
        "tolerance": 0.1,
        "return_value": ()
    },
    17: {
        "segment": segment_h,
        "point": [-1, 1.1],
        "tolerance": 0.01,
        "return_value": ()
    },
    18: {
        "segment": [[-10, 10], [10, 10]],
        "point":  [8, 10],
        "tolerance": 0.1,
        "return_value": (([-10, 10], [8, 10]), ([8, 10], [10, 10]))
    },
}

linestring_split_by_point_parameters = {
    0: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {'type': 'Point', 'coordinates': [-10, -5]},  # point on segment
        "tolerance": None,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]]},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10], [10, 10]]}
                         ]
                         }
    },
    1: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -5], [-10, 2]]},  # point on segment
        "tolerance": None,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]]},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 2]]},
                             {'type': 'LineString', 'coordinates': [[-10, 2], [-10, 10], [10, 10]]}
                         ]
                         }
    },
    2: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type":  "MultiPoint", "coordinates": [[-10, -5], [-10, 2], [8, 10]]},  # point on segment
        "tolerance": None,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]]},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 2]]},
                             {'type': 'LineString', 'coordinates': [[-10, 2], [-10, 10], [8, 10]]},
                             {'type': 'LineString', 'coordinates': [[8, 10], [10, 10]]}
                         ]
                         }
    },
    3: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "Point", "coordinates": [-10, -10]},  # point on extremity of linestring segment
        "tolerance": None,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
                         ]
                         }
    },
    4: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "Point", "coordinates": [-10, 10]},  # point on extremity of linestring segment
        "tolerance": None,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10]]},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [10, 10]]},
                         ]
                         }
    },
    5: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "Point", "coordinates": [10, 10]},  # point on extremity of linestring segment
        "tolerance": None,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
                         ]
                         }
    },
    6: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -10], [-10, 10], [10, 10]]},  # point on extremity of
                                                                                            # linestring segment
        "tolerance": None,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10]]},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [10, 10]]},
                         ]
                         }
    },
    7: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -5], [-10, 10]]},
        "tolerance": None,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]]},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10]]},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [10, 10]]},
                         ]
                         }
    },
    8: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -5], [-10, 10], [8, 10]]},
        "tolerance": None,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]]},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10]]},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [8, 10]]},
                             {'type': 'LineString', 'coordinates': [[8, 10], [10, 10]]},
                         ]
                         }
    },
    9: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[8, 10], [-10, 10], [-10, -5]]},
        "tolerance": None,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]]},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10]]},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [8, 10]]},
                             {'type': 'LineString', 'coordinates': [[8, 10], [10, 10]]},
                         ]
                         }
    },
    10: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {'type': 'Point', 'coordinates': [-10, -5]},  # point on segment
        "tolerance": 1,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]]},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10], [10, 10]]}
                         ]
                         }
    },
    11: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -5], [-10, 2]]},  # point on segment
        "tolerance": 1,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]]},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 2]]},
                             {'type': 'LineString', 'coordinates': [[-10, 2], [-10, 10], [10, 10]]}
                         ]
                         }
    },
    12: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type":  "MultiPoint", "coordinates": [[-10, -5], [-10, 2], [8, 10]]},  # point on segment
        "tolerance": 0.1,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]]},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 2]]},
                             {'type': 'LineString', 'coordinates': [[-10, 2], [-10, 10], [8, 10]]},
                             {'type': 'LineString', 'coordinates': [[8, 10], [10, 10]]}
                         ]
                         }
    },
    13: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "Point", "coordinates": [-10, -10]},  # point on extremity of linestring segment
        "tolerance": 1,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
                         ]
                         }
    },
    14: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "Point", "coordinates": [-10, 10]},  # point on extremity of linestring segment
        "tolerance": 1,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10]]},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [10, 10]]},
                         ]
                         }
    },
    15: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "Point", "coordinates": [10, 10]},  # point on extremity of linestring segment
        "tolerance": 1,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
                         ]
                         }
    },
    16: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -10], [-10, 10], [10, 10]]},  # point on extremity of
                                                                                            # linestring segment
        "tolerance": 1,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10]]},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [10, 10]]},
                         ]
                         }
    },
    17: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -5], [-10, 10]]},
        "tolerance": 0.1,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]]},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10]]},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [10, 10]]},
                         ]
                         }
    },
    18: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -5], [-10, 10], [8, 10]]},
        "tolerance": 0.1,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]]},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10]]},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [8, 10]]},
                             {'type': 'LineString', 'coordinates': [[8, 10], [10, 10]]},
                         ]
                         }
    },
    19: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[8, 10], [-10, 10], [-10, -5]]},
        "tolerance": 0.1,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]]},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10]]},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [8, 10]]},
                             {'type': 'LineString', 'coordinates': [[8, 10], [10, 10]]},
                         ]
                         }
    },
    20: {
        "linestring": {'type': 'LineString', 'coordinates': [[-74062.4730695189, 5594994.6112383], [-74050.9525103839, 5594962.59723702], [-74048.6341860374, 5594954.31724249], [-74047.9358723277, 5594945.39805863], [-74050.6725470166, 5594938.58533757], [-74054.076816874, 5594930.63934635], [-74052.9790999776, 5594920.98888547], [-74048.2481768687, 5594912.95991153], [-74039.1474096008, 5594907.71710154], [-74032.2852820254, 5594902.74026302], [-74028.3194413904, 5594895.42598695], [-74025.8315754671, 5594888.07287173], [-73988.576257249, 5594740.72677394], [-73985.8582675289, 5594717.33522379], [-73981.1355215588, 5594638.8746381], [-73978.6337011271, 5594631.52235549], [-73973.2497420491, 5594626.50678815], [-73963.919798661, 5594624.61151233], [-73952.4129308591, 5594627.56609538], [-73888.8254872408, 5594648.73622164], [-73874.5105866752, 5594653.79779362], [-73858.6728080833, 5594659.77687909], [-73812.7309023294, 5594676.31349433], [-73695.0375046261, 5594716.12853294], [-73527.8559539787, 5594770.75768864], [-73405.7930181951, 5594811.8562396], [-73304.9310107833, 5594846.2229106], [-73284.2472572591, 5594853.50957252], [-73277.5682408938, 5594853.84063557], [-73269.4005031621, 5594851.46769416], [-73260.7872261793, 5594846.711104], [-73251.1482319332, 5594843.27362424], [-73240.7228914151, 5594842.4028789], [-73230.2466985005, 5594845.09776207], [-73222.2190646746, 5594849.27949406], [-73214.8838370089, 5594855.38118901], [-73210.0938816653, 5594862.30077251], [-73207.4840924626, 5594870.3800252], [-73205.641565639, 5594880.16376163], [-73203.0649772395, 5594888.35464593], [-73198.4810460651, 5594894.52961361], [-73190.5991816918, 5594900.69851345], [-73177.2912167857, 5594909.36164303], [-73127.6460312972, 5594941.67388449], [-73074.8734693464, 5594977.46479144], [-73057.4290014858, 5594989.10089726], [-73045.8461131957, 5594997.89785055], [-72971.6367448112, 5595051.20395681], [-72848.0330742924, 5595138.70450259], [-72761.9914587966, 5595200.02586238], [-72709.2074862875, 5595236.25438489], [-72687.7400472862, 5595246.82778638], [-72666.4164837638, 5595253.3927822], [-72406.5418298497, 5595296.70043338], [-72392.9332598039, 5595298.70182426], [-72377.1303322839, 5595299.85501336], [-72360.4974259444, 5595299.78717806], [-72346.1983134473, 5595298.65217789], [-72329.0940972751, 5595295.62188003], [-72311.0513308493, 5595291.14920806], [-72279.4222393235, 5595280.7012809], [-72264.0823405659, 5595271.45396598], [-72211.7386919101, 5595254.46203929], [-72156.7430272802, 5595238.66443883], [-72150.1657848682, 5595236.24675594], [-72147.408121099, 5595234.15132421], [-72146.2275757848, 5595232.02701789], [-72145.6681384656, 5595228.98376686], [-72147.3946914174, 5595206.86032513], [-72147.6857394117, 5595166.26342778], [-72148.2554343922, 5595141.91579755], [-72148.1193284128, 5595125.70268906], [-72149.702625433, 5594991.16931499], [-72150.3833270254, 5594930.37756268], [-72148.1734309941, 5594840.36191634], [-72147.308154279, 5594809.16552009], [-72145.763732548, 5594773.82862151], [-72142.6919911224, 5594713.26451546], [-72142.4342319784, 5594707.21013513], [-72142.6519773053, 5594701.38878156], [-72143.4005990435, 5594696.40596734], [-72144.3178591147, 5594691.72661013], [-72145.8153887831, 5594685.84741135], [-72147.9261348622, 5594679.50215773], [-72171.7965412813, 5594611.99405678], [-72174.2483310051, 5594606.34041713], [-72189.7153040099, 5594575.45276627], [-72198.1700791313, 5594558.49875766], [-72201.0226811491, 5594551.10197789], [-72206.7012328547, 5594542.30486055], [-72214.1788827424, 5594534.34548087], [-72219.3149145933, 5594526.64751431], [-72220.7221362357, 5594519.38680402], [-72219.6188734215, 5594512.70621936], [-72217.253596409, 5594506.4786109], [-72216.7664395217, 5594498.45519427], [-72221.4934640755, 5594475.68880672], [-72229.9925228256, 5594443.09461318], [-72285.8266030373, 5594286.91687431], [-72298.4231798958, 5594251.12631428], [-72306.0445622854, 5594229.12036007]], 'bbox': (-74062.4730695189, 5594229.12036007, -72142.4342319784, 5595299.85501336)},
        "point": {'type': 'MultiPoint', 'coordinates': [[-74116.7315587956, 5597816.64532827], [-73975.1948644918, 5594628.31881763], [-73719.9156979786, 5594707.71237496], [-73710.4430581194, 5594710.91691769], [-73321.4922547073, 5594840.58000465], [-73146.7757729914, 5594929.22303298], [-72657.3749615275, 5595254.89953588], [-72147.2010452765, 5595209.34163861], [-72206.5075275729, 5594542.60494554], [-72302.9179382529, 5593193.26413283]]},
        "tolerance": 0.0000001,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection', 'geometries': [{'type': 'LineString', 'coordinates': [[-74062.4730695189, 5594994.6112383], [-74050.9525103839, 5594962.59723702], [-74048.6341860374, 5594954.31724249], [-74047.9358723277, 5594945.39805863], [-74050.6725470166, 5594938.58533757], [-74054.076816874, 5594930.63934635], [-74052.9790999776, 5594920.98888547], [-74048.2481768687, 5594912.95991153], [-74039.1474096008, 5594907.71710154], [-74032.2852820254, 5594902.74026302], [-74028.3194413904, 5594895.42598695], [-74025.8315754671, 5594888.07287173], [-73988.576257249, 5594740.72677394], [-73985.8582675289, 5594717.33522379], [-73981.1355215588, 5594638.8746381], [-73978.6337011271, 5594631.52235549], [-73975.1948644918, 5594628.31881763]]}, {'type': 'LineString', 'coordinates': [[-73975.1948644918, 5594628.31881763], [-73973.2497420491, 5594626.50678815], [-73963.919798661, 5594624.61151233], [-73952.4129308591, 5594627.56609538], [-73888.8254872408, 5594648.73622164], [-73874.5105866752, 5594653.79779362], [-73858.6728080833, 5594659.77687909], [-73812.7309023294, 5594676.31349433], [-73719.9156979786, 5594707.71237496]]}, {'type': 'LineString', 'coordinates': [[-73719.9156979786, 5594707.71237496], [-73710.4430581194, 5594710.91691769]]}, {'type': 'LineString', 'coordinates': [[-73710.4430581194, 5594710.91691769], [-73695.0375046261, 5594716.12853294], [-73527.8559539787, 5594770.75768864], [-73405.7930181951, 5594811.8562396], [-73321.4922547073, 5594840.58000465]]}, {'type': 'LineString', 'coordinates': [[-73321.4922547073, 5594840.58000465], [-73304.9310107833, 5594846.2229106], [-73284.2472572591, 5594853.50957252], [-73277.5682408938, 5594853.84063557], [-73269.4005031621, 5594851.46769416], [-73260.7872261793, 5594846.711104], [-73251.1482319332, 5594843.27362424], [-73240.7228914151, 5594842.4028789], [-73230.2466985005, 5594845.09776207], [-73222.2190646746, 5594849.27949406], [-73214.8838370089, 5594855.38118901], [-73210.0938816653, 5594862.30077251], [-73207.4840924626, 5594870.3800252], [-73205.641565639, 5594880.16376163], [-73203.0649772395, 5594888.35464593], [-73198.4810460651, 5594894.52961361], [-73190.5991816918, 5594900.69851345], [-73177.2912167857, 5594909.36164303], [-73146.7757729914, 5594929.22303298]]}, {'type': 'LineString', 'coordinates': [[-73146.7757729914, 5594929.22303298], [-73127.6460312972, 5594941.67388449], [-73074.8734693464, 5594977.46479144], [-73057.4290014858, 5594989.10089726], [-73045.8461131957, 5594997.89785055], [-72971.6367448112, 5595051.20395681], [-72848.0330742924, 5595138.70450259], [-72761.9914587966, 5595200.02586238], [-72709.2074862875, 5595236.25438489], [-72687.7400472862, 5595246.82778638], [-72666.4164837638, 5595253.3927822], [-72657.3749615275, 5595254.89953588]]}, {'type': 'LineString', 'coordinates': [[-72657.3749615275, 5595254.89953588], [-72406.5418298497, 5595296.70043338], [-72392.9332598039, 5595298.70182426], [-72377.1303322839, 5595299.85501336], [-72360.4974259444, 5595299.78717806], [-72346.1983134473, 5595298.65217789], [-72329.0940972751, 5595295.62188003], [-72311.0513308493, 5595291.14920806], [-72279.4222393235, 5595280.7012809], [-72264.0823405659, 5595271.45396598], [-72211.7386919101, 5595254.46203929], [-72156.7430272802, 5595238.66443883], [-72150.1657848682, 5595236.24675594], [-72147.408121099, 5595234.15132421], [-72146.2275757848, 5595232.02701789], [-72145.6681384656, 5595228.98376686], [-72147.2010452765, 5595209.34163861]]}, {'type': 'LineString', 'coordinates': [[-72147.2010452765, 5595209.34163861], [-72147.3946914174, 5595206.86032513], [-72147.6857394117, 5595166.26342778], [-72148.2554343922, 5595141.91579755], [-72148.1193284128, 5595125.70268906], [-72149.702625433, 5594991.16931499], [-72150.3833270254, 5594930.37756268], [-72148.1734309941, 5594840.36191634], [-72147.308154279, 5594809.16552009], [-72145.763732548, 5594773.82862151], [-72142.6919911224, 5594713.26451546], [-72142.4342319784, 5594707.21013513], [-72142.6519773053, 5594701.38878156], [-72143.4005990435, 5594696.40596734], [-72144.3178591147, 5594691.72661013], [-72145.8153887831, 5594685.84741135], [-72147.9261348622, 5594679.50215773], [-72171.7965412813, 5594611.99405678], [-72174.2483310051, 5594606.34041713], [-72189.7153040099, 5594575.45276627], [-72198.1700791313, 5594558.49875766], [-72201.0226811491, 5594551.10197789], [-72206.5075275729, 5594542.60494554]]}, {'type': 'LineString', 'coordinates': [[-72206.5075275729, 5594542.60494554], [-72206.7012328547, 5594542.30486055], [-72214.1788827424, 5594534.34548087], [-72219.3149145933, 5594526.64751431], [-72220.7221362357, 5594519.38680402], [-72219.6188734215, 5594512.70621936], [-72217.253596409, 5594506.4786109], [-72216.7664395217, 5594498.45519427], [-72221.4934640755, 5594475.68880672], [-72229.9925228256, 5594443.09461318], [-72285.8266030373, 5594286.91687431], [-72298.4231798958, 5594251.12631428], [-72306.0445622854, 5594229.12036007]]}]}
    },
    21: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {'type': 'Point', 'coordinates': [-10, -5]},  # point on segment
        "tolerance": None,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]], 'bbox': (-10, -10, -10, -5)},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10], [10, 10]], 'bbox': (-10, -5, 10, 10)}
                         ],
                         'bbox': (-10, -10, 10, 10)
                         }
    },
    22: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -5], [-10, 2]]},  # point on segment
        "tolerance": None,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]], "bbox": (-10, -10, -10, -5)},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 2]], "bbox": (-10, -5, -10, 2)},
                             {'type': 'LineString', 'coordinates': [[-10, 2], [-10, 10], [10, 10]], "bbox": (-10, 2, 10, 10)}
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    23: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type":  "MultiPoint", "coordinates": [[-10, -5], [-10, 2], [8, 10]]},  # point on segment
        "tolerance": None,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]], "bbox": (-10, -10, -10, -5)},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 2]], "bbox": (-10, -5, -10, 2)},
                             {'type': 'LineString', 'coordinates': [[-10, 2], [-10, 10], [8, 10]], "bbox": (-10, 2, 8, 10)},
                             {'type': 'LineString', 'coordinates': [[8, 10], [10, 10]], "bbox": (8, 10, 10, 10)}
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    24: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "Point", "coordinates": [-10, -10]},  # point on extremity of linestring segment
        "tolerance": None,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]], "bbox": (-10, -10, 10, 10)},
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    25: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "Point", "coordinates": [-10, 10]},  # point on extremity of linestring segment
        "tolerance": None,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10]], 'bbox': (-10, -10, -10, 10)},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [10, 10]], 'bbox': (-10, 10, 10, 10)},
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    26: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "Point", "coordinates": [10, 10]},  # point on extremity of linestring segment
        "tolerance": None,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]], "bbox": (-10, -10, 10, 10)},
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    27: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -10], [-10, 10], [10, 10]]},  # point on extremity of
                                                                                            # linestring segment
        "tolerance": None,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10]], "bbox": (-10, -10, -10, 10)},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [10, 10]], "bbox": (-10, 10, 10, 10)},
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    28: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -5], [-10, 10]]},
        "tolerance": None,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]], "bbox": (-10, -10, -10, -5)},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10]], "bbox": (-10, -5, -10, 10)},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [10, 10]], "bbox": (-10, 10, 10, 10)},
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    29: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -5], [-10, 10], [8, 10]]},
        "tolerance": None,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]], "bbox": (-10, -10, -10, -5)},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10]], "bbox": (-10, -5, -10, 10)},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [8, 10]], "bbox": (-10, 10, 8, 10)},
                             {'type': 'LineString', 'coordinates': [[8, 10], [10, 10]], "bbox": (8, 10, 10, 10)},
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    30: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[8, 10], [-10, 10], [-10, -5]]},
        "tolerance": None,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]], "bbox": (-10, -10, -10, -5)},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10]], "bbox": (-10, -5, -10, 10)},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [8, 10]], "bbox": (-10, 10, 8, 10)},
                             {'type': 'LineString', 'coordinates': [[8, 10], [10, 10]], "bbox": (8, 10, 10, 10)},
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    31: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {'type': 'Point', 'coordinates': [-10, -5]},  # point on segment
        "tolerance": 1,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]], "bbox": (-10, -10, -10, -5)},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10], [10, 10]], "bbox": (-10, -5, 10, 10)}
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    32: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -5], [-10, 2]]},  # point on segment
        "tolerance": 1,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]], "bbox": (-10, -10, -10, -5)},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 2]], "bbox": (-10, -5, -10, 2)},
                             {'type': 'LineString', 'coordinates': [[-10, 2], [-10, 10], [10, 10]], "bbox": (-10, 2, 10, 10)}
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    33: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type":  "MultiPoint", "coordinates": [[-10, -5], [-10, 2], [8, 10]]},  # point on segment
        "tolerance": 0.1,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]], "bbox": (-10, -10, -10, -5)},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 2]], "bbox": (-10, -5, -10, 2)},
                             {'type': 'LineString', 'coordinates': [[-10, 2], [-10, 10], [8, 10]], "bbox": (-10, 2, 8, 10)},
                             {'type': 'LineString', 'coordinates': [[8, 10], [10, 10]], "bbox": (8, 10, 10, 10)}
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    34: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "Point", "coordinates": [-10, -10]},  # point on extremity of linestring segment
        "tolerance": 1,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]], "bbox": (-10, -10, 10, 10)},
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    35: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "Point", "coordinates": [-10, 10]},  # point on extremity of linestring segment
        "tolerance": 1,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10]], "bbox": (-10, -10, -10, 10)},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [10, 10]], "bbox": (-10, 10, 10, 10)},
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    36: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "Point", "coordinates": [10, 10]},  # point on extremity of linestring segment
        "tolerance": 1,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]], "bbox": (-10, -10, 10, 10)}
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    37: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -10], [-10, 10], [10, 10]]},  # point on extremity of
                                                                                            # linestring segment
        "tolerance": 1,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10]], "bbox": (-10, -10, -10, 10)},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [10, 10]], "bbox": (-10, 10, 10, 10)},
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    38: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -5], [-10, 10]]},
        "tolerance": 0.1,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]], "bbox": (-10, -10, -10, -5)},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10]], "bbox": (-10, -5, -10, 10)},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [10, 10]], "bbox": (-10, 10, 10, 10)},
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    39: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[-10, -5], [-10, 10], [8, 10]]},
        "tolerance": 0.1,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]], "bbox": (-10, -10, -10, -5)},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10]], "bbox": (-10, -5, -10, 10)},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [8, 10]], "bbox": (-10, 10, 8, 10)},
                             {'type': 'LineString', 'coordinates': [[8, 10], [10, 10]], "bbox":  (8, 10, 10, 10)},
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    40: {
        "linestring": {'type': 'LineString', 'coordinates': [[-10, -10], [-10, 10], [10, 10]]},
        "point": {"type": "MultiPoint", "coordinates": [[8, 10], [-10, 10], [-10, -5]]},
        "tolerance": 0.1,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                             {'type': 'LineString', 'coordinates': [[-10, -10], [-10, -5]], "bbox": (-10, -10, -10, -5)},
                             {'type': 'LineString', 'coordinates': [[-10, -5], [-10, 10]], "bbox": (-10, -5, -10, 10)},
                             {'type': 'LineString', 'coordinates': [[-10, 10], [8, 10]], "bbox": (-10, 10, 8, 10)},
                             {'type': 'LineString', 'coordinates': [[8, 10], [10, 10]], "bbox": (8, 10, 10, 10)},
                         ],
                         "bbox": (-10, -10, 10, 10)
                         }
    },
    41: {
        "linestring": {'type': 'LineString', 'coordinates': [[-74062.4730695189, 5594994.6112383], [-74050.9525103839, 5594962.59723702], [-74048.6341860374, 5594954.31724249], [-74047.9358723277, 5594945.39805863], [-74050.6725470166, 5594938.58533757], [-74054.076816874, 5594930.63934635], [-74052.9790999776, 5594920.98888547], [-74048.2481768687, 5594912.95991153], [-74039.1474096008, 5594907.71710154], [-74032.2852820254, 5594902.74026302], [-74028.3194413904, 5594895.42598695], [-74025.8315754671, 5594888.07287173], [-73988.576257249, 5594740.72677394], [-73985.8582675289, 5594717.33522379], [-73981.1355215588, 5594638.8746381], [-73978.6337011271, 5594631.52235549], [-73973.2497420491, 5594626.50678815], [-73963.919798661, 5594624.61151233], [-73952.4129308591, 5594627.56609538], [-73888.8254872408, 5594648.73622164], [-73874.5105866752, 5594653.79779362], [-73858.6728080833, 5594659.77687909], [-73812.7309023294, 5594676.31349433], [-73695.0375046261, 5594716.12853294], [-73527.8559539787, 5594770.75768864], [-73405.7930181951, 5594811.8562396], [-73304.9310107833, 5594846.2229106], [-73284.2472572591, 5594853.50957252], [-73277.5682408938, 5594853.84063557], [-73269.4005031621, 5594851.46769416], [-73260.7872261793, 5594846.711104], [-73251.1482319332, 5594843.27362424], [-73240.7228914151, 5594842.4028789], [-73230.2466985005, 5594845.09776207], [-73222.2190646746, 5594849.27949406], [-73214.8838370089, 5594855.38118901], [-73210.0938816653, 5594862.30077251], [-73207.4840924626, 5594870.3800252], [-73205.641565639, 5594880.16376163], [-73203.0649772395, 5594888.35464593], [-73198.4810460651, 5594894.52961361], [-73190.5991816918, 5594900.69851345], [-73177.2912167857, 5594909.36164303], [-73127.6460312972, 5594941.67388449], [-73074.8734693464, 5594977.46479144], [-73057.4290014858, 5594989.10089726], [-73045.8461131957, 5594997.89785055], [-72971.6367448112, 5595051.20395681], [-72848.0330742924, 5595138.70450259], [-72761.9914587966, 5595200.02586238], [-72709.2074862875, 5595236.25438489], [-72687.7400472862, 5595246.82778638], [-72666.4164837638, 5595253.3927822], [-72406.5418298497, 5595296.70043338], [-72392.9332598039, 5595298.70182426], [-72377.1303322839, 5595299.85501336], [-72360.4974259444, 5595299.78717806], [-72346.1983134473, 5595298.65217789], [-72329.0940972751, 5595295.62188003], [-72311.0513308493, 5595291.14920806], [-72279.4222393235, 5595280.7012809], [-72264.0823405659, 5595271.45396598], [-72211.7386919101, 5595254.46203929], [-72156.7430272802, 5595238.66443883], [-72150.1657848682, 5595236.24675594], [-72147.408121099, 5595234.15132421], [-72146.2275757848, 5595232.02701789], [-72145.6681384656, 5595228.98376686], [-72147.3946914174, 5595206.86032513], [-72147.6857394117, 5595166.26342778], [-72148.2554343922, 5595141.91579755], [-72148.1193284128, 5595125.70268906], [-72149.702625433, 5594991.16931499], [-72150.3833270254, 5594930.37756268], [-72148.1734309941, 5594840.36191634], [-72147.308154279, 5594809.16552009], [-72145.763732548, 5594773.82862151], [-72142.6919911224, 5594713.26451546], [-72142.4342319784, 5594707.21013513], [-72142.6519773053, 5594701.38878156], [-72143.4005990435, 5594696.40596734], [-72144.3178591147, 5594691.72661013], [-72145.8153887831, 5594685.84741135], [-72147.9261348622, 5594679.50215773], [-72171.7965412813, 5594611.99405678], [-72174.2483310051, 5594606.34041713], [-72189.7153040099, 5594575.45276627], [-72198.1700791313, 5594558.49875766], [-72201.0226811491, 5594551.10197789], [-72206.7012328547, 5594542.30486055], [-72214.1788827424, 5594534.34548087], [-72219.3149145933, 5594526.64751431], [-72220.7221362357, 5594519.38680402], [-72219.6188734215, 5594512.70621936], [-72217.253596409, 5594506.4786109], [-72216.7664395217, 5594498.45519427], [-72221.4934640755, 5594475.68880672], [-72229.9925228256, 5594443.09461318], [-72285.8266030373, 5594286.91687431], [-72298.4231798958, 5594251.12631428], [-72306.0445622854, 5594229.12036007]], 'bbox': (-74062.4730695189, 5594229.12036007, -72142.4342319784, 5595299.85501336)},
        "point": {'type': 'MultiPoint', 'coordinates': [[-74116.7315587956, 5597816.64532827], [-73975.1948644918, 5594628.31881763], [-73719.9156979786, 5594707.71237496], [-73710.4430581194, 5594710.91691769], [-73321.4922547073, 5594840.58000465], [-73146.7757729914, 5594929.22303298], [-72657.3749615275, 5595254.89953588], [-72147.2010452765, 5595209.34163861], [-72206.5075275729, 5594542.60494554], [-72302.9179382529, 5593193.26413283]]},
        "tolerance": 0.0000001,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection', 'geometries': [{'type': 'LineString', 'coordinates': [[-74062.4730695189, 5594994.6112383], [-74050.9525103839, 5594962.59723702], [-74048.6341860374, 5594954.31724249], [-74047.9358723277, 5594945.39805863], [-74050.6725470166, 5594938.58533757], [-74054.076816874, 5594930.63934635], [-74052.9790999776, 5594920.98888547], [-74048.2481768687, 5594912.95991153], [-74039.1474096008, 5594907.71710154], [-74032.2852820254, 5594902.74026302], [-74028.3194413904, 5594895.42598695], [-74025.8315754671, 5594888.07287173], [-73988.576257249, 5594740.72677394], [-73985.8582675289, 5594717.33522379], [-73981.1355215588, 5594638.8746381], [-73978.6337011271, 5594631.52235549], [-73975.1948644918, 5594628.31881763]], 'bbox': (-74062.4730695189, 5594628.31881763, -73975.1948644918, 5594994.6112383)}, {'type': 'LineString', 'coordinates': [[-73975.1948644918, 5594628.31881763], [-73973.2497420491, 5594626.50678815], [-73963.919798661, 5594624.61151233], [-73952.4129308591, 5594627.56609538], [-73888.8254872408, 5594648.73622164], [-73874.5105866752, 5594653.79779362], [-73858.6728080833, 5594659.77687909], [-73812.7309023294, 5594676.31349433], [-73719.9156979786, 5594707.71237496]], 'bbox': (-73975.1948644918, 5594624.61151233, -73719.9156979786, 5594707.71237496)}, {'type': 'LineString', 'coordinates': [[-73719.9156979786, 5594707.71237496], [-73710.4430581194, 5594710.91691769]], 'bbox': (-73719.9156979786, 5594707.71237496, -73710.4430581194, 5594710.91691769)}, {'type': 'LineString', 'coordinates': [[-73710.4430581194, 5594710.91691769], [-73695.0375046261, 5594716.12853294], [-73527.8559539787, 5594770.75768864], [-73405.7930181951, 5594811.8562396], [-73321.4922547073, 5594840.58000465]], 'bbox': (-73710.4430581194, 5594710.91691769, -73321.4922547073, 5594840.58000465)}, {'type': 'LineString', 'coordinates': [[-73321.4922547073, 5594840.58000465], [-73304.9310107833, 5594846.2229106], [-73284.2472572591, 5594853.50957252], [-73277.5682408938, 5594853.84063557], [-73269.4005031621, 5594851.46769416], [-73260.7872261793, 5594846.711104], [-73251.1482319332, 5594843.27362424], [-73240.7228914151, 5594842.4028789], [-73230.2466985005, 5594845.09776207], [-73222.2190646746, 5594849.27949406], [-73214.8838370089, 5594855.38118901], [-73210.0938816653, 5594862.30077251], [-73207.4840924626, 5594870.3800252], [-73205.641565639, 5594880.16376163], [-73203.0649772395, 5594888.35464593], [-73198.4810460651, 5594894.52961361], [-73190.5991816918, 5594900.69851345], [-73177.2912167857, 5594909.36164303], [-73146.7757729914, 5594929.22303298]], 'bbox': (-73321.4922547073, 5594840.58000465, -73146.7757729914, 5594929.22303298)}, {'type': 'LineString', 'coordinates': [[-73146.7757729914, 5594929.22303298], [-73127.6460312972, 5594941.67388449], [-73074.8734693464, 5594977.46479144], [-73057.4290014858, 5594989.10089726], [-73045.8461131957, 5594997.89785055], [-72971.6367448112, 5595051.20395681], [-72848.0330742924, 5595138.70450259], [-72761.9914587966, 5595200.02586238], [-72709.2074862875, 5595236.25438489], [-72687.7400472862, 5595246.82778638], [-72666.4164837638, 5595253.3927822], [-72657.3749615275, 5595254.89953588]], 'bbox': (-73146.7757729914, 5594929.22303298, -72657.3749615275, 5595254.89953588)}, {'type': 'LineString', 'coordinates': [[-72657.3749615275, 5595254.89953588], [-72406.5418298497, 5595296.70043338], [-72392.9332598039, 5595298.70182426], [-72377.1303322839, 5595299.85501336], [-72360.4974259444, 5595299.78717806], [-72346.1983134473, 5595298.65217789], [-72329.0940972751, 5595295.62188003], [-72311.0513308493, 5595291.14920806], [-72279.4222393235, 5595280.7012809], [-72264.0823405659, 5595271.45396598], [-72211.7386919101, 5595254.46203929], [-72156.7430272802, 5595238.66443883], [-72150.1657848682, 5595236.24675594], [-72147.408121099, 5595234.15132421], [-72146.2275757848, 5595232.02701789], [-72145.6681384656, 5595228.98376686], [-72147.2010452765, 5595209.34163861]], 'bbox': (-72657.3749615275, 5595209.34163861, -72145.6681384656, 5595299.85501336)}, {'type': 'LineString', 'coordinates': [[-72147.2010452765, 5595209.34163861], [-72147.3946914174, 5595206.86032513], [-72147.6857394117, 5595166.26342778], [-72148.2554343922, 5595141.91579755], [-72148.1193284128, 5595125.70268906], [-72149.702625433, 5594991.16931499], [-72150.3833270254, 5594930.37756268], [-72148.1734309941, 5594840.36191634], [-72147.308154279, 5594809.16552009], [-72145.763732548, 5594773.82862151], [-72142.6919911224, 5594713.26451546], [-72142.4342319784, 5594707.21013513], [-72142.6519773053, 5594701.38878156], [-72143.4005990435, 5594696.40596734], [-72144.3178591147, 5594691.72661013], [-72145.8153887831, 5594685.84741135], [-72147.9261348622, 5594679.50215773], [-72171.7965412813, 5594611.99405678], [-72174.2483310051, 5594606.34041713], [-72189.7153040099, 5594575.45276627], [-72198.1700791313, 5594558.49875766], [-72201.0226811491, 5594551.10197789], [-72206.5075275729, 5594542.60494554]], 'bbox': (-72206.5075275729, 5594542.60494554, -72142.4342319784, 5595209.34163861)}, {'type': 'LineString', 'coordinates': [[-72206.5075275729, 5594542.60494554], [-72206.7012328547, 5594542.30486055], [-72214.1788827424, 5594534.34548087], [-72219.3149145933, 5594526.64751431], [-72220.7221362357, 5594519.38680402], [-72219.6188734215, 5594512.70621936], [-72217.253596409, 5594506.4786109], [-72216.7664395217, 5594498.45519427], [-72221.4934640755, 5594475.68880672], [-72229.9925228256, 5594443.09461318], [-72285.8266030373, 5594286.91687431], [-72298.4231798958, 5594251.12631428], [-72306.0445622854, 5594229.12036007]], 'bbox': (-72306.0445622854, 5594229.12036007, -72206.5075275729, 5594542.60494554)}], 'bbox': (-74062.4730695189, 5594229.12036007, -72142.4342319784, 5595299.85501336)}
    },
    42: {
        "linestring": {'type': "LineString", "coordinates": [[-63158.61131026333, 5596063.5605541505], [-63162.88909308814, 5596064.050241007], [-63168.20512004753, 5596064.11221106]]},
        "point": {'type': 'Point', 'coordinates': [-63163.11369898082, 5596064.052859285]},
        "tolerance": 1.,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection', 'geometries': [{'type': 'LineString', 'coordinates': [[-63158.61131026333, 5596063.5605541505], [-63162.88909308814, 5596064.050241007]], 'bbox': (-63162.88909308814, 5596063.5605541505, -63158.61131026333, 5596064.050241007)}, {'type': 'LineString', 'coordinates': [[-63162.88909308814, 5596064.050241007], [-63168.20512004753, 5596064.11221106]], 'bbox': (-63168.20512004753, 5596064.050241007, -63162.88909308814, 5596064.11221106)}], 'bbox': (-63168.20512004753, 5596063.5605541505, -63158.61131026333, 5596064.11221106)}
    }
}


def test_all():
    # segment_split_by_point
    print(test_function(segment_split_by_point, segment_split_by_point_parameters))

    # linestring_split_by_point
    print(test_function(linestring_split_by_point, linestring_split_by_point_parameters))


if __name__ == '__main__':
    test_all()
