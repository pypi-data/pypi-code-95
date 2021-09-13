from django.conf import settings
from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models as django_models

class RedisQuerySet(django_models.query.QuerySet):

    def update(self, **kwargs):
        update_result = super().update(**kwargs)
        concrete_model = self.model._meta.concrete_model
        print(concrete_model)
        redis_root = get_redis_root()
        data_to_update = redis_root.get(self.model, django_id=concrete_model.id)
        redis_root.update(self.model, data_to_update, **kwargs)
        return self

    def create(self, **kwargs):
        create_result = super().create(**kwargs)
        concrete_model = self.model._meta.concrete_model
        print(concrete_model)
        existing_fields = {}
        for field in self.model._meta.get_fields():
            try:
                existing_fields[field.name] = getattr(concrete_model, field.name)
                print(field.name)
            except:
                pass
        redis_root = get_redis_root()
        print('existing_fields', existing_fields)
        redis_root.create(self.model, **existing_fields)
        return self

    def delete(self):
        concrete_model = self.model._meta.concrete_model
        delete_result = super().delete()
        print(concrete_model)
        redis_root = get_redis_root()
        data_to_delete = redis_root.get(self.model, django_id=concrete_model.id)
        redis_root.delete(self.model, data_to_delete)
        return self

class RedisUserObjectsManager(UserManager):
    def get_queryset(self):
        return RedisQuerySet(self.model)


class RedisObjectsManager(django_models.Manager):
    def get_queryset(self):
        return RedisQuerySet(self.model)


def get_redis_root():
    redis_root = getattr(settings, 'REDIS_ROOT', None)
    return redis_root


class DjangoRedisModel(django_models.Model):
    objects = RedisObjectsManager()

    def save(self, *args, **kwargs):
        save_result = super().save(*args, **kwargs)
        existing_fields = {}
        for field in self.__class__._meta.get_fields():
            try:
                existing_fields[field.name] = getattr(self, field.name)
            except:
                pass
        redis_root = get_redis_root()
        redis_root.create(self.__class__, **existing_fields)
        return self

    def delete(self, *args, **kwargs):
        django_id = self.id
        delete_result = super().delete(*args, **kwargs)
        redis_root = get_redis_root()
        redis_instance_qs = redis_root.get(self.__class__, django_id=django_id)
        if redis_instance_qs:
            redis_root.delete(self.__class__, redis_instance_qs)
        return self

    class Meta:
        abstract = True


class DjangoRedisUserModel(AbstractUser):
    objects = RedisUserObjectsManager()

    def save(self, *args, **kwargs):
        save_result = super().save(*args, **kwargs)
        existing_fields = {}
        for field in self.__class__._meta.get_fields():
            try:
                existing_fields[field.name] = getattr(self, field.name)
            except:
                pass
        redis_root = get_redis_root()
        redis_root.create(self.__class__, **existing_fields)
        return self

    def delete(self, *args, **kwargs):
        django_id = self.id
        delete_result = super().delete(*args, **kwargs)
        redis_root = get_redis_root()
        redis_instance_qs = redis_root.get(self.__class__, django_id=django_id)
        if redis_instance_qs:
            redis_root.delete(self.__class__, redis_instance_qs)
        return self

    class Meta:
        abstract = True
