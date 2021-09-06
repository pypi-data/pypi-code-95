from copy import deepcopy

from ._utils import get_model_type

# %%
BEST_PARAMS = {
    'xgb':
        {
            # 'gmsc_monotone':
            #     {
            #         'learning_rate': 0.09194323538693933,
            #         'max_depth': 9,
            #         'min_child_weight': 87,
            #         'gamma': 35.7748388946367,
            #         'n_estimators': 100,
            #         'subsample': 0.7316541039804246,
            #         'colsample_bytree': 0.807913751796526,
            #         'scale_pos_weight': 41.056705086055004,
            #         'random_state': 2021,
            #         'monotone_constraints': (1, -1, 1, 1, -1, 1, 1, -1),
            #         'binary_threshold': .65,
            #     }
        },
}


def get_best_parameters_from_library(model_type, dataset):
    model_type = get_model_type(model_type)
    try:
        return BEST_PARAMS[model_type][dataset]
    except KeyError:
        return None


# %%
