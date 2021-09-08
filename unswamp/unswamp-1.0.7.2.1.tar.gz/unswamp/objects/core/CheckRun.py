from datetime import datetime
import uuid
from unswamp.objects.base.SerializableObject import SerializableObject
from unswamp.objects.base.MetaDataObject import MetaDataObject


class CheckRun(SerializableObject, MetaDataObject):
    ##################################################################################################
    # Constructor
    ##################################################################################################
    def __init__(self, run_id=None, meta_data = None):
        SerializableObject.__init__(self)
        MetaDataObject.__init__(self, meta_data)

        if run_id is None:
            run_id = str(uuid.uuid4().hex)
        self.id = run_id
        
        self.results = []

    ##################################################################################################
    # Methods
    ##################################################################################################
    def run(self, dataset, suite, run_name):
        self.dataset_rows = dataset.shape[0]
        self.dataset_columns = dataset.shape[1]
        self.results = []
        self.suite_id = suite.id
        self.name = run_name
        self.dataset_name = suite.dataset_name
        self.start = datetime.now()
        for check in suite.checks:
            if check.active:
                result = check.run(dataset)
                result.duration = result.end - result.start
                self.results.append(result)
        self.end = datetime.now()
        self.update_run_data()

    def update_run_data(self):
        self.duration = self.end - self.start
        self.total_checks = len(self.results)

        pass_rate = 0
        if self.total_checks != 0:
            pass_rate = len(self.passed_results) / len(self.results)
        self.pass_rate = pass_rate
        self.fail_rate = 1 - pass_rate


    ##################################################################################################
    # Properties
    ##################################################################################################
    id = None
    meta_data = None
    suite_id = None
    results = []
    start = datetime.min
    end = datetime.min
    duration = 0
    dataset_rows = 0
    dataset_columns = 0
    name = None
    dataset_name = None
    total_checks = 0
    pass_rate = 0
    fail_rate = 0
    

    @property
    def failed_results(self):
        results = [res for res in self.results if res.passed == False]
        return results

    @property
    def passed_results(self):
        results = [res for res in self.results if res.passed == True]
        return results

        
