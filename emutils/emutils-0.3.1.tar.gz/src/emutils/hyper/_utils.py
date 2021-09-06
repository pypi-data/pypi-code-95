from copy import deepcopy
import warnings

SEARCH_TYPES = ['grid', 'random', 'bayes']

SEARCH_TYPES_ALIASES = {
    'bayesian': 'bayes',
}

MODEL_TYPES_ALIASES = {
    'tree': 'dt',
    'decisiontree': 'dt',
    'adaboost': 'ada',
    'randomforest': 'rf',
    'xgboost': 'xgb',
}


def get_model_type(model_type):
    model_type = model_type.lower().replace('_', '')
    if model_type in MODEL_TYPES_ALIASES:
        return MODEL_TYPES_ALIASES[model_type]
    return model_type


def get_hyperopt_type(hyperopt_type):
    hyperopt_type = hyperopt_type.lower()
    if hyperopt_type in SEARCH_TYPES_ALIASES:
        return SEARCH_TYPES_ALIASES[hyperopt_type]
    if hyperopt_type not in SEARCH_TYPES:
        raise ValueError('Invalid search type.')
    return hyperopt_type


def add_random_state(space, model_type, random_state):
    if 'random_state' not in space:
        if random_state is not None:
            space = deepcopy(space)
        else:
            warnings.warn('No random state specified.')

        space['random_state'] = random_state
    return space

    # Add random if needed


def add_constant_parameters(space, constants):
    if constants is not None:
        space = deepcopy(space)
        for k, v in constants.items():
            space[k] = v
    return space
