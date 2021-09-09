import logging
import re

# TODO: Exceptions and Logging

logger = logging.getLogger("datakitchen_api_tools.DkOrder")


class DKOrder():
    def __init__(self, order_run):
        self.order_run = order_run

    def testsFromOrderRun(self):
        try:
            testStr = self.order_run['servings'][0]['testresults']
        except KeyError:
            #print("Error: No tests in OrderRun Object")
            raise Exception
        return self._parseTestString(testStr)

    def mostRecentOrderRun(self):
        return self.order_run['servings'][0]

    def getCurrentOrderRunStatus(self):
        return self.mostRecentOrderRun()['status']

    def didOrderCompleteSuccesfully(self):
        order_status = self.order_run['orders'][0]['order-status']
        order_run_status = self.getCurrentOrderRunStatus()
        if order_status == "COMPLETED_ORDER" and order_run_status == "COMPLETED_SERVING":
            return True
        return False

    def getFailedTests(self, test_level):
        if test_level == "":
            return list()
        failed_tests = list()
        testResults = self.testsFromOrderRun()
        for level in  ["Failed", "Warning", "Log"]:
            failed_tests += [test for test in testResults if test[2] == level]
            if level == test_level:
                break
        return failed_tests

    def getFailedTestsByName(self, test_names):
        for test in self.testsFromOrderRun():
            if test[2] != "Passed" and test[0] in test_names:
                return False
        return True


    def getOrderStatus(self):
        return self.order_run['orders'][0]['order-status']

    def isOrderRunning(self):
        status = self.order_run['orders'][0]['order-status']
        if status in ["ACTIVE_ORDER",  "PLANNED_SERVING"]:
            return True
        return False

    def _parseTestString(self, testStr):
        tests = list()
        lines = testStr.strip().split('\n')
        state_level = "Failed"
        state_step = ""  # Others are known
        for line in lines:
            line_type = self._getTypeOfTestLine(line)
            if line_type:
                if line_type[0] == "Level":
                    state_level = line_type[1]
                elif line_type[0] == "Step":
                    state_step = line_type[1]
                elif line_type[0] == "Test":
                    tests.append((line_type[1], state_step, state_level, line_type[2]))
        return tests

    def _getTypeOfTestLine(self, line):
        line = line.strip()
        match = re.match(r'Tests: (\w+)', line)
        if match:
            return ("Level", match.group(1))
        match = re.match(r'Step \((.+)\)', line)
        if match:
            return ("Step", match.group(1))
        match = re.match(r'\d+\. (.+) \((.+)\)', line)
        if match:
            return ("Test", match.group(1), match.group(2))
        return None
