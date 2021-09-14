'''
# cdk8s-kuma-types v1.3.0

Extends APIObject for Kuma CRD.
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

import cdk8s
import constructs


class CircuitBreaker(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.CircuitBreaker",
):
    '''CircuitBreaker is the Schema for the circuitbreaker API.

    :schema: CircuitBreaker
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "CircuitBreaker" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = CircuitBreakerProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "CircuitBreaker".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = CircuitBreakerProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "CircuitBreaker".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.CircuitBreakerProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class CircuitBreakerProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''CircuitBreaker is the Schema for the circuitbreaker API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: CircuitBreaker
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: CircuitBreaker#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: CircuitBreaker#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: CircuitBreaker#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CircuitBreakerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Dataplane(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.Dataplane",
):
    '''Dataplane is the Schema for the dataplanes API.

    :schema: Dataplane
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "Dataplane" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = DataplaneProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "Dataplane".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = DataplaneProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "Dataplane".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


class DataplaneInsight(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.DataplaneInsight",
):
    '''DataplaneInsight is the Schema for the dataplane insights API.

    :schema: DataplaneInsight
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
    ) -> None:
        '''Defines a "DataplaneInsight" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        '''
        props = DataplaneInsightProps(mesh=mesh, metadata=metadata)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "DataplaneInsight".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        '''
        props = DataplaneInsightProps(mesh=mesh, metadata=metadata)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "DataplaneInsight".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.DataplaneInsightProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata"},
)
class DataplaneInsightProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
    ) -> None:
        '''DataplaneInsight is the Schema for the dataplane insights API.

        :param mesh: 
        :param metadata: 

        :schema: DataplaneInsight
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: DataplaneInsight#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: DataplaneInsight#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplaneInsightProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.DataplaneProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class DataplaneProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Dataplane is the Schema for the dataplanes API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: Dataplane
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: Dataplane#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: Dataplane#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: Dataplane#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplaneProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ExternalService(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.ExternalService",
):
    '''
    :schema: ExternalService
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "ExternalService" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = ExternalServiceProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "ExternalService".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = ExternalServiceProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "ExternalService".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.ExternalServiceProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class ExternalServiceProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''
        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: ExternalService
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: ExternalService#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: ExternalService#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: ExternalService#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExternalServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FaultInjection(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.FaultInjection",
):
    '''FaultInjection is the Schema for the faultinjections API.

    :schema: FaultInjection
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "FaultInjection" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = FaultInjectionProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "FaultInjection".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = FaultInjectionProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "FaultInjection".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.FaultInjectionProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class FaultInjectionProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''FaultInjection is the Schema for the faultinjections API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: FaultInjection
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: FaultInjection#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: FaultInjection#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: FaultInjection#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FaultInjectionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HealthCheck(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.HealthCheck",
):
    '''HealthCheck is the Schema for the healthchecks API.

    :schema: HealthCheck
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "HealthCheck" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = HealthCheckProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "HealthCheck".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = HealthCheckProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "HealthCheck".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.HealthCheckProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class HealthCheckProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''HealthCheck is the Schema for the healthchecks API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: HealthCheck
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: HealthCheck#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: HealthCheck#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: HealthCheck#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HealthCheckProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Mesh(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.Mesh",
):
    '''Mesh is the Schema for the meshes API.

    :schema: Mesh
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "Mesh" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param metadata: 
        :param spec: 
        '''
        props = MeshProps(metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "Mesh".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param metadata: 
        :param spec: 
        '''
        props = MeshProps(metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "Mesh".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


class MeshInsight(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.MeshInsight",
):
    '''MeshInsight is the Schema for the meshes insights API.

    :schema: MeshInsight
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "MeshInsight" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = MeshInsightProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "MeshInsight".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = MeshInsightProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "MeshInsight".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.MeshInsightProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class MeshInsightProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''MeshInsight is the Schema for the meshes insights API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: MeshInsight
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: MeshInsight#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: MeshInsight#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: MeshInsight#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MeshInsightProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.MeshProps",
    jsii_struct_bases=[],
    name_mapping={"metadata": "metadata", "spec": "spec"},
)
class MeshProps:
    def __init__(
        self,
        *,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Mesh is the Schema for the meshes API.

        :param metadata: 
        :param spec: 

        :schema: Mesh
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: Mesh#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: Mesh#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MeshProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ProxyTemplate(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.ProxyTemplate",
):
    '''ProxyTemplate is the Schema for the proxytemplates API.

    :schema: ProxyTemplate
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "ProxyTemplate" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = ProxyTemplateProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "ProxyTemplate".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = ProxyTemplateProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "ProxyTemplate".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.ProxyTemplateProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class ProxyTemplateProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''ProxyTemplate is the Schema for the proxytemplates API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: ProxyTemplate
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: ProxyTemplate#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: ProxyTemplate#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: ProxyTemplate#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProxyTemplateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RateLimit(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.RateLimit",
):
    '''RateLimit is the Schema for the ratelimits API.

    :schema: RateLimit
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "RateLimit" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = RateLimitProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "RateLimit".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = RateLimitProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "RateLimit".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.RateLimitProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class RateLimitProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''RateLimit is the Schema for the ratelimits API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: RateLimit
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: RateLimit#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: RateLimit#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: RateLimit#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RateLimitProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Retry(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.Retry",
):
    '''Retry is the Schema for the retries API.

    :schema: Retry
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "Retry" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = RetryProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "Retry".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = RetryProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "Retry".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.RetryProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class RetryProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Retry is the Schema for the retries API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: Retry
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: Retry#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: Retry#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: Retry#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RetryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceInsight(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.ServiceInsight",
):
    '''ServiceInsight is the Schema for the services insights API.

    :schema: ServiceInsight
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "ServiceInsight" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = ServiceInsightProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "ServiceInsight".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = ServiceInsightProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "ServiceInsight".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.ServiceInsightProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class ServiceInsightProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''ServiceInsight is the Schema for the services insights API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: ServiceInsight
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: ServiceInsight#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: ServiceInsight#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: ServiceInsight#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceInsightProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Timeout(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.Timeout",
):
    '''Timeout is the Schema for the timeout API.

    :schema: Timeout
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "Timeout" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = TimeoutProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "Timeout".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = TimeoutProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "Timeout".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.TimeoutProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class TimeoutProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Timeout is the Schema for the timeout API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: Timeout
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: Timeout#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: Timeout#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: Timeout#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TimeoutProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TrafficLog(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.TrafficLog",
):
    '''TrafficLog is the Schema for the trafficlogs API.

    :schema: TrafficLog
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "TrafficLog" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = TrafficLogProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "TrafficLog".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = TrafficLogProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "TrafficLog".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.TrafficLogProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class TrafficLogProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''TrafficLog is the Schema for the trafficlogs API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: TrafficLog
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: TrafficLog#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: TrafficLog#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: TrafficLog#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TrafficLogProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TrafficPermission(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.TrafficPermission",
):
    '''TrafficPermission is the Schema for the trafficpermissions API.

    :schema: TrafficPermission
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "TrafficPermission" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = TrafficPermissionProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "TrafficPermission".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = TrafficPermissionProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "TrafficPermission".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.TrafficPermissionProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class TrafficPermissionProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''TrafficPermission is the Schema for the trafficpermissions API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: TrafficPermission
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: TrafficPermission#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: TrafficPermission#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: TrafficPermission#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TrafficPermissionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TrafficRoute(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.TrafficRoute",
):
    '''TrafficRoute is the Schema for the trafficroutes API.

    :schema: TrafficRoute
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "TrafficRoute" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = TrafficRouteProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "TrafficRoute".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = TrafficRouteProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "TrafficRoute".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.TrafficRouteProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class TrafficRouteProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''TrafficRoute is the Schema for the trafficroutes API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: TrafficRoute
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: TrafficRoute#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: TrafficRoute#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: TrafficRoute#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TrafficRouteProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TrafficTrace(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.TrafficTrace",
):
    '''TrafficTrace is the Schema for the traffictraces API.

    :schema: TrafficTrace
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "TrafficTrace" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = TrafficTraceProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "TrafficTrace".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = TrafficTraceProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "TrafficTrace".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.TrafficTraceProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class TrafficTraceProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''TrafficTrace is the Schema for the traffictraces API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: TrafficTrace
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: TrafficTrace#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: TrafficTrace#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: TrafficTrace#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TrafficTraceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VirtualOutbound(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.VirtualOutbound",
):
    '''VirtualOutbound is the Schema for the virtualoutbounds API.

    :schema: VirtualOutbound
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "VirtualOutbound" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = VirtualOutboundProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "VirtualOutbound".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = VirtualOutboundProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "VirtualOutbound".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.VirtualOutboundProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class VirtualOutboundProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''VirtualOutbound is the Schema for the virtualoutbounds API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: VirtualOutbound
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: VirtualOutbound#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: VirtualOutbound#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: VirtualOutbound#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VirtualOutboundProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Zone(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.Zone",
):
    '''Zone is the Schema for the zone API.

    :schema: Zone
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "Zone" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = ZoneProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "Zone".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = ZoneProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "Zone".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


class ZoneIngress(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.ZoneIngress",
):
    '''ZoneIngress is the Schema for the zone ingress API.

    :schema: ZoneIngress
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "ZoneIngress" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = ZoneIngressProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "ZoneIngress".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = ZoneIngressProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "ZoneIngress".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


class ZoneIngressInsight(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.ZoneIngressInsight",
):
    '''ZoneIngressInsight is the Schema for the zone ingress insight API.

    :schema: ZoneIngressInsight
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "ZoneIngressInsight" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = ZoneIngressInsightProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "ZoneIngressInsight".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = ZoneIngressInsightProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "ZoneIngressInsight".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.ZoneIngressInsightProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class ZoneIngressInsightProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''ZoneIngressInsight is the Schema for the zone ingress insight API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: ZoneIngressInsight
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: ZoneIngressInsight#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: ZoneIngressInsight#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: ZoneIngressInsight#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZoneIngressInsightProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.ZoneIngressProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class ZoneIngressProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''ZoneIngress is the Schema for the zone ingress API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: ZoneIngress
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: ZoneIngress#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: ZoneIngress#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: ZoneIngress#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZoneIngressProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZoneInsight(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-kuma-types.ZoneInsight",
):
    '''ZoneInsight is the Schema for the zone insight API.

    :schema: ZoneInsight
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Defines a "ZoneInsight" API object.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = ZoneInsightProps(mesh=mesh, metadata=metadata, spec=spec)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> typing.Any:
        '''Renders a Kubernetes manifest for "ZoneInsight".

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param mesh: 
        :param metadata: 
        :param spec: 
        '''
        props = ZoneInsightProps(mesh=mesh, metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''Returns the apiVersion and kind for "ZoneInsight".'''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.ZoneInsightProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class ZoneInsightProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''ZoneInsight is the Schema for the zone insight API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: ZoneInsight
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: ZoneInsight#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: ZoneInsight#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: ZoneInsight#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZoneInsightProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-kuma-types.ZoneProps",
    jsii_struct_bases=[],
    name_mapping={"mesh": "mesh", "metadata": "metadata", "spec": "spec"},
)
class ZoneProps:
    def __init__(
        self,
        *,
        mesh: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        spec: typing.Any = None,
    ) -> None:
        '''Zone is the Schema for the zone API.

        :param mesh: 
        :param metadata: 
        :param spec: 

        :schema: Zone
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if mesh is not None:
            self._values["mesh"] = mesh
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def mesh(self) -> typing.Optional[builtins.str]:
        '''
        :schema: Zone#mesh
        '''
        result = self._values.get("mesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''
        :schema: Zone#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''
        :schema: Zone#spec
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZoneProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CircuitBreaker",
    "CircuitBreakerProps",
    "Dataplane",
    "DataplaneInsight",
    "DataplaneInsightProps",
    "DataplaneProps",
    "ExternalService",
    "ExternalServiceProps",
    "FaultInjection",
    "FaultInjectionProps",
    "HealthCheck",
    "HealthCheckProps",
    "Mesh",
    "MeshInsight",
    "MeshInsightProps",
    "MeshProps",
    "ProxyTemplate",
    "ProxyTemplateProps",
    "RateLimit",
    "RateLimitProps",
    "Retry",
    "RetryProps",
    "ServiceInsight",
    "ServiceInsightProps",
    "Timeout",
    "TimeoutProps",
    "TrafficLog",
    "TrafficLogProps",
    "TrafficPermission",
    "TrafficPermissionProps",
    "TrafficRoute",
    "TrafficRouteProps",
    "TrafficTrace",
    "TrafficTraceProps",
    "VirtualOutbound",
    "VirtualOutboundProps",
    "Zone",
    "ZoneIngress",
    "ZoneIngressInsight",
    "ZoneIngressInsightProps",
    "ZoneIngressProps",
    "ZoneInsight",
    "ZoneInsightProps",
    "ZoneProps",
]

publication.publish()
