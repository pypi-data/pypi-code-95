'''
# cdk8s-redis

> Redis constructs for cdk8s

Basic implementation of a Redis construct for cdk8s. Contributions are welcome!

## Usage

The following will define a Redis cluster with a master and 2 slave replicas:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk8s_redis import Redis

# inside your chart:
redis = Redis(self, "my-redis")
```

DNS names can be obtained from `redis.masterHost` and `redis.slaveHost`.

You can specify how many slave replicas to define:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
Redis(self, "my-redis",
    slave_replicas=4
)
```

Or, you can specify no slave:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
Redis(self, "my-redis",
    slave_replicas=0
)
```

## License

Distributed under the [Apache 2.0](./LICENSE) license.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import constructs


class Redis(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-redis.Redis",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        slave_replicas: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param labels: (experimental) Extra labels to associate with resources. Default: - none
        :param slave_replicas: (experimental) Number of slave replicas. Default: 2

        :stability: experimental
        '''
        options = RedisOptions(labels=labels, slave_replicas=slave_replicas)

        jsii.create(self.__class__, self, [scope, id, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterHost")
    def master_host(self) -> builtins.str:
        '''(experimental) The DNS host for the master server.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "masterHost"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="slaveHost")
    def slave_host(self) -> builtins.str:
        '''(experimental) The DNS host for the slave service.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "slaveHost"))


@jsii.data_type(
    jsii_type="cdk8s-redis.RedisOptions",
    jsii_struct_bases=[],
    name_mapping={"labels": "labels", "slave_replicas": "slaveReplicas"},
)
class RedisOptions:
    def __init__(
        self,
        *,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        slave_replicas: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param labels: (experimental) Extra labels to associate with resources. Default: - none
        :param slave_replicas: (experimental) Number of slave replicas. Default: 2

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if labels is not None:
            self._values["labels"] = labels
        if slave_replicas is not None:
            self._values["slave_replicas"] = slave_replicas

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Extra labels to associate with resources.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def slave_replicas(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of slave replicas.

        :default: 2

        :stability: experimental
        '''
        result = self._values.get("slave_replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedisOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Redis",
    "RedisOptions",
]

publication.publish()
