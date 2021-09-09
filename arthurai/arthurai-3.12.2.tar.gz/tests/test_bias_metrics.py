import responses
import pytest

from arthurai.client.base import BaseApiClient
from arthurai.core.models import ArthurModel
from arthurai.core.bias.bias_metrics import BiasMetrics

from .test_request_models.fixtures import model_response_json_strings
from .fixtures.mocks import BASE_URL, ACCESS_KEY

modelclient = BaseApiClient(url=BASE_URL, access_key=ACCESS_KEY, base_path="binarybasepath", offline=True)

BINARY_MODEL = ArthurModel.from_json(model_response_json_strings[4])
BINARY_MODEL._client = BaseApiClient(url=BASE_URL, access_key=ACCESS_KEY, base_path="binarybasepath", offline=True)
MULTICLASS_MODEL = ArthurModel.from_json(model_response_json_strings[5])
MULTICLASS_MODEL._client = BaseApiClient(url=BASE_URL, access_key=ACCESS_KEY, base_path="multiclassbasepath", offline=True)

bias_query_json_result = {
            "query_result": [
            {
                "bias": 1,
                "confusion_matrix": {
                "accuracy_rate": 0.9,
                "balanced_accuracy_rate": 0.8,
                "f1": 0.7,
                "false_negative_rate": 0.5,
                "false_positive_rate": 0,
                "precision": 0.9,
                "true_negative_rate": 1,
                "true_positive_rate": 0.5
                }
            },
            {
                "bias": 2,
                "confusion_matrix": {
                "accuracy_rate": 0.9,
                "balanced_accuracy_rate": 0.8,
                "f1": 0.7,
                "false_negative_rate": 0.4,
                "false_positive_rate": 0,
                "precision": 0.8,
                "true_negative_rate": 1,
                "true_positive_rate": 0.6
                }
            }
            ],
            "sampling_threshold": 1
        }
    

@responses.activate
def test_get_bias_cm_binary():

    responses.add(responses.POST, "http://mockbinarybasepath/models/ac55c7b4-2db7-4902-8cc3-969ed67a20c8_biasbinary/inferences/query",
        json = bias_query_json_result
    )

    bin_metric = BiasMetrics(BINARY_MODEL)

    metrics = bin_metric.group_confusion_matrices("bias")
    metrics_flipped = bin_metric.group_confusion_matrices("bias", return_by_metric=False)

    assert "precision" in metrics.keys()
    assert len(metrics.keys()) == 8
    assert len(metrics['f1'].keys()) == 2
    assert len(metrics_flipped[1].keys()) == 8
    assert metrics_flipped[1]['accuracy_rate'] == 0.9

@responses.activate
def test_get_bias_cm_multiclass():
    responses.add(responses.POST, "http://mockmulticlassbasepath/models/ac55c7b4-2db7-4902-8cc3-969ed67a20c8_biasmulticlass/inferences/query",
        json = bias_query_json_result
    )

    mult_metric = BiasMetrics(MULTICLASS_MODEL)
    metrics = mult_metric.group_confusion_matrices("bias", "attr_2")
    metrics_flipped = mult_metric.group_confusion_matrices("bias", "attr_2", return_by_metric=False)

    assert "precision" in metrics.keys()
    assert len(metrics.keys()) == 8
    assert len(metrics['f1'].keys()) == 2
    assert len(metrics_flipped[1].keys()) == 8
    assert metrics_flipped[1]['accuracy_rate'] == 0.9

def test_get_bias_cm_multiclass_requires_predvalue():
    mult_metric = BiasMetrics(MULTICLASS_MODEL)
    with pytest.raises(Exception):
        mult_metric.group_confusion_matrices("bias")

@responses.activate
def test_get_bias_pr_binary():
    responses.add(responses.POST, "http://mockbinarybasepath/models/ac55c7b4-2db7-4902-8cc3-969ed67a20c8_biasbinary/inferences/query",
        json = {
            "query_result": [
            {
                "bias": 1,
                "positive_rate": 0.15
            },
            {
                "bias": 2,
                "positive_rate": 0.14
            }
            ],
            "sampling_threshold": 1
        }
    )

    bin_metric = BiasMetrics(BINARY_MODEL)
    prs = bin_metric.group_positivity_rates("bias")
    prsalias = bin_metric.demographic_parity("bias")

    assert prs == prsalias    
    assert len(prs.keys()) == 2
    assert prs[2] == 0.14


def test_get_bias_pr_multiclass():
    mult_metric = BiasMetrics(MULTICLASS_MODEL)
    with pytest.raises(Exception):
        mult_metric.group_positivity_rates("bias")