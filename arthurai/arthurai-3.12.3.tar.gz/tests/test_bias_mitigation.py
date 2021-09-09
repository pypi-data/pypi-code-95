import pytest 
import responses

import pandas as pd

from arthurai.client.base import BaseApiClient
from arthurai.core.models import ArthurModel
from arthurai.core.bias.threshold_mitigation import Curves

from .test_request_models.fixtures import model_response_json_strings
from .fixtures.mocks import BASE_URL, ACCESS_KEY

modelclient = BaseApiClient(url=BASE_URL, access_key=ACCESS_KEY, base_path="binarybasepath", offline=True)

BINARY_MODEL = ArthurModel.from_json(model_response_json_strings[4])
BINARY_MODEL._client = BaseApiClient(url=BASE_URL, access_key=ACCESS_KEY, base_path="binarybasepath", offline=True)

mock_curve_response = {
    'data': [ {
        'constraint': 'demographic_parity',
        'x_label': 'selection_rate',
        'y_label': 'accuracy',
        'model_id': 'test_modelid',
        'attribute_name': 'test_attrname',
        'categorical_value': 'attrval1', 
        'data_points': [
            {'x': 1, 'y': 2, 'threshold': 0.5}
        ],
        'optimization_index': 0
    }, 
    {
        'constraint': 'demographic_parity',
        'x_label': 'selection_rate',
        'y_label': 'accuracy',
        'model_id': 'test_modelid',
        'attribute_name': 'test_attrname',
        'categorical_value': 'attrval2', 
        'data_points': [
            {'x': 1.5, 'y': 2.5, 'threshold': 0.55}
        ],
        'optimization_index': 0
    }
    ]
}

mock_curve_response_cont = {
    'data': [ {
        'constraint': 'demographic_parity',
        'x_label': 'selection_rate',
        'y_label': 'accuracy',
        'model_id': 'test_modelid',
        'attribute_name': 'test_attrname',
        'continuous_end': 1, 
        'data_points': [
            {'x': 1, 'y': 2, 'threshold': 0.5}
        ],
        'optimization_index': 0
    }, 
    {
        'constraint': 'demographic_parity',
        'x_label': 'selection_rate',
        'y_label': 'accuracy',
        'model_id': 'test_modelid',
        'attribute_name': 'test_attrname',
        'continuous_start': 1,
        'continuous_end': 2,
        'data_points': [
            {'x': 1.5, 'y': 2.5, 'threshold': 0.55}
        ],
        'optimization_index': 0
    },
    {
        'constraint': 'demographic_parity',
        'x_label': 'selection_rate',
        'y_label': 'accuracy',
        'model_id': 'test_modelid',
        'attribute_name': 'test_attrname',
        'continuous_start': 2,
        'data_points': [
            {'x': 1.1, 'y': 2.1, 'threshold': 0.51}
        ],
        'optimization_index': 0
    }
    ]
}

sampledict = {
    'val_1': pd.DataFrame({'x': [1, 2, 3], 'y': [2,4,6], 'threshold': [0.1, 0.2, 0.3]}),
    'val_2': pd.DataFrame({'x': [1, 2, 3], 'y': [2,4,6], 'threshold': [0.25, 0.35, 0.45]}),
}

test_curve = Curves(attribute_name="testattrname", constraint="equalized_odds", max_acc_idx=1, attr_val_to_threshold = sampledict )

@responses.activate
def test_get_curves():

    responses.add(responses.GET, "http://mockbinarybasepath/models/ac55c7b4-2db7-4902-8cc3-969ed67a20c8_biasbinary/enrichments/bias_mitigation/curves?attribute_id=8514e278-24d1-4e20-b209-3c77eb2b247f&constraint=demographic_parity",
        json = mock_curve_response)
    
    mitigator = BINARY_MODEL.bias.mitigation_threshold 
    curves = mitigator.get_curves("attr_1", "demographic_parity")

    assert curves.constraint == "demographic_parity"
    assert curves.max_acc_idx == 0
    assert curves.attr_val_to_threshold["attrval2"].iloc[0]['x'] == 1.5


@responses.activate
def test_get_curves_continuous():

    responses.add(responses.GET, "http://mockbinarybasepath/models/ac55c7b4-2db7-4902-8cc3-969ed67a20c8_biasbinary/enrichments/bias_mitigation/curves?attribute_id=8514e278-24d1-4e20-b209-3c77eb2b247f&constraint=demographic_parity",
        json = mock_curve_response_cont)
    
    mitigator = BINARY_MODEL.bias.mitigation_threshold 
    curves = mitigator.get_curves("attr_1", "demographic_parity")

    assert curves.constraint == "demographic_parity"
    assert curves.max_acc_idx == 0
    assert '(-inf,1]' in curves.attr_val_to_threshold.keys()
    assert '(1,2]' in curves.attr_val_to_threshold.keys()
    assert curves.attr_val_to_threshold["(2,inf)"].iloc[0]['x'] == 1.1

def test_get_thresholds_for_idx_default():
    mitigator = BINARY_MODEL.bias.mitigation_threshold 

    idxs = mitigator.get_thresholds_for_idx(test_curve)

    assert idxs['val_1'] == 0.2
    assert idxs['val_2'] == 0.35
    assert len(idxs.keys()) == 2

def test_get_thresholds_for_idx_spec():
    mitigator = BINARY_MODEL.bias.mitigation_threshold 

    idxs = mitigator.get_thresholds_for_idx(test_curve, idx=0)

    assert idxs['val_1'] == 0.1
    assert idxs['val_2'] == 0.25
    assert len(idxs.keys()) == 2