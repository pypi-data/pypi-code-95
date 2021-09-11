from swimlane_platform.lib.names import names
from swimlane_platform.lib.debug_decorators import info_function_start_finish
from swimlane_platform.shared_steps import enable_turbine
from swimlane_platform.upgrade_steps.upgrade_step import UpgradeStep
import semver


class UpgradeFrom1011To1012(UpgradeStep):
    FROM = semver.parse_version_info('10.1.1')  # type: semver.VersionInfo
    TO = semver.parse_version_info('10.1.2')  # type: semver.VersionInfo

    @info_function_start_finish('Upgrade From 10.1.1 To 10.1.2.')
    def process(self):
        # type: () -> None
        enable_turbine.run(self.config)
        self.upgrade_standard_images(self.config.args.dev, names.INSTALL_DIR).save()
