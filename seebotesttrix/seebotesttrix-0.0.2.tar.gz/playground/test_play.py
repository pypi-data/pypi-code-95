import pytest
from unit_tests import actions_unit_test
from shared import run_parallel
import allure


# @allure.step
# def function_scope_step():


# test annotation
@allure.feature('Fixtures')
def test_1():
    run_parallel.run_parallel(5, actions_unit_test.first_test)
