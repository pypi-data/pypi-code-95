import unittest
import uuid

import numpy as np
from pyhectiqlab import Run, Config, AuthProvider

run_name = f'test {uuid.uuid4()}'
run = Run(name=run_name, project='test', should_create_project=True)

class CreateRunTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.hectiq_run = run
        logger = cls.hectiq_run.start_recording_logs('unittest')
        
    def test_is_logged(self):
        self.assertEqual(AuthProvider().is_logged(), True)

    def test_add_meta(self):
        self.hectiq_run.add_meta('is_test', True)
        self.hectiq_run.add_meta('scalar', 1.2)
        self.hectiq_run.add_meta('string', 'Hello world')

    def test_add_tag(self):
        self.hectiq_run.add_tag(name='hello', description='This run is a test')
        self.hectiq_run.add_tag(name='world')

    def test_add_packages(self):
        self.hectiq_run.add_package_versions(globals())

    def test_add_package_repo_state(self):
        self.hectiq_run.add_package_repo_state('pyhectiqlab')

    def test_add_metrics(self):
        key = 'sinx'
        self.hectiq_run.set_metrics_cache_settings(min_cache_flush_delay=0, max_cache_length=10)
        for step in np.arange(100):
            value = np.sin(step/20)
            self.hectiq_run.add_metrics(key, value, step)

    def test_add_artifact(self):
        self.hectiq_run.add_artifacts('./test_img1.jpeg')
        self.hectiq_run.add_artifacts('./test_img2.jpeg')

    def test_add_step_artifact(self):
        self.hectiq_run.add_artifacts('./test_img2.jpeg', step=1)

    def test_add_config(self):
        sub_config = Config(c='hello world', d=1.5, e=True)
        config = Config(a=1, sub_config=sub_config)
        self.hectiq_run.add_config(config=config)

    def test_log(self):
        logger = self.hectiq_run.start_recording_logs()
        logger.info('info')
        logger.warning('warning')
        logger.error('error')
        logger.critical('critical')
        logger.debug('debug')

    def test_status(self):
        self.hectiq_run.running()
        self.hectiq_run.pending()
        self.hectiq_run.training()
        self.hectiq_run.completed()

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CreateRunTest)
    result = unittest.TextTestRunner().run(suite)

    if result.wasSuccessful():
        run.completed()
        run.add_tag(name='success')
    else:
        run.failed()