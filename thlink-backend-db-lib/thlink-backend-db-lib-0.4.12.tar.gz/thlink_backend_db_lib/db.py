from __future__ import annotations
from typing import List, Dict, Tuple, Optional, Any
import boto3
import botocore.exceptions
import boto3.dynamodb.conditions
import circuitbreaker
import concurrent.futures
import hashlib


class ItemKey:

    def __init__(self, name, value, secondary: ItemKey = None):
        if secondary and secondary.secondary:
            raise ValueError("ItemKey can only consist of one primary and one secondary key")
        self.name = name
        self.value = value
        self.secondary = secondary

    def as_dynamodb_primary_key_cond_expression(self):
        return boto3.dynamodb.conditions.Key(self.name).eq(self.value)

    def as_dynamodb_key(self):
        return {
            self.name: self.value,
            **(self.secondary.as_dynamodb_key() if self.secondary else {}),
        }


class InternalError(Exception):
    pass


class DB:

    def __init__(self, name: str, logger):
        self._name = name
        self._table = boto3.resource("dynamodb").Table(name)
        self._logger = logger
        self._to_put = []
        self._to_update = []
        self._to_delete = []

    def query_items(self, key: ItemKey):
        # query primary key
        try:
            response = self._table.query(
                IndexName=key.name,
                KeyConditionExpression=key.as_dynamodb_primary_key_cond_expression(),
            )
            return response["Items"]
        except botocore.exceptions.ClientError as e:
            raise InternalError() from e

    def get_item(self, key: ItemKey):
        try:
            resp = self._table.get_item(Key=key.as_dynamodb_key())
            return resp["Item"] if "Item" in resp else None
        except botocore.exceptions.ClientError as e:
            raise InternalError() from e

    def get_bulk(self, keys: List[ItemKey]):
        try:
            response = self._table.meta.client.batch_get_item(RequestItems={
                self._name: {"Keys": [key.as_dynamodb_key() for key in keys]}
            })
            return response["Responses"][self._name]
        except botocore.exceptions.ClientError as e:
            raise InternalError() from e

    def stage_put(self, key: ItemKey, item: Dict, expect_if_item_exists: Dict = None):
        self._to_put.append((key, item, expect_if_item_exists))

    def stage_update(self, key: ItemKey, item: Dict, old_item: Dict):
        self._to_update.append((key, item, old_item))

    def stage_delete(self, key: ItemKey):
        self._to_delete.append((key,))

    def flush(self):
        # TODO make use of self._table.batch_writer for put/ delete
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            for to_put in self._to_put:
                executor.submit(self.put, *to_put)
            for to_update in self._to_update:
                executor.submit(self.update, *to_update)
            for to_delete in self._to_delete:
                executor.submit(self.delete, *to_delete)

    def put(self, key: ItemKey, item: Dict, expect_if_item_exists: Dict = None):
        try:
            self._operation("put", (key, item, expect_if_item_exists))
        except InternalError as e:
            if self._logger:
                self._logger.exception(f"Put operation failed: {e}")
            raise
        except circuitbreaker.CircuitBreakerError as e:
            if self._logger:
                self._logger.exception(f"Didn't execute the operation because previous attempts failed")
            raise InternalError() from e

    def update(self, key: ItemKey, item: Dict, old_item: Dict):
        try:
            self._operation("update", (key, item, old_item))
        except InternalError as e:
            if self._logger:
                self._logger.exception(f"Update operation failed: {e}")
            raise
        except circuitbreaker.CircuitBreakerError as e:
            if self._logger:
                self._logger.exception(f"Didn't execute the operation because previous attempts failed")
            raise InternalError() from e

    def delete(self, key: ItemKey):
        try:
            self._operation("delete", (key,))
        except InternalError as e:
            if self._logger:
                self._logger.exception(f"Delete operation failed: {e}")
            raise
        except circuitbreaker.CircuitBreakerError as e:
            if self._logger:
                self._logger.exception(f"Didn't execute the operation because previous attempts failed")
            raise InternalError() from e

    @circuitbreaker.circuit(failure_threshold=1, recovery_timeout=None, expected_exception=InternalError)
    def _operation(self, name: str, args):
        # Aggregate operations for circuit breaker
        if name == "put":
            self._put(*args)
        elif name == "update":
            self._update(*args)
        elif name == "delete":
            self._delete(*args)
        else:
            raise ValueError("Invalid operation")

    def _put(self, key: ItemKey, item: Dict, expect_if_item_exists: Dict = None):
        assert key.name in item
        assert not key.secondary or key.secondary.name in item
        kwargs = {"Item": item}
        if expect_if_item_exists:
            statements = []
            expression_names = {}
            expression_values = {}
            for name, value in expect_if_item_exists.items():
                hashed_name = self._hash_name(name)
                statements.append(f"#{hashed_name} = :{hashed_name}")
                expression_names[f"#{hashed_name}"] = name
                expression_values[f":{hashed_name}"] = value
            condition_expression = " AND ".join(statements)
            # or item does not exist
            hashed_key_name = self._hash_name(key.name)
            condition_expression = f"({condition_expression}) OR #{hashed_key_name}<>:{hashed_key_name}"
            expression_names[f"#{hashed_key_name}"] = key.name
            expression_values[f":{hashed_key_name}"] = key.value
            kwargs = {
                **kwargs,
                "ConditionExpression": condition_expression,
                "ExpressionAttributeNames": expression_names,
                "ExpressionAttributeValues": expression_values,
            }
        try:
            self._table.put_item(**kwargs)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ExpectationNotMet() from e
            raise InternalError() from e

    def _update(self, key: ItemKey, item: Dict, old_item: Dict):
        assert key.name in item
        assert not key.secondary or key.secondary.name in item

        def build_expression():  # apply diff
            set_actions = []
            remove_actions = []
            names = {}
            values = {}

            for name, value in item.items():
                hashed_name = self._hash_name(name)

                if type(value) is dict and name in old_item:
                    for sub_name, sub_value in value.items():
                        hashed_sub_name = self._hash_name(sub_name)
                        if sub_name not in old_item[name] or old_item[name][sub_name] != sub_value:
                            set_actions.append(
                                f"#{hashed_name}.#{hashed_sub_name} = :{hashed_name + hashed_sub_name}"
                            )
                            names[f"#{hashed_name}"] = name
                            names[f"#{hashed_sub_name}"] = sub_name
                            values[f":{hashed_name + hashed_sub_name}"] = sub_value

                    for old_sub_name in old_item.get(name, {}):
                        if old_sub_name not in value:
                            hashed_old_sub_name = self._hash_name(old_sub_name)
                            remove_actions.append(f"#{hashed_name}.#{hashed_old_sub_name}")
                            names[f"#{hashed_name}"] = name
                            names[f"#{hashed_old_sub_name}"] = old_sub_name

                elif name not in old_item or old_item[name] != value:
                    set_actions.append(f"#{hashed_name} = :{hashed_name}")
                    names[f"#{hashed_name}"] = name
                    values[f":{hashed_name}"] = value

            for old_name in old_item:
                if old_name not in item:
                    hashed_old_name = self._hash_name(old_name)
                    remove_actions.append(f"#{hashed_old_name}")
                    names[f"#{hashed_old_name}"] = old_name

            clauses = []
            if set_actions:
                clauses.append("SET " + ", ".join(set_actions))
            if remove_actions:
                clauses.append("REMOVE " + ", ".join(remove_actions))
            return " ".join(clauses), names, values

        expression, expression_names, expression_values = build_expression()

        hashed_key_name = self._hash_name(key.name)
        expression_names[f"#{hashed_key_name}"] = key.name

        kwargs = {
            "Key": key.as_dynamodb_key(),
            "UpdateExpression": expression,
            "ExpressionAttributeNames": expression_names,
            # make sure that item is being updated, not created
            "ConditionExpression": f"attribute_exists(#{hashed_key_name})",
        }
        if expression_values:
            kwargs["ExpressionAttributeValues"] = expression_values

        try:
            self._table.update_item(**kwargs)
        except botocore.exceptions.ClientError as e:
            raise InternalError() from e

    def _delete(self, key: ItemKey):
        try:
            self._table.delete_item(Key=key.as_dynamodb_key())
        except botocore.exceptions.ClientError as e:
            raise InternalError() from e

    @staticmethod
    def _hash_name(name: str):
        return str(hashlib.md5(bytes(name, "utf-8")).hexdigest())


class DBMock:

    def __init__(self, *args, **kwargs):
        self._to_put = []
        self._to_update = []
        self._to_delete = []

    _table: Dict[Tuple[str, Optional[str]], Any]

    count_query_operations: int

    def query_items(self, key: ItemKey):
        DBMock.count_query_operations += 1
        items = []
        for found_key, found_item in DBMock._table.items():
            if found_key[0] == key.value:
                items.append(found_item)
        return items

    count_get_operations: int

    def get_item(self, key: ItemKey, count=True):
        if count:
            DBMock.count_get_operations += 1
        return DBMock._table.get(self._key_for_table(key))

    def get_bulk(self, keys: List[ItemKey]):
        items = []
        for key in keys:
            items.append(DBMock._table.get(self._key_for_table(key)))
        return items

    def stage_put(self, key: ItemKey, item: Dict, expect_if_item_exists: Dict = None):
        self._to_put.append((key, item, expect_if_item_exists))

    def stage_update(self, key: ItemKey, item: Dict, old_item: Dict):
        self._to_update.append((key, item, old_item))

    def stage_delete(self, key: ItemKey):
        self._to_delete.append((key,))

    def flush(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            for to_put in self._to_put:
                executor.submit(self.put, *to_put)
            for to_update in self._to_update:
                executor.submit(self.update, *to_update)
            for to_delete in self._to_delete:
                executor.submit(self.delete, *to_delete)

    count_put_operations: int

    def put(self, key: ItemKey, item: Dict, expect_if_item_exists: Dict = None, count=True):
        if expect_if_item_exists is None:
            expect_if_item_exists = {}
        if count:
            DBMock.count_put_operations += 1
        assert key.name in item
        assert not key.secondary or key.secondary.name in item
        existing = self.get_item(key, count=False)
        if existing:
            for name, value in expect_if_item_exists.items():
                if existing.get(name) != value:
                    raise ExpectationNotMet()
        DBMock._table[self._key_for_table(key)] = item

    count_update_operations: int

    def update(self, key: ItemKey, item: Dict, old_item: Dict):
        DBMock.count_update_operations += 1
        self.put(key, item, count=False)

    count_delete_operations: int

    def delete(self, key: ItemKey):
        DBMock.count_delete_operations += 1
        if self._key_for_table(key) in self._table:
            del DBMock._table[self._key_for_table(key)]

    @staticmethod
    def test_operations_count(query=0, get=0, put=0, update=0, delete=0):
        assert DBMock.count_query_operations == query
        assert DBMock.count_get_operations == get
        assert DBMock.count_put_operations == put
        assert DBMock.count_update_operations == update
        assert DBMock.count_delete_operations == delete

    @staticmethod
    def _key_for_table(key: ItemKey):
        if key.secondary:
            return key.value, key.secondary.value
        return key.value, None


class ExpectationNotMet(ValueError):
    pass
