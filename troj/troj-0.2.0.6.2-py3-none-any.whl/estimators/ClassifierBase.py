from art import estimators



"""
This class is our base class that child classes will inherit metadata collection (and other functions in the future) as well as inherits from
ART's base estimator class for instantiation and attack. 
We'll have a class for major frameworks that will inherit this class

"""


class TrojClassifier(estimators.BaseEstimator):
    """
    Collects and returns the model's metadata
    :return dict: returns a dictionary of metadata related to the classifier passed to the ART estimator class
    """

    def get_classifier_meta(self):
        return {
            "model": str(self._model),
            "model_name": str(self._model.__class__.__name__),
            "input_shape": str(self._input_shape),
            "num_classes": str(self.nb_classes),
            "loss_func": str(self._loss),
            "channels_first": str(self._channels_first),
        }





