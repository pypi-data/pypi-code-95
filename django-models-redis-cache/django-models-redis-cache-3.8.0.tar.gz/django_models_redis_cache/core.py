import datetime
import decimal
import json
import asyncio
import pytz
import redis
from copy import deepcopy
from typing import Callable

from django.db import models as django_models

from .utils import check_types, check_classes, get_ids_from_untyped_data
from .cache import default_cache_func, django_sync_to_async_list, django_sync_to_async_get


class RedisField:

    def __init__(self, default=None, choices=None, null=True):
        self.default = default
        self.value = None
        check_types(choices, dict)
        self.choices = choices
        self.null = null

    def _get_default_value(self):
        if self.default is not None:
            try:
                self.value = self.default()
            except BaseException as ex:
                self.value = self.default
        return self.value

    def _check_choices(self, value):
        if self.choices:
            if value not in self.choices.keys():
                raise Exception(f'{value} is not allowed. Allowed values: {", ".join(list(self.choices.keys()))}')

    def check_value(self):
        if self.value is None:
            self.value = self._get_default_value()
        if self.value is None:
            if self.null:
                self.value = 'null'
            else:
                raise Exception('null is not allowed')
        if self.value:
            self._check_choices(self.value)
        return self.value

    def clean(self):
        self.value = self.check_value()
        return self.value

    def deserialize_value_check_null(self, value, redis_root):
        if value == 'null':
            if not self.null:
                if redis_root.ignore_deserialization_errors:
                    print(
                        f'{datetime.datetime.now()} - {value} can not be deserialized like {self.__class__.__name__}, ignoring')
                else:
                    raise Exception(f'{value} can not be deserialized like {self.__class__.__name__}')

    def deserialize_value(self, value, redis_root):
        self.deserialize_value_check_null(value, redis_root)
        return value


class RedisString(RedisField):

    def clean(self):
        self.value = self.check_value()
        if self.value not in [None, 'null']:
            self.value = f'{self.value}'
        return super().clean()

    def deserialize_value(self, value, redis_root):
        self.deserialize_value_check_null(value, redis_root)
        if value != 'null':
            value = f'{value}'
        else:
            value = None
        return value


class RedisNumber(RedisField):

    def clean(self):
        self.value = self.check_value()
        if self.value not in [None, 'null']:
            check_types(self.value, (int, float))
        return super().clean()

    def deserialize_value(self, value, redis_root):
        self.deserialize_value_check_null(value, redis_root)
        if value != 'null':
            if type(value) == str:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            else:
                check_types(value, (int, float))
        else:
            value = None
        return value


class RedisId(RedisNumber):

    def __init__(self, *args, **kwargs):
        kwargs['null'] = False
        super().__init__(*args, **kwargs)


class RedisDateTime(RedisString):

    def clean(self):
        self.value = self.check_value()
        if self.value not in [None, 'null']:
            check_types(self.value, datetime.datetime)
            string_datetime = self.value.replace(tzinfo=pytz.UTC).strftime('%Y.%m.%d-%H:%M:%S+%Z')
            self.value = string_datetime
        return super().clean()

    def deserialize_value(self, value, redis_root):
        self.deserialize_value_check_null(value, redis_root)
        if value != 'null':
            value = super().deserialize_value(value, redis_root)
            check_types(value, str)
            value = datetime.datetime.strptime(value, '%Y.%m.%d-%H:%M:%S+%Z').replace(tzinfo=pytz.UTC)
        else:
            value = None
        return value


class RedisForeignKey(RedisNumber):

    def __init__(self, model=None, save_related_models=False, *args, **kwargs):
        allowed = True
        if model is None:
            allowed = False
        elif not issubclass(model, RedisModel):
            allowed = False
        if not allowed:
            raise Exception(f'{model.__name__} class is not RedisModel')
        else:
            self.model = model
            check_types(save_related_models, bool)
            self.save_related_models = save_related_models
            super().__init__(*args, **kwargs)

    def _get_id_from_instance_dict(self):
        if self.value:
            if type(self.value) == dict:
                if 'id' in self.value.keys():
                    self.value = self.value['id']
                else:
                    raise Exception(
                        f"{self.value} has no key 'id', please provide serialized instance or dict like " + "{'id': 1, ...}")
            else:
                raise Exception(
                    f'{self.value} type is not dict, please provide serialized instance or dict like ' + "{'id': 1, ...}")
        return self.value

    def clean(self):
        self.value = self.check_value()
        if self.value not in [None, 'null']:
            self.value = get_ids_from_untyped_data(self.value)[0]
        return super().clean()

    def deserialize_value(self, value, redis_root):
        self.deserialize_value_check_null(value, redis_root)
        if value != 'null':
            check_types(value, int)
            model_name = self.model.__name__
            instance_id = value
            value = redis_root._get_instances_by_key(f'{redis_root.prefix}:{model_name}:{instance_id}')[instance_id]
        else:
            value = None
        return value


class RedisJson(RedisField):

    def __init__(self, json_allowed_types=(list, dict), *args, **kwargs):
        self.json_allowed_types = json_allowed_types
        super().__init__(*args, **kwargs)

    def set_json_allowed_types(self, allowed_types):
        self.json_allowed_types = allowed_types
        return self.json_allowed_types

    def clean(self):
        self.value = self.check_value()
        if self.value not in [None, 'null']:
            check_types(self.value, self.json_allowed_types)
            json_string = json.dumps(self.value)
            self.value = json_string
        return super().clean()

    def deserialize_value(self, value, redis_root):
        self.deserialize_value_check_null(value, redis_root)
        if value != 'null':
            check_types(value, str)
            value = json.loads(value)
            check_types(value, self.json_allowed_types)
        else:
            value = None
        return value


class RedisDict(RedisJson):

    def clean(self):
        self.set_json_allowed_types(dict)
        return super().clean()

    def deserialize_value(self, value, redis_root):
        self.set_json_allowed_types(dict)
        self.deserialize_value_check_null(value, redis_root)
        if value != 'null':
            value = super().deserialize_value(value, redis_root)
        else:
            value = None
        return value


class RedisList(RedisJson):

    def clean(self):
        self.set_json_allowed_types(list)
        return super().clean()

    def deserialize_value(self, value, redis_root):
        self.set_json_allowed_types(list)
        self.deserialize_value_check_null(value, redis_root)
        if value != 'null':
            value = super().deserialize_value(value, redis_root)
        else:
            value = None
        return value


class RedisManyToMany(RedisList):

    def __init__(self, model=None, save_related_models=False, *args, **kwargs):
        allowed = True
        if model is None:
            allowed = False
        elif not issubclass(model, RedisModel):
            allowed = False
        if not allowed:
            raise Exception(f'{model.__name__} class is not RedisModel')
        else:
            self.model = model
            check_types(save_related_models, bool)
            self.save_related_models = save_related_models
            super().__init__(*args, **kwargs)

    def clean(self):
        self.value = self.check_value()
        if self.value not in [None, 'null']:
            self.value = get_ids_from_untyped_data(self.value)
        return super().clean()

    def deserialize_value(self, value, redis_root):
        self.deserialize_value_check_null(value, redis_root)
        if value != 'null':
            value = super().deserialize_value(value, redis_root)
            model_name = self.model.__name__
            isntances_ids = value
            instances_list = []
            for instance_id in isntances_ids:
                instances = redis_root._get_instances_by_key(f'{redis_root.prefix}:{model_name}:{instance_id}')
                if len(instances.keys()):
                    instance = instances[instance_id]
                    instances_list.append(instance)
            value = instances_list

        return value


class RedisBool(RedisNumber):

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = {True: 'Yes', False: 'No'}
        super().__init__(*args, **kwargs)

    def clean(self):
        self.value = self.check_value()
        if self.value not in [None, 'null']:
            check_types(self.value, bool)
            self.value = int(self.value)
        return super().clean()

    def deserialize_value(self, value, redis_root):
        self.deserialize_value_check_null(value, redis_root)
        if value != 'null':
            check_types(value, int)
            value = bool(value)
        return value


class RedisDecimal(RedisString):

    def clean(self):
        self.value = self.check_value()
        if self.value not in [None, 'null']:
            check_types(self.value, (int, float, decimal.Decimal))
        return super().clean()

    def deserialize_value(self, value, redis_root):
        self.deserialize_value_check_null(value, redis_root)
        if value != 'null':
            value = decimal.Decimal(value)
        else:
            value = None
        return value


class RedisDate(RedisString):

    def clean(self):
        self.value = self.check_value()
        if self.value not in [None, 'null']:
            check_types(self.value, datetime.date)
            string_date = self.value.strftime('%Y.%m.%d+%Z')
            self.value = string_date
        return super().clean()

    def deserialize_value(self, value, redis_root):
        self.deserialize_value_check_null(value, redis_root)
        if value != 'null':
            value = super().deserialize_value(value, redis_root)
            check_types(value, str)
            value = datetime.datetime.strptime(value, '%Y.%m.%d+%Z').date()
        else:
            value = None
        return value


# class RedisDjangoForeignKey(RedisNumber):
#
#     def __init__(self, django_model=None, **kwargs):
#         super().__init__(**kwargs)
#         self.django_model = None
#         if not issubclass(django_model.__class__, django_models.Model):
#             raise Exception(f'{django_model.__class__.__name__} class is not django.db.models Model')
#         self.django_model = django_model
#
#     def _get_id_from_instance(self):
#         if issubclass(self.value.__class__, django_models.Model):
#             if isinstance(self.value, self.django_model):
#                 if self.value.id:
#                     django_instances_with_this_id = self.django_model.objects.filter(id=self.value.id)
#                     if django_instances_with_this_id:
#                         if len(django_instances_with_this_id) == 1:
#                             self.value = self.value.id
#                         elif len(django_instances_with_this_id) > 1:
#                             raise Exception(f'There are {len(django_instances_with_this_id)} django instances with this id')
#                         else:
#                             raise Exception(f'There are no django instances with this id')
#                     else:
#                         raise Exception(f'There are no django instances with this id')
#                 else:
#                     raise Exception(f'This django instance ({self.value}) has no attribute id')
#             else:
#                 raise Exception(f'{self.value} is not instance of {self.django_model}')
#         else:
#             raise Exception(f'{self.value} class is not django.db.models Model')
#         return self.value
#
#     def clean(self):
#         self.value = self.check_value()
#         if self.value not in [None, 'null']:
#             self.value = self._get_id_from_instance()
#         return super().clean()
#
#     def _get_instance_by_id(self, id):
#         instance = {
#             'id': id
#         }
#         django_instances_with_this_id = self.django_model.objects.filter(id=id)
#         if django_instances_with_this_id:
#             if len(django_instances_with_this_id) == 1:
#                 instance = django_instances_with_this_id[0]
#             elif len(django_instances_with_this_id) > 1:
#                 raise Exception(f'There are {len(django_instances_with_this_id)} django instances with this id')
#             else:
#                 raise Exception(f'There are no django instances with this id')
#         else:
#             raise Exception(f'There are no django instances with this id')
#         return instance
#
#     def deserialize_value(self, value, redis_root):
#         self.deserialize_value_check_null(value, redis_root)
#         if value != 'null':
#             value = super().deserialize_value(value, redis_root)
#             check_types(value, int)
#             value = self._get_instance_by_id(value)
#         return value


class RedisRoot:

    def __init__(
            self,
            connection_pool=None,
            prefix='redis_test',
            async_db_requests_limit=50,
            ignore_deserialization_errors=True,
            save_consistency=False,
            economy=False,
    ):
        self.registered_models = []
        self.registered_django_models = {}
        if type(prefix) == str:
            self.prefix = prefix
        else:
            print(
                f'{datetime.datetime.now()} - Prefix {prefix} is type of {type(prefix)}, allowed only str, using default prefix "redis_test"')
            self.prefix = 'redis_test'
        self.connection_pool = self._get_connection_pool(connection_pool)
        self.async_db_requests_limit = async_db_requests_limit
        self.ignore_deserialization_errors = ignore_deserialization_errors
        self.save_consistency = save_consistency
        self.economy = economy

    @property
    def redis_instance(self):
        redis_instance = redis.Redis(connection_pool=self.connection_pool)
        return redis_instance

    @property
    def cached_models(self):
        return self.registered_models

    def _get_django_models_to_cache(self):
        django_models_to_cache = {}
        for django_model, django_model_cache_data in self.registered_django_models.items():
            now = datetime.datetime.now()
            to_cache_in = django_model_cache_data['to_cache_in']
            cache_conf = django_model_cache_data['cache_conf']
            if to_cache_in <= now and cache_conf['enabled']:
                django_models_to_cache[django_model] = cache_conf
                ttl = cache_conf['ttl']
                now = datetime.datetime.now()
                self.registered_django_models[django_model] = {
                    'to_cache_in': now + datetime.timedelta(seconds=ttl),
                    'cache_conf': cache_conf
                }
        if django_models_to_cache:
            print(
                f"{datetime.datetime.now()} - {', '.join([str(model) for model in django_models_to_cache.keys()])} will be cached now...")
        return django_models_to_cache

    def get_cache_conf(self, django_model):
        if django_model in self.registered_django_models.keys():
            cache_conf = self.registered_django_models[django_model]['cache_conf']
            return cache_conf
        else:
            cached_cache_conf = self.redis_instance.get(f'{self.prefix}:cache_confs:{django_model.__name__}')
            if cached_cache_conf:
                cache_conf = json.loads(cached_cache_conf)
            else:
                cache_conf = {
                    'enabled': False,
                    'ttl': 60 * 5,
                    'save_related_models': True,
                    'exclude_fields': [],
                    'filter_by': {},
                    'write_to_django': False,
                    'delete': False,
                }
            return cache_conf

    def django_to_cache(
            self,
    ):
        async def run_django_to_cache(
                redis_root,
                django_model,
                django_fields,
                cache_conf,
        ):
            filter_by = cache_conf['filter_by']
            if filter_by:
                django_instances = await django_sync_to_async_list(django_model.objects.filter, filter_by)
            else:
                django_instances = await django_sync_to_async_list(django_model.objects.all)
            async_chunk_size = redis_root.async_db_requests_limit
            async_tasks = []
            completed = 0
            to_complete = len(django_instances)
            if django_instances:

                for django_instance in django_instances:
                    async_tasks.append(
                        redis_root.update_or_create_redis_instance_from_django_instance(
                            django_instance,
                            django_fields,
                            cache_conf,
                        )
                    )
                    completed += 1
                    if len(async_tasks) == async_chunk_size or completed == to_complete:
                        await asyncio.gather(*async_tasks)
                        async_tasks = []
                        print(
                            f'{datetime.datetime.now()} - '
                            f'Written {completed} {django_model} instances from django to cache')

            if cache_conf['delete']:
                async def check_if_need_to_delete_redis_instance(redis_root, django_instances_ids, redis_instance):
                    if 'django_id' in redis_instance.keys():
                        if redis_instance['django_id'] not in django_instances_ids:
                            redis_root.delete(django_model, redis_instance)

                django_instances_ids = [django_instance.id for django_instance in django_instances]
                all_redis_instances = redis_root.get(django_model)
                async_tasks = [
                    check_if_need_to_delete_redis_instance(redis_root, django_instances_ids, redis_instance)
                    for redis_instance in all_redis_instances
                ]

                await asyncio.gather(*async_tasks)

            print(f'{datetime.datetime.now()} - '
                  f'Deleted {django_model} instances from cache')

        for django_model, django_model_cache_data in self.registered_django_models.items():
            cache_conf = django_model_cache_data['cache_conf']
            django_fields = django_model._meta.get_fields()
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                run_django_to_cache(
                    self,
                    django_model,
                    django_fields,
                    cache_conf,
                )
            )

    def django_fields_to_redis_fields(self, django_model, save_related_models, exclude_fields):
        redis_fields = {}
        for django_field in django_model._meta.get_fields():
            django_field_name = django_field.name
            allowed = True
            if exclude_fields:
                allowed = (django_field.name not in exclude_fields)
            if allowed:
                if django_field.name in ['id', 'pk']:
                    django_field_name = 'django_id'
                    redis_field = RedisNumber(null=True)
                else:
                    redis_field = self.django_field_to_redis_field(django_field, save_related_models, exclude_fields)
                if redis_field:
                    redis_fields[django_field_name] = redis_field
        return redis_fields

    def create_redis_model_from_redis_fields(self, django_model, redis_fields, register=True):
        new_redis_model = type(django_model.__name__, (RedisModel,), redis_fields)
        if register:
            self.register_models([new_redis_model])
        return new_redis_model

    def django_field_to_redis_field(self, django_field, save_related_models, exclude_fields):

        field_mapping = {
            django_models.BooleanField: RedisBool,
            django_models.DecimalField: RedisDecimal,
            django_models.PositiveSmallIntegerField: RedisNumber,
            django_models.BigAutoField: RedisNumber,
            django_models.BigIntegerField: RedisNumber,
            django_models.DateField: RedisDate,
            django_models.DateTimeField: RedisDateTime,
            django_models.EmailField: RedisString,
            django_models.IntegerField: RedisNumber,
            django_models.GenericIPAddressField: RedisString,
            django_models.JSONField: RedisJson,
            django_models.PositiveBigIntegerField: RedisNumber,
            django_models.PositiveIntegerField: RedisNumber,
            django_models.SmallAutoField: RedisNumber,
            django_models.SmallIntegerField: RedisNumber,
            django_models.TextField: RedisString,
            django_models.URLField: RedisString,
            django_models.UUIDField: RedisString,
            django_models.ForeignKey: RedisForeignKey,
            django_models.ManyToManyField: RedisManyToMany
        }

        if django_field.__class__.__name__.endswith('Rel'):
            redis_field = None
        elif django_field.__class__ in field_mapping.keys():
            redis_field = field_mapping[django_field.__class__]
        else:
            redis_field = RedisString

        if redis_field:
            redis_field_class = type(
                django_field.__class__.__name__,
                (redis_field,),
                {}
            )

            redis_field_params = self.django_field_params_to_redis_field_params(django_field,
                                                                                save_related_models, exclude_fields)
            redis_field = redis_field_class(**redis_field_params)
        return redis_field

    def django_field_params_to_redis_field_params(self, django_field, save_related_models, exclude_fields):
        allowed_params = ['default', 'choices', 'remote_field']
        allowed_redis_params = {}
        django_field_params = django_field.__dict__.copy()
        for django_field_param_name in django_field_params.keys():
            redis_field_param_name = django_field_param_name
            if django_field_param_name in allowed_params:
                value = getattr(django_field, django_field_param_name)
                if value in [django_models.NOT_PROVIDED, django_models.Empty, django_models.BLANK_CHOICE_DASH, None]:
                    value = None
                if django_field_param_name == 'choices':
                    real_value = {}
                    if value is not None:
                        for choice in value:
                            real_value[choice[0]] = choice[1]
                    else:
                        real_value = None
                    value = real_value
                    allowed_redis_params[redis_field_param_name] = value
                elif django_field_param_name == 'remote_field':
                    redis_field_param_name = 'model'
                    if value is not None:
                        value = value.model
                        if value is not None:
                            value = self.get_or_create_redis_model_from_django_model(value)
                            if value is not None:
                                allowed_redis_params[redis_field_param_name] = value
                                allowed_redis_params['save_related_models'] = save_related_models
                else:
                    allowed_redis_params[redis_field_param_name] = value
        return allowed_redis_params

    def update_redis_model_from_redis_fields(self, django_model, existing_redis_model, redis_fields):
        new_redis_model = self.create_redis_model_from_redis_fields(django_model, redis_fields, False)
        new_registered_models = []
        for redis_model in self.registered_models:
            if redis_model == existing_redis_model:
                new_registered_models.append(new_redis_model)
            else:
                new_registered_models.append(redis_model)
        self.registered_models = new_registered_models
        return new_redis_model

    def get_or_create_redis_model_from_django_model(self, django_model):
        cache_conf = self.get_cache_conf(django_model)
        save_related_models = cache_conf['save_related_models']
        exclude_fields = cache_conf['exclude_fields']
        redis_fields = self.django_fields_to_redis_fields(django_model, save_related_models, exclude_fields)
        registered_models_names = [model.__name__ for model in self.registered_models]
        if django_model.__name__ in registered_models_names:
            existing_redis_model_index = registered_models_names.index(django_model.__name__)
            existing_redis_model = self.registered_models[existing_redis_model_index]
            new_redis_model = self.update_redis_model_from_redis_fields(django_model, existing_redis_model,
                                                                        redis_fields)
        else:
            new_redis_model = self.create_redis_model_from_redis_fields(django_model, redis_fields)
        return new_redis_model

    def check_cache(self):
        django_models_to_cache = self._get_django_models_to_cache()
        for django_model, cache_conf in django_models_to_cache.items():
            print(f'{datetime.datetime.now()} - '
                  f'Start caching {django_model}'
                  f'\n')

            redis_model = self.get_or_create_redis_model_from_django_model(django_model)
            default_cache_func(
                self,
                django_model,
                cache_conf,
            )
            print(f'{datetime.datetime.now()} - '
                  f'Cached {django_model} successfully'
                  f'\n\n\n')

    def fast_get_keys_values(self, string):
        keys = list(self.redis_instance.keys(string))
        values = self.redis_instance.mget(keys)
        results = dict(zip(keys, values))
        return results

    def _get_connection_pool(self, connection_pool):
        if isinstance(connection_pool, redis.ConnectionPool):
            connection_pool.connection_kwargs['decode_responses'] = True
            self.connection_pool = connection_pool
        else:
            print(
                f'{datetime.datetime.now()} - {self.__class__.__name__}: No connection_pool provided, trying default config...')
            default_host = 'localhost'
            default_port = 6379
            default_db = 0
            try:
                connection_pool = redis.ConnectionPool(
                    decode_responses=True,
                    host=default_host,
                    port=default_port,
                    db=default_db,
                )
                self.connection_pool = connection_pool
            except BaseException as ex:
                raise Exception(
                    f'Default config ({default_host}:{default_port}, db={default_db}) failed, please provide connection_pool to {self.__class__.__name__}')
        return self.connection_pool

    def register_models(self, models_list):
        for model in models_list:
            if issubclass(model, RedisModel):
                if model not in self.registered_models:
                    self.registered_models.append(model)
            else:
                raise Exception(f'{model.__name__} class is not RedisModel')

    def check_cache_conf(self, model, user_cache_conf=None):
        name = model.__name__

        cache_conf = {
            'enabled': False,
            'ttl': 60 * 5,
            'save_related_models': True,
            'exclude_fields': [],
            'filter_by': {},
            'write_to_django': False,
            'delete': False,
        }
        if user_cache_conf is not None:
            if type(user_cache_conf) == dict:
                if 'enabled' in user_cache_conf.keys():
                    if type(user_cache_conf['enabled']) == bool:
                        cache_conf['enabled'] = user_cache_conf['enabled']
                    else:
                        raise Exception(f'{name} -> cache config -> enabled must be bool')
                if 'ttl' in user_cache_conf.keys():
                    if type(user_cache_conf['ttl']) == int:
                        cache_conf['ttl'] = user_cache_conf['ttl']
                    else:
                        raise Exception(f'{name} -> cache config -> ttl must be int')
                if 'save_related_models' in user_cache_conf.keys():
                    if type(user_cache_conf['save_related_models']) == bool:
                        cache_conf['save_related_models'] = user_cache_conf['save_related_models']
                    else:
                        raise Exception(f'{name} -> cache config -> save_related_models must be int')
                if 'exclude_fields' in user_cache_conf.keys():
                    if type(user_cache_conf['exclude_fields']) == list:
                        if all([
                            (type(field) == str)
                            for field in user_cache_conf['exclude_fields']
                        ]):
                            cache_conf['exclude_fields'] = user_cache_conf['exclude_fields']
                        else:
                            raise Exception(f'{name} -> cache config -> exclude_fields -> all fields must be strings')
                    else:
                        raise Exception(f'{name} -> cache config -> exclude_fields must be list')
                if 'filter_by' in user_cache_conf.keys():
                    if type(user_cache_conf['filter_by']) == dict:
                        if all([
                            (type(field_name) == str)
                            for field_name in user_cache_conf['filter_by'].keys()
                        ]):
                            cache_conf['filter_by'] = user_cache_conf['filter_by']
                        else:
                            raise Exception(f'{name} -> cache config -> filter_by -> all keys must be strings')
                    else:
                        raise Exception(f'{name} -> cache config -> filter_by must be dict')
                if 'write_to_django' in user_cache_conf.keys():
                    if type(user_cache_conf['write_to_django']) == bool:
                        cache_conf['write_to_django'] = user_cache_conf['write_to_django']
                    else:
                        raise Exception(f'{name} -> cache config -> write_to_django must be bool')
                if 'delete' in user_cache_conf.keys():
                    if type(user_cache_conf['delete']) == bool:
                        cache_conf['delete'] = user_cache_conf['delete']
                    else:
                        raise Exception(f'{name} -> cache config -> delete must be bool')
            else:
                raise Exception(f'{name} -> cache config must be dict')

        return cache_conf

    async def update_or_create_redis_instance_from_django_instance(
            self,
            django_instance,
            django_fields,
            cache_conf,
    ):
        def check_fields_need_to_update(
                redis_instance,
                redis_dict,
        ):
            fields_to_update = {}
            for field_name, field_value in redis_dict.items():
                if field_name not in redis_instance.keys():
                    fields_to_update[field_name] = field_value
                else:
                    if redis_instance[field_name] != field_value:
                        fields_to_update[field_name] = field_value
            return fields_to_update

        django_instance_model = django_instance.__class__
        old_redis_instance = self.get(django_instance_model, django_id=django_instance.id)
        redis_dict = await self.django_instance_to_redis_params(
            django_instance,
            django_fields,
            cache_conf,
        )

        if not old_redis_instance:
            fields_to_create = redis_dict
            redis_instance = self.create(
                django_model=django_instance_model,
                django_id=django_instance.id,
                **fields_to_create
            )
            result_redis_instance_id = redis_instance['id']
        else:
            old_redis_instance = old_redis_instance[0]
            fields_to_update = check_fields_need_to_update(
                old_redis_instance,
                redis_dict,
            )
            if fields_to_update:
                self.update(django_instance_model, old_redis_instance,
                            **fields_to_update
                            )
                redis_instance = self.get(django_instance_model, django_id=django_instance.id)[0]
                result_redis_instance_id = redis_instance['id']
            else:
                result_redis_instance_id = old_redis_instance['id']

        return result_redis_instance_id

    async def django_instance_to_redis_params(
            self,
            django_instance,
            django_fields,
            cache_conf,
    ):

        redis_params = {}
        exclude_fields = cache_conf['exclude_fields']

        for i, django_field in enumerate(django_fields):
            if not django_field.__class__.__name__.endswith('Rel'):
                django_field_name = django_field.name
                allowed = True
                if exclude_fields:
                    allowed = (django_field.name not in exclude_fields)
                if allowed:
                    if django_field.name not in ['id', 'pk']:
                        redis_param = await self.django_instance_field_to_redis_value(
                            django_instance,
                            django_field,
                            cache_conf,
                        )
                        if redis_param:
                            redis_params[django_field_name] = redis_param

        return redis_params

    async def django_instance_field_to_redis_value(
            self,
            django_instance,
            django_field,
            cache_conf,
    ):

        save_related_models = cache_conf['save_related_models']
        django_field_value = await django_sync_to_async_get(django_instance, django_field.name)
        redis_value = django_field_value
        if django_field.__class__ == django_models.ForeignKey:
            if django_field_value is None:
                redis_value = None
            else:
                django_foreign_key_instance = django_field_value
                if save_related_models:
                    if django_foreign_key_instance:
                        django_instance_model = django_foreign_key_instance.__class__
                        redis_foreign_key_instance = await self.get_or_create_redis_instance_from_django_instance(
                            django_foreign_key_instance,
                            cache_conf,
                        )
                        redis_value = redis_foreign_key_instance
                    else:
                        redis_value = None
                else:
                    redis_value = django_foreign_key_instance.id
        elif django_field.__class__ == django_models.ManyToManyField:
            if save_related_models:
                django_many_to_many_instances = await django_sync_to_async_list(django_field_value.all)
                if len(django_many_to_many_instances):
                    django_instance_model = django_many_to_many_instances[0].__class__
                    redis_value = [
                        await self.get_or_create_redis_instance_from_django_instance(
                            django_many_to_many_instance,
                            cache_conf,
                        )
                        for django_many_to_many_instance in django_many_to_many_instances
                    ]
                else:
                    redis_value = []
            else:
                redis_value = [
                    django_many_to_many_instance.id
                    for django_many_to_many_instance in django_many_to_many_instances
                ]
        elif django_field.__class__.__name__.startswith('Image') or django_field.__class__.__name__.startswith('File'):
            try:
                redis_value = django_field_value.file.path
            except:
                redis_value = None
        return redis_value

    async def get_or_create_redis_instance_from_django_instance(
            self,
            django_instance,
            cache_conf,
    ):
        django_fields = django_instance.__class__._meta.get_fields()
        django_instance_model = django_instance.__class__
        redis_instance = self.get(django_instance_model, django_id=django_instance.id)

        if not redis_instance:
            redis_dict = await self.django_instance_to_redis_params(
                django_instance,
                django_fields,
                cache_conf,
            )
            redis_instance = self.create(
                django_model=django_instance_model,
                django_id=django_instance.id,
                **redis_dict
            )
        else:
            redis_instance = redis_instance[0]

        return redis_instance

    def register_django_models(self, models_dict):
        for model, user_cache_conf in models_dict.items():
            if issubclass(model, django_models.Model):
                if model not in self.registered_django_models.keys():
                    cache_conf = self.check_cache_conf(model, user_cache_conf)
                    self.redis_instance.set(f'{self.prefix}:cache_confs:{model.__name__}', json.dumps(cache_conf))
                    self.registered_django_models[model] = {
                        'cache_conf': cache_conf,
                        'to_cache_in': datetime.datetime.now()
                    }
            else:
                raise Exception(f'{model.__name__} class is not django_models.Model')

    def _get_registered_model_by_name(self, model_name):
        found = False
        model = None
        for registered_model in self.registered_models:
            if registered_model.__name__ == model_name:
                found = True
                model = registered_model
                break
        if not found:
            if self.ignore_deserialization_errors:
                print(f'{datetime.datetime.now()} - {model_name} not found in registered models, ignoring')
                model = model_name
            else:
                raise Exception(f'{model_name} not found in registered models')
        return model

    def _get_field_instance_by_name(self, field_name, model):
        field_instance = None
        try:
            if field_name == 'id':
                field_instance = getattr(model, field_name)
            else:
                field_instance = getattr(model, field_name)
        except BaseException as ex:
            if self.ignore_deserialization_errors:
                print(
                    f'{datetime.datetime.now()} - {model.__name__} has no field {field_name}, ignoring deserialization')
                field_instance = field_name
            else:
                raise Exception(f'{model.__name__} has no field {field_name}')
        return field_instance

    def _deserialize_value_by_field_instance(self, raw_value, field_instance):
        value = field_instance.deserialize_value(raw_value, self)
        try:
            pass
        except BaseException as ex:
            if self.ignore_deserialization_errors:
                print(
                    f'{datetime.datetime.now()} - {raw_value} can not be deserialized like {field_instance.__class__.__name__}, ignoring')
                value = raw_value
            else:
                raise Exception(f'{raw_value} can not be deserialized like {field_instance.__class__.__name__}')
        return value

    def deserialize_value(self, raw_value, model_name, field_name):
        value = raw_value
        saved_model = self._get_registered_model_by_name(model_name)
        if issubclass(saved_model, RedisModel):
            saved_field_instance = self._get_field_instance_by_name(field_name, saved_model)
            if issubclass(saved_field_instance.__class__, RedisField):
                value = self._deserialize_value_by_field_instance(raw_value, saved_field_instance)
        return value

    def _return_with_format(self, instances, return_dict=False):
        if return_dict:
            return instances
        else:
            instances_list = [
                {
                    'id': instance_id,
                    **instance_fields
                }
                for instance_id, instance_fields in instances.items()
            ]
            return instances_list

    def _check_fields_existence(self, model, instances_with_allowed, filters):
        checked_instances = {}
        fields = model.__dict__
        cleaned_fields = {}
        for field_name, field in fields.items():
            if not field_name.startswith('__'):
                cleaned_fields[field_name] = field
        if 'id' not in cleaned_fields.keys():
            cleaned_fields['id'] = RedisString(null=True)
        fields = cleaned_fields
        for instance_id, instance_fields in instances_with_allowed.items():
            checked_instances[instance_id] = {}
            for field_name, field in fields.items():
                if field_name in instance_fields.keys():
                    checked_instances[instance_id][field_name] = instance_fields[field_name]
                else:
                    field.value = None
                    cleaned_value = field.clean()
                    allowed = self._filter_field_name(model, field_name, cleaned_value, filters)
                    checked_instances[instance_id][field_name] = {
                        'value': cleaned_value,
                        'allowed': allowed
                    }
        return checked_instances

    def _filter_value(self, value, filter_type, filter_by):
        allowed = True
        if filter_type == 'exact':
            if value != filter_by:
                allowed = False
        elif filter_type == 'iexact':
            if value.lower() != filter_by.lower():
                allowed = False
        elif filter_type == 'contains':
            if filter_by not in value:
                allowed = False
        elif filter_type == 'icontains':
            if filter_by.lower() not in value.lower():
                allowed = False
        elif filter_type == 'in':
            if value not in filter_by:
                allowed = False
        elif filter_type == 'gt':
            if value <= filter_by:
                allowed = False
        elif filter_type == 'gte':
            if value < filter_by:
                allowed = False
        elif filter_type == 'lt':
            if value >= filter_by:
                allowed = False
        elif filter_type == 'lte':
            if value > filter_by:
                allowed = False
        elif filter_type == 'startswith':
            if not value.startswith(filter_by):
                allowed = False
        elif filter_type == 'istartswith':
            if not value.lower().startswith(filter_by.lower()):
                allowed = False
        elif filter_type == 'endswith':
            if not value.endswith(filter_by):
                allowed = False
        elif filter_type == 'iendswith':
            if not value.lower().endswith(filter_by.lower()):
                allowed = False
        elif filter_type == 'range':
            if value not in range(filter_by):
                allowed = False
        return allowed

    def _split_filtering(self, filter_param):
        filter_field_name, filter_type = filter_param, 'exact'
        if '__' in filter_param:
            filter_param_split = filter_param.split('__')
            if filter_param_split[-1] in ['exact', 'iexact', 'contains', 'icontains', 'in', 'gt', 'gte', 'lt', 'lte',
                                          'startswith', 'istartswith', 'endswith', 'iendswith', 'range']:
                fields_to_filter = filter_param_split[:-1]
                filter_type = filter_param_split[-1]
            else:
                fields_to_filter = filter_param_split
        else:
            fields_to_filter = [filter_field_name]
        return fields_to_filter, filter_type

    def _filter(self, value, fields_to_filter, filter_type, filter_by):
        for field_to_filter in fields_to_filter:
            try:
                value = value[field_to_filter]
            except BaseException as ex:
                print(f'Exception: {ex}\n'
                      f'Info: {field_to_filter}, {value}\n'
                      f'Maybe: deep filtering is not included on this model')
                value = None
        if isinstance(value, datetime.datetime) and isinstance(filter_by, datetime.datetime):
            value = value.replace(tzinfo=pytz.UTC)
            filter_by = filter_by.replace(tzinfo=pytz.UTC)
        allowed = self._filter_value(value, filter_type, filter_by)
        return allowed

    def _filter_field_name(self, redis_model, field_name, value, raw_filters):
        allowed_list = [True]
        for filter_param in raw_filters.keys():
            filter_by = raw_filters[filter_param]
            fields_to_filter, filter_type = self._split_filtering(filter_param)
            if field_name == fields_to_filter[0]:
                fields_to_filter = fields_to_filter[1:]
                print(value, fields_to_filter, filter_type, filter_by)
                allowed_list.append(self._filter(value, fields_to_filter, filter_type, filter_by))
        allowed = all(allowed_list)
        return allowed

    def _get_instances_by_key(self, key):
        raw_instances = self.fast_get_keys_values(key)
        instances = {}
        for instance_key, fields_json in raw_instances.items():
            prefix, model_name, instance_id = instance_key.split(':')
            instance_id = int(instance_id)
            fields_dict = json.loads(fields_json)
            for field_name, raw_value in fields_dict.items():
                value = self.deserialize_value(raw_value, model_name, field_name)
                if instance_id not in instances.keys():
                    instances[instance_id] = {}
                instances[instance_id][field_name] = value
        return instances

    def _get_all_stored_model_instances(self, redis_model, filters=None):
        redis_model_name = redis_model.__name__
        instances = self._get_instances_by_key(f'{self.prefix}:{redis_model_name}:*')
        instances_with_allowed = {}
        for instance_id, instance_fields in instances.items():
            for field_name, field_value in instance_fields.items():
                allowed = self._filter_field_name(redis_model, field_name, field_value, filters)
                if instance_id not in instances_with_allowed.keys():
                    instances_with_allowed[instance_id] = {}
                instances_with_allowed[instance_id][field_name] = {
                    'value': field_value,
                    'allowed': allowed
                }
        return instances_with_allowed

    def _get_instances_from_instances_with_allowed(self, instances_with_allowed):
        instances = {}
        for instance_id, instance_fields in instances_with_allowed.items():
            instance_allowed = all([
                instance_field_data['allowed']
                for instance_field_data in instance_fields.values()
            ])
            if instance_allowed and instance_id not in instances.keys():
                instances[instance_id] = {
                    instance_field_name: instance_field_data['value']
                    for instance_field_name, instance_field_data in instance_fields.items()
                }
        return instances

    def _get_all_redis_model_instances(self, redis_model, filters=None):
        if filters is None:
            filters = {}
        instances_with_allowed = self._get_all_stored_model_instances(redis_model, filters)
        if self.save_consistency:
            instances_with_allowed = self._check_fields_existence(redis_model, instances_with_allowed, filters)
        instances = self._get_instances_from_instances_with_allowed(instances_with_allowed)
        return instances

    def get_by_redis_model(self, redis_model, return_dict=False, **filters):
        instances = self._get_all_redis_model_instances(redis_model, filters)
        return self._return_with_format(instances, return_dict)

    def get(self, django_model, return_dict=False, **filters):
        redis_model = self.get_or_create_redis_model_from_django_model(django_model)
        result = self.get_by_redis_model(redis_model, return_dict, **filters)
        return result

    def order(self, instances, field_name):
        reverse = False
        if field_name.startswith('-'):
            reverse = True
            field_name = field_name[1:]

        return sorted(instances, key=(lambda instance: instance[field_name]), reverse=reverse)

    def _get_ttl_by_update_params(self, field, saved_model, renew_ttl, new_ttl):
        field_ttl = None
        if new_ttl is not None:
            check_types(new_ttl, (int, float))
            field_ttl = new_ttl
        else:
            if renew_ttl:
                field_ttl = saved_model.get_field_ttl(field)
        return field_ttl

    def _update_by_instance_key(self, instance_key, fields_to_update, renew_ttl, new_ttl):
        updated_data = None
        prefix, model_name, instance_id = instance_key.split(':')
        redis_model = self._get_registered_model_by_name(model_name)
        instance_id = int(instance_id)
        instance_data_json = self.redis_instance.get(instance_key)
        instance_data = json.loads(instance_data_json)
        data_to_write = {}
        for field_name, field_data in instance_data.items():
            saved_field_instance = self._get_field_instance_by_name(field_name, redis_model)
            if field_name in fields_to_update.keys():
                saved_field_instance.value = fields_to_update[field_name]
                cleaned_value = saved_field_instance.clean()
            else:
                cleaned_value = field_data
            if instance_key not in data_to_write.keys():
                data_to_write[instance_key] = {}
            data_to_write[instance_key][field_name] = cleaned_value
        for instance_key, fields_to_write in data_to_write.items():
            ttl = None
            if renew_ttl:
                ttl = redis_model.get_model_ttl()
            elif new_ttl:
                ttl = new_ttl
            fields_to_write_json = json.dumps(fields_to_write)
            self.redis_instance.set(instance_key, fields_to_write_json, ex=ttl)
            updated_data = {
                'redis_model': redis_model,
                'id': instance_id
            }
        return updated_data

    def _get_allowed_redis_model_params(self, redis_model, params):
        redis_model_fields_names = redis_model.__dict__.keys()
        allowed_param_names = list(filter(
            lambda param_name: param_name in redis_model_fields_names and not param_name.startswith('__'),
            params.keys()
        ))
        result_params = {param_name: params[param_name] for param_name in params.keys() if
                         param_name in allowed_param_names}
        return result_params

    def update(self, django_model, instances=None, return_dict=False, renew_ttl=False, new_ttl=None,
               **fields_to_update):
        model = self.get_or_create_redis_model_from_django_model(django_model)
        model_name = model.__name__
        updated_datas = []
        if instances is None:
            for key in self.redis_instance.keys(f'{self.prefix}:{model_name}:*'):
                updated_data = self._update_by_instance_key(key, fields_to_update, renew_ttl, new_ttl)
                if updated_data is not None:
                    updated_datas.append(updated_data)
        else:
            ids_to_update = get_ids_from_untyped_data(instances)
            for instance_id in ids_to_update:
                for key in self.redis_instance.keys(f'{self.prefix}:{model_name}:{instance_id}'):
                    updated_data = self._update_by_instance_key(key, fields_to_update, renew_ttl, new_ttl)
                    if updated_data is not None:
                        updated_datas.append(updated_data)
        updated_instances = {}
        for updated_data in updated_datas:
            updated_redis_model = updated_data['redis_model']
            updated_id = updated_data['id']
            if self.economy:
                updated_instances[updated_id] = {'id': updated_id}
            else:
                updated_instance_qs = self.get_by_redis_model(updated_redis_model, id=updated_id)
                updated_instance = updated_instance_qs[0]
                updated_instances[updated_id] = updated_instance
        result = self._return_with_format(updated_instances, return_dict)
        return result

    def _delete_by_key(self, key):
        self.redis_instance.delete(key)

    def delete(self, django_model, instances=None):
        model = self.get_or_create_redis_model_from_django_model(django_model)
        model_name = model.__name__
        if instances is None:
            for key in self.redis_instance.keys(f'{self.prefix}:{model_name}:*'):
                self._delete_by_key(key)
        else:
            ids_to_delete = get_ids_from_untyped_data(instances)
            for instance_id in ids_to_delete:
                for key in self.redis_instance.keys(f'{self.prefix}:{model_name}:{instance_id}'):
                    self._delete_by_key(key)

    # def get_id_from_django_id(self, django_model, django_id):
    #     model_name = django_model.__name__
    #     check_types(django_id, int)
    #     result = False
    #     for key in self.redis_instance.keys(f'{self.prefix}:{model_name}:*:django_id'):
    #         prefix, model_name, instance_id, field_name = key.split(':')
    #         value = int(self.redis_instance.get(key))
    #         if value == django_id:
    #             result = instance_id
    #     return result
    #
    # def is_instance_edited_by_id(self, django_model, instance_id):
    #     model_name = django_model.__name__
    #     check_types(instance_id, int)
    #     result = False
    #     for key in self.redis_instance.keys(f'{self.prefix}:{model_name}:{instance_id}:edited'):
    #         prefix, model_name, instance_id, field_name = key.split(':')
    #         value = bool(int(self.redis_instance.get(key)))
    #         result = value
    #     return result

    def create(self, django_model, **params):
        redis_model = self.get_or_create_redis_model_from_django_model(django_model)
        params = self._get_allowed_redis_model_params(redis_model, params)
        redis_instance = redis_model(redis_root=self, **params).save()
        return redis_instance


class RedisModel:
    id = RedisId()

    def __init__(self, redis_root=None, **kwargs):
        self.__model_data__ = {
            'redis_root': None,
            'name': None,
            'fields': None,
            'meta': {}
        }

        if isinstance(redis_root, RedisRoot):
            self.__model_data__['redis_root'] = redis_root
            self.__model_data__['name'] = self.__class__.__name__
            if self.__class__ != RedisModel:
                self._renew_fields()
                self.__model_data__['redis_root'].register_models([self.__class__])
                self._fill_fields_values(kwargs)

        else:
            raise Exception(f'{redis_root.__name__} type is {type(redis_root)}. Allowed only RedisRoot')

    def _check_meta_ttl(self, ttl):
        check_types(ttl, (int, float))
        return ttl

    def _set_meta(self, meta_fields):
        allowed_meta_fields_with_check_functions = {
            'ttl': self._check_meta_ttl,
        }
        for field_name, field_value in meta_fields.items():
            if field_name in allowed_meta_fields_with_check_functions.keys():
                cleaned_value = allowed_meta_fields_with_check_functions[field_name](field_value)
                if cleaned_value is not None:
                    self.__model_data__['meta'][field_name] = cleaned_value

    def _get_initial_model_field(self, field_name):
        name = self.__model_data__['name']
        if field_name in self.__class__.__dict__.keys():
            return deepcopy(self.__class__.__dict__[field_name])
        else:
            raise Exception(f'{name} has no field {field_name}')

    def _renew_fields(self):
        class_fields = self.__class__.__dict__.copy()
        fields = {}
        for field_name, field in class_fields.items():
            if not field_name.startswith('__'):
                if field_name == 'Meta':
                    self._set_meta(self.__class__.Meta.__dict__)
                else:
                    fields[field_name] = self._get_initial_model_field(field_name)
        self._get_new_id()
        if 'id' not in fields.keys():
            fields['id'] = self.id
        self.__model_data__['fields'] = fields

    def _fill_fields_values(self, field_values_dict):
        for name, value in field_values_dict.items():
            fields = self.__model_data__['fields']
            if name in fields.keys():
                self.__model_data__['fields'][name].value = value
            else:
                raise Exception(f'{self.__class__.__name__} has no field {name}')

    def _serialize_data(self):
        redis_root = self.__model_data__['redis_root']
        name = self.__model_data__['name']
        fields = self.__model_data__['fields']
        fields = dict(fields)
        instance_key = f'{redis_root.prefix}:{name}:{self.id.value}'
        deserialized_fields = {}
        cleaned_fields = {}
        for field_name, field in fields.items():
            if not field_name.startswith('__'):
                try:
                    cleaned_value = field.clean()
                    cleaned_fields[field_name] = cleaned_value
                    deserialized_value = redis_root.deserialize_value(cleaned_value, name, field_name)
                    deserialized_fields[field_name] = deserialized_value
                except BaseException as ex:
                    raise Exception(f'{ex} ({name} -> {field_name})')
        return instance_key, cleaned_fields, deserialized_fields

    def get_model_ttl(self):
        ttl = None
        meta = self.__model_data__['meta']
        if 'ttl' in meta.keys():
            ttl = meta['ttl']
        return ttl

    def _set_fields(self):
        instance_key, fields_dict, deserialized_fields = self._serialize_data()
        model_ttl = self.get_model_ttl()
        redis_root = self.__model_data__['redis_root']
        prefix, model_name, instance_id = instance_key.split(':')
        redis_instance = redis_root.redis_instance
        fields_json = json.dumps(fields_dict)
        redis_instance.set(instance_key, fields_json, ex=model_ttl)
        saved_instance = deserialized_fields
        return saved_instance

    def _get_new_id(self):
        redis_root = self.__model_data__['redis_root']
        instances_with_ids = redis_root.get_by_redis_model(self.__class__, return_dict=True)
        all_ids = [int(instance_id) for instance_id in list(instances_with_ids.keys())]
        if all_ids:
            max_id = max(all_ids)
        else:
            max_id = 0
        self.id.value = int(max_id + 1)

    def save(self):
        saved_instance = self._set_fields()
        return saved_instance

    def set(self, **fields_with_values):
        name = self.__model_data__['name']
        fields = self.__model_data__['fields']
        meta = self.__model_data__['meta']
        for field_name, value in fields_with_values.items():
            if field_name in fields.keys():
                field = fields[field_name]
                field.value = value
                return field.value
            elif field_name in meta.keys():
                meta[field_name] = value
                return meta[field_name]
            else:
                raise Exception(f'{name} has no field {field_name}')

    def get(self, field_name):
        name = self.__model_data__['name']
        fields = self.__model_data__['fields']
        meta = self.__model_data__['meta']
        if field_name in fields.keys():
            field = fields[field_name]
            return field.value
        elif field_name in meta.keys():
            return meta[field_name]
        else:
            raise Exception(f'{name} has no field {field_name}')
