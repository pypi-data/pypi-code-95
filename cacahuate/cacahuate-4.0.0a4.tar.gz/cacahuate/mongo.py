from datetime import datetime

import cacahuate.inputs
from cacahuate.jsontypes import MultiFormDict, Map

DATE_FIELDS = [
    'started_at',
    'finished_at',
]


def make_actor_map(execution_data):
    actor_map = {}

    for fg in execution_data['values']:
        ref = fg['ref']
        form_groups = []

        for frm in fg['forms']:
            current_form = {}

            for fld in frm['fields']:
                if fld['state'] != 'valid':
                    continue

                k = fld['name']
                current_form[k] = {
                      'actor': fld['actor']['identifier'],
                      'set_at': fld['set_at'],
                }

            form_groups.append(current_form)

        actor_map[ref] = form_groups

    return actor_map


def make_context(execution_data, config):
    ''' the proper and only way to get the ``'values'`` key out of
    an execution document from mongo. It takes care of the transformations
    needed for it to work in jinja templates and other contexts where the
    multiplicity of answers (multiforms) is relevant. '''
    context = {}

    try:
        for fg in execution_data['values']:
            ref = fg['ref']
            form_groups = []

            for frm in fg['forms']:
                current_form = {}

                for fld in frm['fields']:
                    if fld['state'] != 'valid':
                        continue

                    k = fld['name']
                    current_form[k] = fld['value']
                    current_form[f'get_{k}_display'] = (
                        fld.get('value_caption') or fld['value']
                    )

                form_groups.append(current_form)
            context[ref] = MultiFormDict(form_groups)
    except KeyError:
        pass

    context['_env'] = MultiFormDict([config.get('PROCESS_ENV') or {}])

    return context


def json_prepare(obj):
    ''' Takes ``obj`` from a mongo collection and returns it *as is* with two
    minor changes:

    * ``_id`` key removed
    * objects of type ``datetime`` converted to their string isoformat representation
    '''
    return {
        k: v if not isinstance(v, datetime) else v.isoformat()
        for k, v in obj.items()
        if k != '_id'
    }


def pointer_entry(node, name, description, execution, pointer, notified_users=None):
    return {
        'id': pointer.id,
        'started_at': pointer.started_at,
        'finished_at': pointer.finished_at,
        'execution': execution.to_json(),
        'node': {
            'id': node.id,
            'name': name,
            'description': description,
            'type': type(node).__name__.lower(),
        },
        'actors': Map([], key='identifier').to_json(),
        'actor_list': [],
        'process_id': execution.process_name,
        'notified_users': notified_users or [],
        'state': 'ongoing',
    }


def execution_entry(execution, state):
    return {
        '_type': 'execution',
        'id': execution.id,
        'name': execution.name,
        'process_name': execution.process_name,
        'description': execution.description,
        'status': execution.status,
        'started_at': execution.started_at,
        'finished_at': None,
        'state': state,
        'values': [{
            '_type': 'fgroup',
            'ref': '_execution',
            'forms': [{
                'ref': '_execution',
                'fields': [
                    {
                        **cacahuate.inputs.TextInput(
                            label='Id',
                            name='id',
                        ).to_json(),
                        'value': execution.id,
                        'value_caption': execution.id,
                        'state': 'valid',
                        'actor': {
                            '_type': 'user',
                            'identifier': '__system__',
                            'fullname': 'System',
                            'email': None,
                        },
                        'set_at': execution.started_at,
                    },
                    {
                        **cacahuate.inputs.TextInput(
                            label='Process Name',
                            name='process_name',
                        ).to_json(),
                        'value': execution.process_name,
                        'value_caption': execution.process_name,
                        'state': 'valid',
                        'actor': {
                            '_type': 'user',
                            'identifier': '__system__',
                            'fullname': 'System',
                            'email': None,
                        },
                        'set_at': execution.started_at,
                    },
                    {
                        **cacahuate.inputs.TextInput(
                            label='Name',
                            name='name',
                        ).to_json(),
                        'value': execution.name,
                        'value_caption': execution.name,
                        'state': 'valid',
                        'actor': {
                            '_type': 'user',
                            'identifier': '__system__',
                            'fullname': 'System',
                            'email': None,
                        },
                        'set_at': execution.started_at,
                    },
                    {
                        **cacahuate.inputs.TextInput(
                            label='Description',
                            name='description',
                        ).to_json(),
                        'value': execution.description,
                        'value_caption': execution.description,
                        'state': 'valid',
                        'actor': {
                            '_type': 'user',
                            'identifier': '__system__',
                            'fullname': 'System',
                            'email': None,
                        },
                        'set_at': execution.started_at,
                    },
                    {
                        **cacahuate.inputs.DatetimeInput(
                            label='Started At',
                            name='started_at',
                        ).to_json(),
                        'value': execution.started_at.isoformat(),
                        'value_caption': execution.started_at.isoformat(),
                        'state': 'valid',
                        'actor': {
                            '_type': 'user',
                            'identifier': '__system__',
                            'fullname': 'System',
                            'email': None,
                        },
                        'set_at': execution.started_at,
                    },
                ],
            }],
        }],
        'actors': {},
        'actor_list': [],
    }
