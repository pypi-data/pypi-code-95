#  Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: Apache-2.0

from servicecatalog_puppet import constants
from servicecatalog_puppet.workflow.launch import launch_for_task


class LaunchTask(launch_for_task.LaunchForTask):
    def params_for_results_display(self):
        return {
            "puppet_account_id": self.puppet_account_id,
            "launch_name": self.launch_name,
            "cache_invalidator": self.cache_invalidator,
        }

    def requires(self):
        requirements = list()

        klass = self.get_klass_for_provisioning()
        for (
            account_id,
            regions,
        ) in self.manifest.get_account_ids_and_regions_used_for_section_item(
            self.puppet_account_id, constants.LAUNCHES, self.launch_name
        ).items():
            for region in regions:
                for task in self.manifest.get_tasks_for_launch_and_account_and_region(
                    self.puppet_account_id,
                    self.section_name,
                    self.launch_name,
                    account_id,
                    region,
                    single_account=self.single_account,
                ):
                    requirements.append(
                        klass(**task, manifest_file_path=self.manifest_file_path)
                    )

        return requirements

    def run(self):
        self.write_output(self.params_for_results_display())
