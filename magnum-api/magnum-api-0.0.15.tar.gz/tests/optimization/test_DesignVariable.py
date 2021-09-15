from unittest import TestCase

import numpy as np

from magnumapi.optimization.DesignVariable import DesignVariable, GeneticDesignVariable


class TestDesignVariable(TestCase):
    def test_get_variable_name_empty_bcs(self):
        # arrange
        dv = DesignVariable(xl=5, xu=10, xs=7, variable='R_EE', bcs='')

        # act
        variable_names = dv.get_variable_names()

        # assert
        self.assertEqual('R_EE', variable_names[0])

    def test_get_variable_name_single_index_bcs(self):
        # arrange
        dv = DesignVariable(xl=5, xu=10, xs=7, variable='nco', bcs='1')

        # act
        variable_names = dv.get_variable_names()

        # assert
        self.assertEqual('1:nco', variable_names[0])

    def test_get_variable_name_range_index_bcs(self):
        # arrange
        dv = DesignVariable(xl=5, xu=10, xs=7, variable='nco', bcs='1-5')

        # act
        variable_names = dv.get_variable_names()

        # assert
        self.assertListEqual(['1:nco', '2:nco', '3:nco', '4:nco', '5:nco'], variable_names)

    def test_get_variable_name_error(self):
        # arrange
        dv = DesignVariable(xl=5, xu=10, xs=7, variable='nco', bcs='1:5')

        # act
        # assert
        with self.assertRaises(AttributeError) as context:
            dv.get_variable_names()

        self.assertTrue('The design variable has incorrect block index value: 1:5.' in str(context.exception))

    def test__convert_range_of_blocks_into_list_error_two_hyphens(self):
        # arrange
        dv = DesignVariable(xl=5, xu=10, xs=7, variable='nco', bcs='1--')

        # act
        # assert
        with self.assertRaises(AttributeError) as context:
            dv._convert_range_of_blocks_into_list()

        self.assertTrue('The block index range definition 1-- is wrong. Only one hyphen is allowed.'
                        in str(context.exception))

    def test__convert_range_of_blocks_into_list_error_lower_limit_character(self):
        # arrange
        dv = DesignVariable(xl=5, xu=10, xs=7, variable='nco', bcs='a-5')

        # act
        # assert
        with self.assertRaises(AttributeError) as context:
            dv._convert_range_of_blocks_into_list()

        self.assertTrue('The lower block index range a is not a number.' in str(context.exception))

    def test__convert_range_of_blocks_into_list_error_upper_limit_character(self):
        # arrange
        dv = DesignVariable(xl=5, xu=10, xs=7, variable='nco', bcs='5-b')

        # act
        # assert
        with self.assertRaises(AttributeError) as context:
            dv._convert_range_of_blocks_into_list()

        self.assertTrue('The upper block index range b is not a number.' in str(context.exception))

    def test__convert_range_of_blocks_into_list_lower_greater_than_upper(self):
        # arrange
        dv = DesignVariable(xl=5, xu=10, xs=7, variable='nco', bcs='5-1')

        # act
        # assert
        with self.assertRaises(AttributeError) as context:
            dv._convert_range_of_blocks_into_list()

        self.assertTrue('The lower index 5 is greater than the upper one 1.' in str(context.exception))

    def test__convert_range_of_blocks_into_list_lower_equal_to_upper(self):
        # arrange
        dv = DesignVariable(xl=5, xu=10, xs=7, variable='nco', bcs='5-5')

        # act
        variable_name = dv._convert_range_of_blocks_into_list()

        # assert
        self.assertListEqual(['5:nco'], variable_name)

    def test__convert_range_of_blocks_into_list(self):
        # arrange
        dv = DesignVariable(xl=5, xu=10, xs=7, variable='nco', bcs='1-5')

        # act
        variable_name = dv._convert_range_of_blocks_into_list()

        # assert
        self.assertListEqual(['1:nco', '2:nco', '3:nco', '4:nco', '5:nco'], variable_name)


class TestGeneticDesignVariable(TestCase):
    def test_generate_random_gene_int_seed_0(self):
        # arrange
        np.random.seed(0)
        dv = GeneticDesignVariable(xl=5, xu=10, xs=7, variable='nco', bcs='1-5', bits=5, variable_type='int')

        # act
        gene = dv.generate_random_gene()

        # assert
        self.assertListEqual([0, 0, 1, 0, 1], gene)

    def test_generate_random_gene_int_seed_2001(self):
        # arrange
        np.random.seed(2001)
        dv = GeneticDesignVariable(xl=5, xu=10, xs=7, variable='nco', bcs='1-5', bits=4, variable_type='int')

        # act
        gene = dv.generate_random_gene()

        # assert
        self.assertListEqual([0, 0, 0, 0], gene)

    def test_generate_random_gene_float_seed_0(self):
        # arrange
        np.random.seed(0)
        dv = GeneticDesignVariable(xl=5, xu=10, xs=7, variable='nco', bcs='1-5', bits=5, variable_type='float')

        # act
        gene = dv.generate_random_gene()

        # assert
        self.assertListEqual([0, 1, 1, 0, 1], gene)

    def test_convert_gene_to_value_int(self):
        # arrange
        np.random.seed(0)
        dv = GeneticDesignVariable(xl=5, xu=10, xs=7, variable='nco', bcs='1-5', bits=5, variable_type='int')

        # act
        gene = dv.generate_random_gene()
        value = dv.convert_gene_to_value(gene)

        # assert
        self.assertEqual(10, value)

    def test_convert_gene_to_value_float(self):
        # arrange
        np.random.seed(0)
        dv = GeneticDesignVariable(xl=5, xu=10, xs=7, variable='nco', bcs='1-5', bits=5, variable_type='float')

        # act
        gene = dv.generate_random_gene()
        value = dv.convert_gene_to_value(gene)

        # assert
        self.assertAlmostEqual(7.03125, value, places=5)

    def test_convert_gene_to_int(self):
        # arrange
        gene = [1, 0, 1, 0]

        # act
        int_value = GeneticDesignVariable.convert_gene_to_int(gene)

        # assert
        self.assertEqual(10, int_value)

    def test_convert_int_to_gene(self):
        # arrange
        int_value = 10

        # act
        gene = GeneticDesignVariable.convert_int_to_gene(int_value)

        # assert
        self.assertListEqual([1, 0, 1, 0], gene)
