from unswamp.objects.base.SerializableObject import SerializableObject
from unswamp.objects.base.MetaDataObject import MetaDataObject
from unswamp.objects.core.CheckRun import CheckRun


class CheckSuite(SerializableObject, MetaDataObject):
    ##################################################################################################
    # Constructor
    ##################################################################################################
    def __init__(self, suite_id, dataset_name, meta_data=None, checks=None):
        SerializableObject.__init__(self)
        MetaDataObject.__init__(self, meta_data)
        self.id = suite_id
        self.dataset_name = dataset_name
        if checks is None:
            checks = []
        self.checks = checks

    ##################################################################################################
    # Methods
    ##################################################################################################
    def add_check(self, check):
        self.checks.append(check)

    def run(self, dataset, run_name, run_id=None, meta_data=None):
        run = CheckRun(run_id, meta_data)
        run.run(dataset, self, run_name)
        return run

    ##################################################################################################
    # Properties
    ##################################################################################################
    id = None
    dataset_name = None
    checks = []
