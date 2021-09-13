from setuptools import setup

name = "types-aws-xray-sdk"
description = "Typing stubs for aws-xray-sdk"
long_description = '''
## Typing stubs for aws-xray-sdk

This is a PEP 561 type stub package for the `aws-xray-sdk` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `aws-xray-sdk`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/aws-xray-sdk. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `8a704ab2900bb27cd3f9905457b012696451738e`.
'''.lstrip()

setup(name=name,
      version="2.8.1",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['aws_xray_sdk-stubs'],
      package_data={'aws_xray_sdk-stubs': ['__init__.pyi', 'core/__init__.pyi', 'core/async_context.pyi', 'core/async_recorder.pyi', 'core/context.pyi', 'core/daemon_config.pyi', 'core/emitters/__init__.pyi', 'core/emitters/udp_emitter.pyi', 'core/exceptions/__init__.pyi', 'core/exceptions/exceptions.pyi', 'core/lambda_launcher.pyi', 'core/models/__init__.pyi', 'core/models/default_dynamic_naming.pyi', 'core/models/dummy_entities.pyi', 'core/models/entity.pyi', 'core/models/facade_segment.pyi', 'core/models/http.pyi', 'core/models/noop_traceid.pyi', 'core/models/segment.pyi', 'core/models/subsegment.pyi', 'core/models/throwable.pyi', 'core/models/trace_header.pyi', 'core/models/traceid.pyi', 'core/patcher.pyi', 'core/plugins/__init__.pyi', 'core/plugins/ec2_plugin.pyi', 'core/plugins/ecs_plugin.pyi', 'core/plugins/elasticbeanstalk_plugin.pyi', 'core/plugins/utils.pyi', 'core/recorder.pyi', 'core/sampling/__init__.pyi', 'core/sampling/connector.pyi', 'core/sampling/local/__init__.pyi', 'core/sampling/local/reservoir.pyi', 'core/sampling/local/sampler.pyi', 'core/sampling/local/sampling_rule.pyi', 'core/sampling/reservoir.pyi', 'core/sampling/rule_cache.pyi', 'core/sampling/rule_poller.pyi', 'core/sampling/sampler.pyi', 'core/sampling/sampling_rule.pyi', 'core/sampling/target_poller.pyi', 'core/streaming/__init__.pyi', 'core/streaming/default_streaming.pyi', 'core/utils/__init__.pyi', 'core/utils/atomic_counter.pyi', 'core/utils/compat.pyi', 'core/utils/conversion.pyi', 'core/utils/search_pattern.pyi', 'core/utils/stacktrace.pyi', 'sdk_config.pyi', 'version.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Typed",
      ]
)
