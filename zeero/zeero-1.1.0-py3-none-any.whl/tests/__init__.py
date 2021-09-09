# import os
# import tempfile
# import unittest

# from ploigos_step_runner.step_runner import StepRunner
# from ploigos_step_runner.workflow_result import WorkflowResult


# class StepImplementerTestCase(unittest.TestCase):
#     def run_step_test(self, config, step, test_dir, expected_step_results):
#         self.maxDiff = 5000
#         working_dir_path = os.path.join(test_dir, 'step-runner-working')
#         results_dir_path = os.path.join(test_dir, 'step-runner-results')

#         factory = StepRunner(config, results_dir_path, 'step-runner-results.yml', working_dir_path)
#         factory.run_step(step_name=step)

#         pickle = f'{working_dir_path}/step-runner-results.pkl'
#         workflow_results = WorkflowResult.load_from_pickle_file(pickle)

#         step_result = workflow_results.get_step_result(step_name=step)
#         self.assertEqual(expected_step_results, step_result.get_step_result_dict())
