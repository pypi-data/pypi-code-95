import asyncio
from typing import Type

from tracardi_plugin_sdk.action_runner import ActionRunner


class PluginTestResult:
    def __init__(self, output, profile=None, session=None, event=None):
        self.event = event
        self.session = session
        self.profile = profile
        self.output = output

    def __repr__(self):
        return f"output=`{self.output}`\nprofile=`{self.profile}`\nsession=`{self.session}`\nevent=`{self.session}`"


def run_plugin(plugin: Type[ActionRunner], init, payload, profile=None, session=None, event=None) -> PluginTestResult:

    async def main(plugin, init, payload):
        try:

            build_method = getattr(plugin, "build", None)
            if build_method and callable(build_method):
                plugin = await build_method(**init)
            else:
                plugin = plugin(**init)

            plugin.profile = profile
            plugin.session = session
            plugin.event = event

            output = await plugin.run(payload)

            return PluginTestResult(
                output,
                profile,
                session,
                event
            )

        except Exception as e:
            if isinstance(plugin, ActionRunner):
                await plugin.on_error()
            raise e
        finally:
            if isinstance(plugin, ActionRunner):
                await plugin.close()

    return asyncio.run(main(plugin, init, payload))
