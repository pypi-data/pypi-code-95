from hestia_earth.utils.tools import flatten, non_empty_list


def _filter_models(models: list):
    return non_empty_list([
        m.get('value') for m in models if isinstance(m, dict) and m.get('key') == 'emissions'
    ] + flatten([
        _filter_models(m) for m in models if isinstance(m, list)
    ]))


def _run_emission(emission_models: list):
    def run(emission: dict):
        term_id = emission.get('term', {}).get('@id')
        return {**emission, 'deleted': True} if term_id not in emission_models else None
    return run


def run(models: list, cycle: dict):
    emission_models = _filter_models(models)
    emissions = cycle.get('emissions', [])
    return non_empty_list(map(_run_emission(emission_models), emissions)) if len(emission_models) > 0 else []
