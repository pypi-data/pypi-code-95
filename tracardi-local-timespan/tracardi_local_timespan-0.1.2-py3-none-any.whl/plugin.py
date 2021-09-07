import re

from tracardi_dot_notation.dot_accessor import DotAccessor
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result
from tracardi_local_timespan.model.configuration import TimeSpanConfiguration


class LocalTimeSpanAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = TimeSpanConfiguration(**kwargs)

    @staticmethod
    def _validate_timezone(timezone):
        regex = re.compile('^[a-zA-z\-]+\/[a-zA-z\-]+$', re.I)
        return regex.match(str(timezone))

    async def run(self, payload):
        dot = DotAccessor(self.profile, self.session, payload, self.event, self.flow)
        time_zone = dot[self.config.timezone]

        if not self._validate_timezone(time_zone):
            raise ValueError("Your configuration {} points to value {}. And the value is not valid time zone.".format(
                self.config.timezone, time_zone
            ))

        if self.config.is_in_timespan():
            return Result(value=True, port="in"), Result(value=None, port="out")

        return Result(value=None, port="in"), Result(value=True, port="out")


def register() -> Plugin:
    return Plugin(
        start=False,
        debug=False,
        spec=Spec(
            module='tracardi_local_timespan.plugin',
            className='LocalTimeSpanAction',
            inputs=['payload'],
            outputs=['in', 'out'],
            manual='local_timespan',
            version="0.1.2",
            author="Marcin Gaca",
            init={
                "timezone": "session@context.time.tz",
                "start": None,
                "end": None,
            }
        ),
        metadata=MetaData(
            name='Local time span',
            desc='Checks if an event is in given time span',
            type='flowNode',
            width=200,
            height=100,
            icon='profiler',
            group=["Time"]
        )
    )
