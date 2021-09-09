#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Application to testing and printing obsinfo information files. 

Includes class TestObsinfo, class JsonRefTest and entry points.

   # JsonRefTest tests the reading functions of JSON and YAML files.

   # TestObsinfo tests information files content


 Much the SAME functions and methods are called whether printing or testing, as there is little difference
 between both functionalities. Entry points vary for each functionality and the distinction is achieved by naming
 the executable with two different names (i.e. a named link):


    * obsinfo-print has entry point print_obs. 

    * obsinfo-test has entry point run_suite_info_files. It is meant to be used by developers. In this vein, contrary to obsinfo-validate, obsinfo-print calls private methods which are not callable from the command line but which can be called from the interpreter.

    * JsonRefTest is meant to be called from the interpreter. It has no entry point.


 There are two types of testing functionalities.

    a) If the file name includes "test--attributes" the output of the corresponding obsinfo test function will be checked against data contained in this class.
    
    b) If the file name is "normal", it will simply run through to make sure there are no errors

 Testing for type (a) uses data from obsinfo/tests/data/Information_Files/responses/_filters. 
 Testing for type (b) uses data from obsinfo/_examples/Information_Files 

 WARNING: many tests are critically dependent on file hierarchy, including names. Do not change names
 in tests or _examples hierarchy, or else change the names here.
 Also, the following methods use four specific file names:
 
     * test_all_stage_types()
     * test_sensor()
     * test_preamplifier()
     * test_datalogger()
     * test_station()
     
 All current examples of sensors safe NANOMETRICS_T240_SINGLESIDED have no configuration key and no default. 
 Messages to this effect are to be expected.

"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from future.builtins import *  # NOQA @UnusedWildImport

import os
import warnings
warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
import sys
from pathlib import Path, PurePath
import unittest
import inspect
import difflib
import re
import glob
from json.decoder import JSONDecodeError
from argparse import ArgumentParser

import logging
from logging.handlers import RotatingFileHandler


#Third party  imports
from obspy.core.utcdatetime import UTCDateTime
from obspy.core.inventory.util import  (Latitude, Longitude, Site, Comment)

# obsinfo modules
from ..obsMetadata.obsmetadata import (ObsMetadata)
from ..network.station import (Station, Location)

from obsinfo.obsMetadata.obsmetadata import (ObsMetadata)
from obsinfo.instrumentation import (Instrumentation, InstrumentComponent,
                                     Datalogger, Preamplifier, Sensor,
                                     ResponseStages, Stage, Filter)
from obsinfo.instrumentation.instrumentation import (Location)
from obsinfo.network import (Station, Network)
from obsinfo.instrumentation.filter import (Filter, PolesZeros, FIR, Coefficients, ResponseList,
                     Analog, Digital, AD_Conversion)
from obsinfo.misc.printobs import  (PrintObs)
from obsinfo.misc.discoveryfiles import Datapath
import obsinfo
from obsinfo.misc.const import *
from obsinfo.misc.configuration import Singleton

verbose = False

class JsonRefTest(unittest.TestCase):
    """
    Class of test methods for information file format
    
      **Attributes:**
    
        * testing_path (str): path to datafiles to be tested aside from the examples
        * level (str): level to be printed
        * test (boolean): determines if this is test mode
        * print_output (boolean): determines if this is print mode. Both can coexist.
    
    """
    
    def setUp(self, test=True, print_output=False, level=None):
        """
        
        Set up default values and paths
        
        """
           
        self.testing_path =  Path(os.getcwd()).joinpath("obsinfo", "tests", "data")
    
        self.level = level
        self.test = test
        self.print_output = print_output
        
    
    def assertTextFilesEqual(self, first, second, msg=None):
        with open(first) as f:
            str_a = f.read()
        with open(second) as f:
            str_b = f.read()

        if str_a != str_b:
            first_lines = str_a.splitlines(True)
            second_lines = str_b.splitlines(True)
            delta = difflib.unified_diff(
                first_lines, second_lines,
                fromfile=first, tofile=second)
            message = ''.join(delta)

            if msg:
                message += " : " + msg

            self.fail("Multi-line strings are unequal:\n" + message)

    def test_readJSONREF_json(self):
        """
        Test JSONref using a JSON file.
        
        """
        fname_A =  PurePath(self.testing_path).joinpath("jsonref_A.json")
        print(f'File name : {fname_A}')
        dp = Datapath()
        A = ObsMetadata.read_json_yaml_ref(str(fname_A), dp, None)
        AB = ObsMetadata.read_json_yaml_ref(str(PurePath(self.testing_path).joinpath(
                                              "jsonref_AB.json")), None)
        self.assertTrue(A == AB)
        

    def test_readJSONREF_yaml(self):
        """
        Test JSONref using a YAML file.
        
        """
        
        dp = Datapath()
        A = ObsMetadata.read_json_yaml_ref(str(PurePath(self.testing_path).joinpath(
                                             "jsonref_A.yaml")), dp, None)
        AB = ObsMetadata.read_json_yaml_ref(str(PurePath(self.testing_path).joinpath(
                                              "jsonref_AB.yaml")), dp, None)
        self.assertTrue(A == AB)


    def test_validate_json(self):
        """
        Test validation on a YAML file.

        The test file as an $ref to a file that doesn't exist, a field that
        is not specified in the the schema, and lacks a field required in
        the schema
        
        """
        test_file = PurePath(self.testing_path).joinpath( 'json_testschema.json')
        test_schema = PurePath(self.testing_path).joinpath(
                                   'json_testschema.schema.json')
        # self.assertFalse(validate(test_file, schema_file=test_schema,
        #                           quiet=True))

        # Run the code
        cmd = f'obsinfo-validate -s {test_schema} {test_file} > temp'
        os.system(cmd)

        # Compare text files
        self.assertTextFilesEqual(
            'temp',
            str(PurePath(self.testing_path).joinpath( 'json_testschema.out.txt'))
            )
        os.remove('temp')
          

class TestObsinfo(unittest.TestCase):
    """
    Test suite and print methods for obsinfo operations.
    
     **Attributes:**
    
        * infofiles_path (str): path to datafiles to be tested 
        * level (str): level to be printed
        * test (boolean): determines if this is test mode
        * print_output (boolean): determines if this is print mode. Both can coexist.
    
    """
        
    def setUp(self, test=True, print_output=False, level=None):
        """
        Set up default values and paths
        
        :param: test - Invoke class methods in test mode, i.e. invoke assertions as well as obsinfo object creation
        :type test: boolean
        :param: print_output - Invoke class methos in print mode, no assertions.
        :type print_output: boolean
        :param: level - In print mode, determine up to which level information will be printed
        :type level: string
        
        """   
        self.infofiles_path =  Datapath()
    
        self.level = level
        self.test = test
        self.print_output = print_output
        
        
    def test_all_filters(self):
        """
        Test all information files in both examples and test/data/Information_Files/_filters" subdirectory
        If you wish to test individual files, use test_filter(file) with file an absolute or 
        relative file name.
        """
        for dir in self.infofiles_path.datapath_list:
            files_in_validate_dir = Path(dir).joinpath(
                "*rs", # includes sensors, preamplifiers and dataloggers
                "responses",
                "filters/*.yaml")
            
            filelist = glob.glob(str(files_in_validate_dir)) + glob.glob(str(Path(os.getcwd()).joinpath("obsinfo", "tests", "data", 
                "Information_Files", "filters", "*/*.yaml")))
            
            for file in filelist:
                self._test_filter(file)
            
            #if self.test:
            #   self._test_PZ_conditionals()
                    

    def _test_filter(self, info_file):
        """
        Test and/or print a filter file. 
        
        All are actual examples except the info files called "test---attributes. 
        In this special cases there will also be a comparison against a dict of expected results.
        This comparison occurs for all four main types of filters.
        
        :param: info_file - Filename to test or print
        :type info_file: str
        
        """
        test_expected_result = { 
            'PolesZeros' : 
                {
                    "type": "PolesZeros",
                    "transfer_function_type": "LAPLACE (RADIANS/SECOND)",
                    "zeros": [(0.0+0.0j)],
                    "poles": [(0.546+0.191j), (4.00004e4+0.000j),],
                    "normalization_frequency" : 1.,
                    "normalization_factor" : 42833.458122775904,
                    "offset": 0,  
                },
            'FIR' : 
                {
                    "type": "FIR",
                    "symmetry": "ODD",
                    "coefficient_divisor": 8388608,
                    "coefficients": [-10944, 0, 103807, 0, -507903, 0, 2512192, 4194304,],
                    "offset": 7,  
                },
            'Coefficients' : 
                {
                    "type" : "Coefficients",
                    "transfer_function_type" : "DIGITAL", 
                    "numerator_coefficients" :   [1, 0.1, -0.3, 0.6],
                    "denominator_coefficients" : [-0.2, 0.8, 0.4, -0.3],
                    "offset": 0,
                },
            'ResponseList' : 
                {
                    "type" : "ResponseList",
                    "offset": 0,  
                    "response_list" : [[ 0.050, 0.56, 0.0], [ 0.075, 0.73, 0.0], [ 1, 1, 0.0], [10, 0.97, -179], [100, 0.96, 179], [1000, 0.96, 179], [5000, 0.82, 143], [7500, 0.69, 129]],
                },
            'AD_CONVERSION' : 
                {
                    "type" : "AD_CONVERSION",
                    "input_full_scale" : 5,
                    "output_full_scale" : 4294967292,
                    "transfer_function_type" : "DIGITAL",
                    "numerator_coefficients" :   [1.0],
                    "denominator_coefficients" : [],
                    "offset": 0,  
                },
            'ANALOG' : 
                {
                    "type" : "ANALOG",
                    "transfer_function_type" : "LAPLACE (RADIANS/SECOND)",
                    "zeros": [],
                    "poles": [],
                    "normalization_frequency" : 0.,
                    "normalization_factor" : 1.0,
                    "offset": 0,      
                },
            'DIGITAL' : 
                {
                    "type" : "DIGITAL",
                    "transfer_function_type" : "DIGITAL",
                    "numerator_coefficients" :   [1.0],
                    "denominator_coefficients" : [],
                    "offset": 0,                   
                },
             }
            
        read_stream = ObsMetadata.read_info_file(info_file, self.infofiles_path)
        obj = Filter.dynamic_class_constructor(ObsMetadata(read_stream['filter']), "")
        
        if verbose:  
           print(f'Processing filter file:"{info_file}"')
           
        if self.test:    
        #   self.assertTrue(isinstance(obj, obj.type), f'Object {info_file} is not a {obj.type} filter')    
            
           if re.match("test---attributes", str(info_file)): # compare with expected result
               self._filter_compare(info_file, obj, test_expected_result)
        
        
        if verbose:
           print(f'Filter test for: {info_file}: PASSED')
        
        if self.print_output:    
           print(obj)
           
    
    def _filter_compare(self, info_file, filter, expected_result):
        """
        Test a created filter object against an expected result to make sure all values are right
        
        :param: info_file - Filename to test or print
        :type info_file: str
        :param: filter - type of filter
        :type filter: str
        :param: expected_result - dictionary containing attributes to test against
        :type expected_result: dict
        
        """
        ftype = filter.type 
        read_dict = vars(filter)
        
        # Remove notes and extras
        if read_dict.get('notes', None) == []:
            read_dict.pop('notes')
        if read_dict.get('extras', None) == None:
            read_dict.pop('extras')
        
        self.assertEqual(read_dict,expected_result.get(ftype, None), 
f" File: '{info_file}'. Computed result: {read_dict} and expected result: {expected_result.get(ftype, None)} are different")
        
    
    def _test_PZ_conditionals(self):
        """
        Test all the conditionals in the PZ filter. In particular, this tests the function
        to calculate the normalization factor.
        
        """
        obj = Filter.dynamic_class_constructor(ObsMetadata({'type': 'PolesZeros', 
                                         'transfer_function_type' : 'LAPLACE (RADIANS/SECOND)',
                                         'zeros': [[0.3, 0.2],],
                                         'poles': [[0.546, 0.191], [4.40e4, 0.000],],
                                         'normalization_frequency' : 1.,
                                         'normalization_factor' : None,
                                          }), None, None, None)
        self.assertIn(obj.transfer_function_type, ['LAPLACE (RADIANS/SECOND)', 'LAPLACE (HERTZ)', 'DIGITAL (Z-TRANSFORM)'], 
                                              f'transfer function type wrong in test case for PZ {obj.transfer_function_type}')
        self.assertEqual(obj.normalization_factor,  44188.013594177224, 
                f'object normalization factor in test case for PZ {obj.normalization_factor} in PZ test is different from 44188.013594177224')
        print("1", end=" ")
        
        obj = Filter.dynamic_class_constructor(ObsMetadata({'type': 'PolesZeros', 
                                         'transfer_function_type' : 'LAPLACE (HERTZ)',
                                         'zeros': [[0.3, 0.2],],
                                         'poles': [[0.546, 0.191], [4.40e4, 0.000],],
                                         'normalization_frequency' : 1.,
                                         'normalization_factor' : None,
                                          }), None, None, None)
        self.assertIn(obj.transfer_function_type, ['LAPLACE (RADIANS/SECOND)', 'LAPLACE (HERTZ)', 'DIGITAL (Z-TRANSFORM)'], 
                                              f'transfer function type wrong in test case for PZ {obj.transfer_function_type}')
        self.assertEqual(obj.normalization_factor,  50262.70428857582, 
                    f'object normalization factor in test case for PZ {obj.normalization_factor} is different from 50262.70428857582')
        print("2", end=" ")
        
        obj = Filter.dynamic_class_constructor(ObsMetadata({'type': 'PolesZeros', 
                                         'transfer_function_type' : 'LAPLACE (RADIANS/SECOND)',
                                         'zeros': [[0.3, 0.2],],
                                         'poles': [[0.546, 0.191], [4.40e4, 0.000],],
                                         'normalization_frequency' : 120.,
                                         'normalization_factor' : None,
                                          }), None, None, None)
                                          
        self.assertEqual(obj.normalization_factor, 44006.99311749303, f'{obj.normalization_factor} in test case for PZ is different from 44006.99311749303')
        print("3", end=" ")
        
        obj = Filter.dynamic_class_constructor(ObsMetadata({'type': 'PolesZeros', 
                                         'transfer_function_type' : 'LAPLACE (RADIANS/SECOND)',
                                         'zeros': [],
                                         'poles': [],
                                         'normalization_frequency' : 1.,
                                         'normalization_factor' : None,
                                          }), None, None, None)
        
        self.assertEqual(obj.normalization_factor, 1., f'{obj.normalization_factor} is different from 1.')
        print("4", end=" ")
        
        obj = Filter.dynamic_class_constructor(ObsMetadata({'type': 'PolesZeros', 
                                         'transfer_function_type' : 'DIGITAL (Z-TRANSFORM)',
                                         'zeros': [[0.3, 0.2],],
                                         'poles': [[0.546, 0.191], [4.40e4, 0.000],],
                                         'normalization_frequency' : 1.,
                                         'normalization_factor' : None,
                                          }), None, None, None)
        
        self.assertIn(obj.transfer_function_type, ['LAPLACE (RADIANS/SECOND)', 'LAPLACE (HERTZ)', 'DIGITAL (Z-TRANSFORM)'], 
                                              f'transfer function type wrong in test case for PZ {obj.transfer_function_type}')
        self.assertEqual(obj.normalization_factor,  None, 
                    f'object normalization factor {obj.normalization_factor} is different from None')
        print("5", end=" ")
        
        obj = Filter.dynamic_class_constructor(ObsMetadata({'type': 'PolesZeros', 
                                         'transfer_function_type' : 'LAPLACE (RADIANS/SECOND)',
                                         'zeros': [[0.3, 0.2],],
                                         'poles': [[0.546, 0.191], [4.40e4, 0.000],],
                                         'normalization_frequency' : None,
                                         'normalization_factor' : None,
                                          }), None, None, None)
        
        self.assertEqual(obj.normalization_factor, None, f'{obj.normalization_factor} is different from None')
        print("6: Should have returned error", end=" ")
        
    
    def _test_all_stage_types(self):
        """
        Test reading and converting to obspy a stage file with each filter type. 
        
        This is the first time obspy conversion occurs so make sure it's done right
        Only one example stage for each type. If you wish to test all stage files,
        use test_all_responses(). If you wish to test individual files use test_stage
        with file as stripped file name. 
        File must exist in obsinfo/Information_files/XXX/responses
        where XXX = sensor, preamplifier or datalogger
        
        """
        
        self.test_stage('TI_ADS1281_FIR1.stage.yaml')
        self.test_stage('SIO-LDEO_DPG_5018_calibrated.stage.yaml')
        self.test_stage('test-with-coeff.stage.yaml')
        self.test_stage('test-with-response-list.stage.yaml')
        
    def test_all_stages(self):
        """
        Test all information files in each responses subdirectory.
        
        """
        for dir in self.infofiles_path.datapath_list:
            files_in_validate_dir = Path(dir).joinpath(
                "*rs", # includes sensors, preamplifiers and dataloggers
                "responses/*.yaml"
                )
            
            filelist = glob.glob(str(files_in_validate_dir))
            
            for file in filelist:
                self._test_stage(file)
        
        
    def _test_stage(self, file):
        """
        Test or print stage according to contained filter type
        
        :param: file - Filename to test or print
        :type file: str
        
        """
        if verbose:  
           print(f'Processing stage file:"{file}"')
         
        info_file_dict = ObsMetadata.read_info_file(file, self.infofiles_path)
           
        stage_from_info_file = Stage(ObsMetadata(info_file_dict['stage']))
        
        obspy_result = stage_from_info_file.to_obspy()
    
        if self.test:
            
            self._test_common_attributes(stage_from_info_file, obspy_result)
            
            if isinstance(filter, FIR):
                self.assertEqual(stage_from_info_file.filter.symmetry, obspy_result._symmetry)
                for info_file_coeff in stage_from_info_file.filter.coefficients:
                    for obspy_coeff in obspy_result.decimation_correction:
                        self.assertEqual(info_file_coeff / 512, obspy_coeff (f))
            elif isinstance(filter, PolesZeros):
                self.assertEqual(stage_from_info_file.filter.transfer_function_type, obspy_result.pz_transfer_function_type)
                self.assertEqual(stage_from_info_file.filter.normalization_frequency, obspy_result.normalization_frequency)
                self.assertEqual(stage_from_info_file.filter.normalization_factor, obspy_result.normalization_factor)
                self.assertEqual(stage_from_info_file.filter.zeros, obspy_result.zeros)
                self.assertEqual(stage_from_info_file.filter.poles, obspy_result.poles)
            elif isinstance(filter, ResponseList):
                self.assertEqual(stage_from_info_file.filter.response_list, obspy_result.response_list_elements)
            elif isinstance(filter, Coefficients):
                self.test_common_attributes(stage_from_info_file, obspy_result)
                self.assertEqual(stage_from_info_file.filter.transfer_function_type, obspy_result.cf_transfer_function_type)
                self.assertEqual(stage_from_info_file.filter.numerator_coefficients, obspy_result.numerator)
                self.assertEqual(stage_from_info_file.filter.denominator_coefficients, obspy_result.denominator)                
                
        if verbose:
            print(f'Stage test for: {file}: PASSED')
            
        if self.print_output:
            print(obj)
            if self.level == "all":
                print(s.filter) 
    
    def _test_common_attributes(self, stage_from_info_file, obspy_result):
        """
        Test attributes common to all stages
        
        :param stage_from_info_file:  Stage portion of dictionary with attributes
        :type stage_from_info_file: object of class:`Stage`
        :param obspy_result: Dictionary generated by obspy with corresponding attributes
        :type obspy_result: object of class ``Stage`` in ``osbpy.core.inventory.response``
        
        """
        
        self.assertEqual(stage_from_info_file.name, obspy_result.name)
        self.assertEqual(stage_from_info_file.description, obspy_result.description)
        self.assertEqual(stage_from_info_file.input_units, obspy_result.input_units)
        self.assertEqual(stage_from_info_file.output_units, obspy_result.output_units)
        self.assertEqual(stage_from_info_file.input_units_description, obspy_result.input_units_description)
        self.assertEqual(stage_from_info_file.output_units_description, obspy_result.output_units_description)
        self.assertEqual(stage_from_info_file.gain, obspy_result.stage_gain)
        self.assertEqual(stage_from_info_file.gain_frequency, obspy_result.stage_gain_frequency)
        self.assertEqual(stage_from_info_file.decimation_factor, obspy_result.decimation_factor)
        self.assertEqual(stage_from_info_file.filter.offset, obspy_result.decimation_offset)
        self.assertEqual(stage_from_info_file.delay, obspy_result.decimation_delay)
        self.assertEqual(stage_from_info_file.correction, obspy_result.decimation_correction)
         
         
    def _test_response_stage_addition(self):
        """
        Test reading and combining response_stages from a sensor and a datalogger
        
        """
        
        read_info_A = ObsMetadata.read_info_file(PurePath(self.infofiles_path).joinpath( 
            'sensors',
            'responses',
            'Trillium_T240_SN400-singlesided_theoretical.stage.yaml'))
        read_info_B = ObsMetadata.read_info_file(PurePath(self.infofiles_path).joinpath(
            'dataloggers',
            'responses',
            'TexasInstruments_ADS1281_100sps-linear_theoretical.response_stages.yaml'))
        stages_A = ResponseStages(read_info_A['response']['stages'])
        stages_B = ResponseStages(read_info_B['response']['stages'])
        stages = stages_A + stages_B
        
        
    def test_all_components(self):
        """
        Test all information files in each components directory.
        
        """
        components_list = [
            "sensors",
            "preamplifiers",
            "dataloggers"
            ]
        
        for dir in self.infofiles_path.datapath_list:
            for comp in components_list:
                files_in_validate_dir = Path(dir).joinpath(
                    comp,
                    "*.yaml"  # includes sensors, preamplifiers and dataloggers
                    )
                
                filelist = glob.glob(str(files_in_validate_dir))
                
                for file in filelist:
                    if verbose:   
                       print(f'Processing component file: {file}')
                       
                    info_file_dict = ObsMetadata.read_info_file(file, self.infofiles_path)
        
                    #OJO: no configuraton passed from above. No delay_correction either.
                    obj = InstrumentComponent.dynamic_class_constructor(comp[:-1], info_file_dict)
                    
                    if self.test:
                        self.assertTrue(type(obj), comp[:-1])
                        self._test_equipment_attributes(obj.equipment, obj.equipment.obspy_equipment)
                                      
                    if verbose:   
                       print(f'{file}: PASSED')
                       
                    if self.print_output:
                        PrintObs.print_component(obj, self.level)
     
     
    def _test_equipment_attributes(self, equipment_from_info_file, obspy_result):
        """
        Tesl the equipment portion of a component or instrumentation
        
        :param: equipment_from_info_file - Stage portion of dictionary with attributes
        :type equipment:  object of class:`Stage`
        :param: obspy_result - Dictionary generated by obspy with corresponding attributes
        :type obspy_result: object of class ``Stage`` in ``osbpy.core.inventory.response`
        
        """
        
        try:  
            self.assertEqual(equipment_from_info_file.type, obspy_result.type)
            self.assertEqual(equipment_from_info_file.description, obspy_result.description)
            self.assertEqual(equipment_from_info_file.manufacturer, obspy_result.manufacturer)
            self.assertEqual(equipment_from_info_file.model, obspy_result.model)
            self.assertEqual(equipment_from_info_file.vendor, obspy_result.vendor)
            self.assertEqual(equipment_from_info_file.serial_number, obspy_result.serial_number)
            self.assertEqual(UTCDateTime(equipment_from_info_file.installation_date) if equipment_from_info_file.installation_date\
                                          else None, obspy_result.installation_date)
            self.assertEqual(UTCDateTime(equipment_from_info_file.removal_date) if equipment_from_info_file.removal_date\
                                          else None, obspy_result.removal_date)
            for dt, obspy_dt in zip(equipment_from_info_file.calibration_dates, obspy_result.calibration_dates):
                self.assertEqual(UTCDateTime(dt) if dt else None, obspy_dt)        
            self.assertEqual(equipment_from_info_file.resource_id, obspy_result.resource_id)
        except TypeError:
            print(f"TypeError, probably in UTCDateTime conversion")
            
            
    def test_sensor_configurations(self):
        """
        Test cases for configurations of particular sensor examples
        
        Will test what happens if no default is specified, if a default is specified and if default is overridden
        
        WARNING: Depends critically on the expected values of information files. If these change, tests will fail.
        
        """
        component_dir = Path(os.getcwd()).joinpath("obsinfo", "tests", "data", 
                "Information_Files", "components")
        
        sensor_wo_configs = str(component_dir.joinpath("HITECH_HTI04-PLC-ULF-wo-configs.sensor.yaml"))
        sensor_w_default = str(component_dir.joinpath("NANOMETRICS_T240_w_config_and_default.sensor.yaml"))
        sensor_w_configs = str(component_dir.joinpath("NANOMETRICS_T240_w_config_no_default.sensor.yaml"))
        
        # expected value for all test cases
        expected_gain_value_1 = 0.000195
        expected_gain_value_2 = 598.45
        expected_gain_value_3 = 594.5
                
        if verbose:
            print(f'Processing sensor file w/o configurations: {sensor_wo_configs}')
          
        # Case 1;
        # Expect message :"No configuration key or default found in sensor. Configurations, if present, will not be applied
        
        obj = self._read_and_get_component(sensor_wo_configs, "sensor")
        self.assertEqual(obj.response_stages.stages[0].gain,  expected_gain_value_1)
             
        if verbose:
            print(f'Processing sensor file with default and configurations: {sensor_w_default}')
          
        # Case 2;
        # Expect default to be applied as no other configuration is specified
        # Assumes configuration_default: "SINGLE-SIDED_SN1-399"
        obj = self._read_and_get_component(sensor_w_default, "sensor")
        self.assertEqual(obj.response_stages.stages[0].gain,  expected_gain_value_2)
        
        # Expect default to be overridden by selection specified
        obj = self._read_and_get_component(sensor_w_default, "sensor", config_selector="SINGLE-SIDED_SN400plus")
        self.assertEqual(obj.response_stages.stages[0].gain,  expected_gain_value_3)
        
        if verbose:
            print(f'Processing sensor file with configurations: {sensor_w_configs}')
        
        # Case 3:  
        # Expect selected configuration selection to be applied as there is no default
        obj = self._read_and_get_component(sensor_w_configs, "sensor", config_selector="SINGLE-SIDED_SN400plus")
        self.assertEqual(obj.response_stages.stages[0].gain,  expected_gain_value_3)
        
        # Expect default to be overridden
        obj = self._read_and_get_component(sensor_w_configs, "sensor", config_selector="SINGLE-SIDED_SN400plus")
        self.assertEqual(obj.response_stages.stages[0].gain,  expected_gain_value_3)
        
        # Expect not to find configuration specified and no default and thus raise TypeError
        self.assertRaises(TypeError, self._read_and_get_component,  
                          sensor_w_configs, "sensor", config_selector="SGLE-SIDED_SN1-399")

        # This will raise an exception as there are no response_stages due to lack of selection
        self.assertRaises(TypeError, self._read_and_get_component, sensor_w_configs, "sensor")
       
    
    def test_preamp_configurations(self):
        """
        Test all configurations of particular preamp examples
        
        Will not test case 1 in test_sensor_configurations as it is common code. Will test what happens if configuration is not 
        found or is empty.
        
        WARNING: Depends critically on the expected values of information files. If these change, tests will fail.
        
        """
        component_dir = Path(os.getcwd()).joinpath("obsinfo", "tests", "data", 
                "Information_Files", "components")
        
        preamp_w_configs = str(component_dir.joinpath("LCHEAPO_HYDRO.preamplifier.yaml"))
        preamp_wo_default = str(component_dir.joinpath("LCHEAPO_HYDRO_wo_default.preamplifier.yaml"))
        preamp_w_empty_config = str(component_dir.joinpath("LCHEAPO_GEOPHONE.preamplifier.yaml"))
        preamp_w_empty_config_no_stages = str(component_dir.joinpath("LCHEAPO_GEOPHONE-no-stages.preamplifier.yaml"))
        
        # expected value for all test cases
        expected_gain_mult_1 = 16
        expected_gain_mult_2 = 32
        expected_gain_mult_3 = 64
        expected_gain_mult_4 = 128
        
        if verbose:
            print(f'Processing preamplifier file with configurations: {preamp_w_configs}')
                
        # Case 1;
        #Select different configs over default
        obj = self._read_and_get_component(preamp_w_configs, "preamplifier", config_selector="16x gain")
        self.assertEqual(obj.response_stages.stages[0].gain,  expected_gain_mult_1)
        
        obj = self._read_and_get_component(preamp_w_configs, "preamplifier", config_selector="32x gain")
        self.assertEqual(obj.response_stages.stages[0].gain,  expected_gain_mult_2)
        
        obj = self._read_and_get_component(preamp_w_configs, "preamplifier", config_selector="64x gain")
        self.assertEqual(obj.response_stages.stages[0].gain,  expected_gain_mult_3)
        
        obj = self._read_and_get_component(preamp_w_configs, "preamplifier", config_selector="128x gain")
        self.assertEqual(obj.response_stages.stages[0].gain,  expected_gain_mult_4)      
        
        if verbose:
            print(f'Processing preamplifier file without default: {preamp_wo_default}')
                 
        # Case 2:
        # select configuration without default
        obj = self._read_and_get_component(preamp_wo_default, "preamplifier", config_selector="128x gain")
        self.assertEqual(obj.response_stages.stages[0].gain,  expected_gain_mult_4)
        
        # Case 3:
        # No select configuration, no  default config
        # Since a default response_stages is specified, it should be used
        obj = self._read_and_get_component(preamp_wo_default, "preamplifier")
        self.assertEqual(obj.response_stages.stages[0].gain,  expected_gain_mult_3)
        
        if verbose:
            print(f'Processing preamplifier file with empty config: {preamp_w_empty_config}')
                     
        # Case 4:
        # Config cannot be found. Expect message: Configuration selected "128x gain" in preamplifier not found in configuration definitions, using default configuration
        obj = self._read_and_get_component(preamp_w_empty_config, "preamplifier", config_selector="16x")
        self.assertEqual(obj.response_stages.stages[0].gain,  expected_gain_mult_4)
        
        # Case 5:
        # Config cannot be found, there is a default.
        # Expect selected configuration selection to be applied instead of default
        obj = self._read_and_get_component(preamp_w_empty_config, "preamplifier", config_selector="128x")
        self.assertEqual(obj.response_stages.stages[0].gain,  expected_gain_mult_4)
        
        # Case 6:
        # Config cannot be found, there is no default, response_stage list is empty
        # This just checks how resilient the default behaviour is
        obj = self._read_and_get_component(preamp_w_empty_config, "preamplifier", config_selector="128x")
        self.assertEqual(obj.response_stages.stages[0].gain,  expected_gain_mult_4)
        
        # Case 6:
        # Config cannot be found, there is no default, response_stage list is empty
        # Expect this to raise an exception
        self.assertRaises(TypeError, self._read_and_get_component, 
                          preamp_w_empty_config_no_stages, "preamplifier", config_selector="128x")
        
    
    def test_datalogger_configurations(self):
        """
        Test all configurations of a particular datalogger example
        
        Will not test case 1 in test_sensor_configurations as it is common code. Will test what happens if configuration is not 
        found or is empty.
        
        WARNING: Depends critically on the expected values of information files. If these change, tests will fail.
        
        """
        component_dir = Path(os.getcwd()).joinpath("obsinfo", "tests", "data", 
                "Information_Files", "components")
        
        datalogger_w_configs = str(component_dir.joinpath("LC2000.datalogger.yaml"))
       
        # expected value for all test cases
        expected_sample_rate_1 = 62.5
        expected_sample_rate_2 = 125
        expected_sample_rate_3 = 250
        expected_sample_rate_4 = 500
        expected_sample_rate_5 = 1000
        
        if verbose:
            print(f'Processing datalogger file with configurations: {datalogger_w_configs}')
                
        # Case 1;
        #Select different configs over default
        obj = self._read_and_get_component(datalogger_w_configs, "datalogger", config_selector="62.5sps")    
        self.assertEqual(self._calc_sample_rate(obj.response_stages.stages), expected_sample_rate_1)
        
        obj = self._read_and_get_component(datalogger_w_configs, "datalogger", config_selector="125sps")
        self.assertEqual(self._calc_sample_rate(obj.response_stages.stages),  expected_sample_rate_2)
        
        obj = self._read_and_get_component(datalogger_w_configs, "datalogger", config_selector="250sps")
        self.assertEqual(self._calc_sample_rate(obj.response_stages.stages),  expected_sample_rate_3)
        
        obj = self._read_and_get_component(datalogger_w_configs, "datalogger", config_selector="500sps")
        self.assertEqual(self._calc_sample_rate(obj.response_stages.stages),  expected_sample_rate_4)
        
        obj = self._read_and_get_component(datalogger_w_configs, "datalogger", config_selector="1000sps")
        self.assertEqual(self._calc_sample_rate(obj.response_stages.stages),  expected_sample_rate_5)         
    
    
    def _calc_sample_rate(self, stage_list):
        """
        Calculates the total sample rate for the response using a different method than the
        actual program
        
        :param stage_list: stages with input_sample_rate and decimation_factor
        :type stage_list: list of objects of :class:`Stage`
        :returns: the calculated sample rate
        
        """
    
        sample_rate = stage_list[0].input_sample_rate
        for st in stage_list[1:]:
            sample_rate /= st.decimation_factor 
            
        return sample_rate
                    
           
    def _read_and_get_component(self, file, component, 
                                  channel_modif={},
                                  delay_correction=None, 
                                  config_selector=''):
        """
        Read a component information file and create corresponding *obsinfo* object
        
        :param file: filename of information file with complete path
        :type file: str
        :param component: type of component
        :type component: str
        :returns: object of :class:`Information_Component`
        """
        info_file_dict = ObsMetadata.read_info_file(file, self.infofiles_path)
        obj = InstrumentComponent.dynamic_class_constructor(component, info_file_dict, config_selector=config_selector)
        
        return obj
                         
    
    def test_all_instrumentations(self):
        """
        Test all information files in instrumentation directory
        
        """
        for dir in self.infofiles_path.datapath_list:
            files_in_validate_dir = Path(dir).joinpath(
                "instrumentation/*.yaml" # includes sensors, preamplifiers and dataloggers
                )
            
            filelist = glob.glob(str(files_in_validate_dir))
            
            for file in filelist:
                self._test_instrumentation(file)
                
         
    def _test_instrumentation(self, file):
        """
        Test or print a single instrumentation file
        
        WARNING: Response is assumed to be checked stage by stage at the stage level (test_stage), 
        Here some trivial checks are done, such as number of stages
        SENSITIVITY MUST BE CHECKED MANUALLY in the StationXML file
        
        :param: file - Filename to test or print
        :type file: str
        
        """
        
        dict = ObsMetadata.read_info_file(file, self.infofiles_path)
        
        start_date = end_date = "2021-01-03"
        
        # create a dummy location dictionary for testing
        location_dict = {
                          "00": 
                             {"position": {"lon": 0., "lat": 0., "elev": 200.},
                              "base":  { 
                                "depth.m": 100.,
                                "geology": "unknown",
                                "vault": "Sea floor",
                                "uncertainties.m": {"lon": 1., "lat": 1., "elev": 1.},
                                "localisation_method": "Sea surface release point",
                                }
                              },
                           "01":
                             {"position": {"lon": 0., "lat": 0., "elev": 300.},
                              "base":  { 
                                "depth.m": 200.,
                                "geology": "unknown",
                                "vault": "Sea floor",
                                "uncertainties.m": {"lon": 2., "lat": 2., "elev": 2.},
                                "localisation_method": "Sea surface release point"
                                }
                              },
                           "02":
                             {"position": {"lon": 0., "lat": 0., "elev": 300.},
                              "base":  { 
                                "depth.m": 200.,
                                "geology": "unknown",
                                "vault": "Sea floor",
                                "uncertainties.m": {"lon": 2., "lat": 2., "elev": 2.},
                                "localisation_method": "Sea surface release point"
                                }
                              },
                           "03":
                             {"position": {"lon": 0., "lat": 0., "elev": 300.},
                              "base":  { 
                                "depth.m": 200.,
                                "geology": "unknown",
                                "vault": "Sea floor",
                                "uncertainties.m": {"lon": 2., "lat": 2., "elev": 2.},
                                "localisation_method": "Sea surface release point"
                                }
                              },
                           "04":
                             {"position": {"lon": 0., "lat": 0., "elev": 300.},
                              "base":  { 
                                "depth.m": 200.,
                                "geology": "unknown",
                                "vault": "Sea floor",
                                "uncertainties.m": {"lon": 2., "lat": 2., "elev": 2.},
                                "localisation_method": "Sea surface release point"
                                }
                              },
                           "05":
                             {"position": {"lon": 0., "lat": 0., "elev": 300.},
                              "base":  { 
                                "depth.m": 200.,
                                "geology": "unknown",
                                "vault": "Sea floor",
                                "uncertainties.m": {"lon": 2., "lat": 2., "elev": 2.},
                                "localisation_method": "Sea surface release point"
                                }
                               },
                           "06":
                             {"position": {"lon": 0., "lat": 0., "elev": 300.},
                              "base":  { 
                                "depth.m": 200.,
                                "geology": "unknown",
                                "vault": "Sea floor",
                                "uncertainties.m": {"lon": 2., "lat": 2., "elev": 2.},
                                "localisation_method": "Sea surface release point"
                                }
                               },
                           "06":
                             {"position": {"lon": 0., "lat": 0., "elev": 300.},
                              "base":  { 
                                "depth.m": 200.,
                                "geology": "unknown",
                                "vault": "Sea floor",
                                "uncertainties.m": {"lon": 2., "lat": 2., "elev": 2.},
                                "localisation_method": "Sea surface release point"
                                }
                               },
                           "07":
                             {"position": {"lon": 0., "lat": 0., "elev": 300.},
                              "base":  { 
                                "depth.m": 200.,
                                "geology": "unknown",
                                "vault": "Sea floor",
                                "uncertainties.m": {"lon": 2., "lat": 2., "elev": 2.},
                                "localisation_method": "Sea surface release point"
                                }
                               },
                           "08":
                             {"position": {"lon": 0., "lat": 0., "elev": 300.},
                              "base":  { 
                                "depth.m": 200.,
                                "geology": "unknown",
                                "vault": "Sea floor",
                                "uncertainties.m": {"lon": 2., "lat": 2., "elev": 2.},
                                "localisation_method": "Sea surface release point"
                                }
                               },
                           "09":
                             {"position": {"lon": 0., "lat": 0., "elev": 300.},
                              "base":  { 
                                "depth.m": 200.,
                                "geology": "unknown",
                                "vault": "Sea floor",
                                "uncertainties.m": {"lon": 2., "lat": 2., "elev": 2.},
                                "localisation_method": "Sea surface release point"
                                }
                               },
                         }
        
        
     
        locations = {c: Location(v) for c, v in location_dict.items()}
                
        if verbose:  
           print(f'Processing instrumentation file:"{file}"')
           
        obj = Instrumentation(ObsMetadata(dict['instrumentation']), locations, start_date, end_date, {})
        
        if self.test:
           for ch in obj.channels:
              
              self.assertEqual(ch.channel_code(ch.instrument.sample_rate), ch.obspy_channel.code) #Checks that code is well built according to sample rate
              self.assertEqual(ch.location_code, ch.obspy_channel.location_code)
              self.assertEqual(ch.location.obspy_latitude, ch.obspy_channel.latitude)
              self.assertEqual(ch.location.obspy_longitude, ch.obspy_channel.latitude)
              self.assertEqual(ch.location.elevation, ch.obspy_channel.elevation)
              self.assertEqual(ch.location.depth_m, ch.obspy_channel.depth)
              self.assertEqual(ch.orientation.azimuth, ch.obspy_channel.azimuth)
              self.assertEqual(ch.orientation.dip, ch.obspy_channel.dip)
              self.assertEqual(ch.instrument.sample_rate, ch.obspy_channel.sample_rate)
              self.assertEqual(ch.instrument.sensor.equipment.obspy_equipment, ch.obspy_channel.sensor)
              self.assertEqual(ch.instrument.datalogger.equipment.obspy_equipment, ch.obspy_channel.data_logger)
              preamp = ch.instrument.preamplifier.equipment.obspy_equipment if ch.instrument.preamplifier else None
              self.assertEqual(preamp, ch.obspy_channel.pre_amplifier)
              self.assertEqual(UTCDateTime(ch.start_date) if ch.start_date\
                                          else None, ch.obspy_channel.start_date)
              self.assertEqual(UTCDateTime(ch.end_date) if ch.end_date\
                                          else None, ch.obspy_channel.end_date)
              self.assertEqual(ch.channel_id_code, ch.obspy_channel.description)
              self.assertEqual(len(ch.instrument.response_stages), len(ch.obspy_channel.response.response_stages))
              
              self._test_equipment_attributes(obj.equipment, obj.equipment.obspy_equipment)
              
              if verbose: 
                  for st in ch.instrument.obspy_response.response_stages:
                        print(f'Stage label:{st.name} Stage description: {st.description} Stage number:{st.stage_sequence_number}')  
                            
        if verbose:   
           print(f'{file}: PASSED')
        
        if self.print_output:
            PrintObs.print_instrumentation(obj, self.level)
            
        
    def _test_station(self, file_name="", info_dict={}, read_file=True):
        """
        Test or print a station.
        
        :param: file_name - Filename to test or print
        :type file_name: str
        :param: info_dict - If not reading file, MUST provide an info_dict with the info
        :type info_dict: dict or object of :class:`ObsMetadata`
        :param: read_file - indicates whether file should be read or info_dict will be provided
        :type read_file: boolean
        
        WARNING: Comments, extras and Processing string must be checked visually
        WARNING: Check operator visually
        
        """
        
        if self.test and not read_file and not info_dict:
            print("MUST provide info_dict if read_file is False")
        
        if read_file:           
            info_dict = ObsMetadata.read_info_file(file_name, self.infofiles_path)
            info_dict = info_dict['station']
            
        key = list(info_dict.keys())[0]
        value = ObsMetadata(list(info_dict.values())[0])
        
        obj = Station(key, value)
        
        if self.test:
            latitude, longitude = Location.get_obspy_latitude_and_longitude(obj.location) 
            site = Site(name=obj.site, description=None, town=None, county=None, region=None, country=None)      
            self.assertEqual(obj.label, obj.obspy_station.code)
            self.assertEqual(site.name, obj.obspy_station.site.name)
            self.assertEqual(UTCDateTime(obj.start_date) if obj.start_date else None, obj.obspy_station.creation_date)
            self.assertEqual(UTCDateTime(obj.end_date) if obj.end_date else None, obj.obspy_station.termination_date)
            self.assertEqual(obj.restricted_status, obj.obspy_station.restricted_status)
            self.assertEqual(latitude, obj.obspy_station.latitude)
            self.assertEqual(longitude, obj.obspy_station.longitude)
            self.assertEqual(obj.location.elevation, obj.obspy_station.elevation)
            self.assertEqual(obj.location.vault, obj.obspy_station.vault)
            self.assertEqual(obj.location.geology, obj.obspy_station.geology)
            
            # Check if locations are correctly assigned to channels
            for ch in obj.instrumentation.channels:
                try:
                    self.assertEqual(obj.locations[ch.location_code].latitude, ch.location.latitude)
                except TypeError:
                    pass 
            
            # Check number of channels OK
            num_channels = len(obj.instrumentation.channels)
            self.assertEqual(num_channels, len(obj.obspy_station.channels))
            self.assertEqual(num_channels, obj.obspy_station.total_number_of_channels)
            self.assertEqual(num_channels, obj.obspy_station.selected_number_of_channels)                  
                                       
        if verbose:
           print(f'Processing station file: {file_name}: PASSED')
           
        if self.print_output:
            PrintObs.print_station(obj, self.level)
            
    
    def test_all_networks(self):
        """
        Test all information files in network directory
        
        """ 
        
        for dir in self.infofiles_path.datapath_list:
            files_in_validate_dir = Path(dir).joinpath(
                "network/*.yaml" # includes sensors, preamplifiers and dataloggers
                )
            
            filelist = glob.glob(str(files_in_validate_dir))
            
            for file in filelist:
                self._test_network(file)
                    
             
    def _test_network(self, file_name):
        """
        Test or print a network information file
        
        :param: file_name - Filename to test or print
        :type file_name: str
        
        WARNING: Check operator visually
        
        """
        
        info_dict = ObsMetadata.read_info_file(file_name, self.infofiles_path)
        
        net_dict = info_dict.get('network',None)
        if not net_dict:
            return 
        
        if verbose:
            print(f'Processing network file: {file_name}')
            
        obj = Network(ObsMetadata(net_dict))
        
        if self.test:
            description = obj.fdsn_name + " -" + obj.description
            self.assertEqual(obj.fdsn_code, obj.obspy_network.code)
            self.assertEqual(UTCDateTime(obj.start_date) if obj.start_date else None, obj.obspy_network.start_date)
            self.assertEqual(UTCDateTime(obj.end_date) if obj.end_date else None, obj.obspy_network.end_date)
            self.assertEqual(obj.restricted_status, obj.obspy_network.restricted_status)
           
            # Check number of channels OK
            num_stations = len(obj.stations)
            self.assertEqual(num_stations, len(obj.obspy_network.stations))
            self.assertEqual(num_stations, obj.obspy_network.total_number_of_stations)
            self.assertEqual(num_stations, obj.obspy_network.selected_number_of_stations) 
            
            self._test_station(info_dict=net_dict['stations'], read_file=False)  
              
        if verbose:
           print(f'Network test for: {file_name}: PASSED')
           
        if self.print_output:
            PrintObs.print_network(obj, self.level)
       
    def test_change_modifications(self):
        """
        Test all possible channel modification and response modification labels
        
        Uses several test network information files plus a test instrumentation file in _examples.
        Rationale for each assertEqual is given in the test information files themselves 
        
        The five first tests check channel modification labels and their priorities. The last one
        checks response_modifications
        
        WARNING: Depends critically on the expected values of information files. If these change, tests will fail.
        
         * channel 0 - 3-00
         * channel 1 - H-00
         * channel 2 - H-01
         * channel 3 - 3-02
         
        """
    
        expected_sample_rate = 62.5
        expected_sample_rate_2 = 500
        expected_sample_rate_3 = 250
        unchanged_sample_rate = 125
        
        if verbose:
            print(f'Processing network file with channel modifications: TEST-channel-mods-1.network.yaml')
              
        obj = self._create_test_network("TEST-channel-mods-1.network.yaml")
        inst = obj.stations[0].instrumentation
        
        self.assertEqual(inst.channels[0].instrument.sample_rate, expected_sample_rate)
        self.assertEqual(inst.channels[1].instrument.sample_rate, expected_sample_rate)
        self.assertEqual(inst.channels[2].instrument.sample_rate, unchanged_sample_rate)
        self.assertEqual(inst.channels[3].instrument.sample_rate, unchanged_sample_rate)
        
        if verbose:
            print(f'Processing network file with channel modifications: TEST-channel-mods-2.network.yaml')
        
        obj = self._create_test_network("TEST-channel-mods-2.network.yaml")
        inst = obj.stations[0].instrumentation
        
        self.assertEqual(inst.channels[0].instrument.sample_rate, expected_sample_rate)
        self.assertEqual(inst.channels[1].instrument.sample_rate, expected_sample_rate)
        self.assertEqual(inst.channels[2].instrument.sample_rate, expected_sample_rate_2)
        self.assertEqual(inst.channels[3].instrument.sample_rate, expected_sample_rate_3)
        
        if verbose:
            print(f'Processing network file with channel modifications: TEST-channel-mods-3.network.yaml')
                
        obj = self._create_test_network("TEST-channel-mods-3.network.yaml")
        inst = obj.stations[0].instrumentation
        
        self.assertEqual(inst.channels[0].instrument.sample_rate, expected_sample_rate_2)
        self.assertEqual(inst.channels[1].instrument.sample_rate, expected_sample_rate)
        self.assertEqual(inst.channels[2].instrument.sample_rate, expected_sample_rate)
        self.assertEqual(inst.channels[3].instrument.sample_rate, expected_sample_rate_3)
        
        if verbose:
            print(f'Processing network file with channel modifications: TEST-channel-mods-4.network.yaml')
        
        obj = self._create_test_network("TEST-channel-mods-4.network.yaml")
        inst = obj.stations[0].instrumentation
        
        self.assertEqual(inst.channels[0].instrument.sample_rate, expected_sample_rate)
        self.assertEqual(inst.channels[1].instrument.sample_rate, expected_sample_rate)
        self.assertEqual(inst.channels[2].instrument.sample_rate, expected_sample_rate)
        self.assertEqual(inst.channels[3].instrument.sample_rate, expected_sample_rate)
        
        if verbose:
            print(f'Processing network file with channel modifications: TEST-channel-mods-5.network.yaml')
        
        obj = self._create_test_network("TEST-channel-mods-5.network.yaml")
        inst = obj.stations[0].instrumentation
        
        self.assertEqual(inst.channels[0].instrument.sample_rate, expected_sample_rate_3)
        self.assertEqual(inst.channels[1].instrument.sample_rate, expected_sample_rate)
        self.assertEqual(inst.channels[2].instrument.sample_rate, expected_sample_rate)
        self.assertEqual(inst.channels[3].instrument.sample_rate, expected_sample_rate_3)
        
        
        # check response stages
        expected_gain =  123456.
        expected_coeff_1 = [0,1,2,3,4]
        expected_symm_1 = "ODD"
        expected_coeff_2 = [5,6,4,6]
        expected_symm_2 = "EVEN"
        expected_descr = "Labeled modifications"
        
        if verbose:
            print(f'Processing network file with stage modifications: TEST-stage-mods-1.network.yaml')
        
        obj = self._create_test_network("TEST-stage-mods-1.network.yaml")
        inst = obj.stations[0].instrumentation
        
        ins = inst.channels[0].instrument 
        
        self.assertEqual(ins.sample_rate, expected_sample_rate)
        self.assertEqual(ins.sensor.response_stages.stages[0].gain, expected_gain)
        # just check a few, all should be expected_gain
        self.assertEqual(ins.datalogger.response_stages.stages[1].gain, expected_gain)
        self.assertEqual(ins.datalogger.response_stages.stages[4].gain, expected_gain)
        self.assertEqual(ins.datalogger.response_stages.stages[8].gain, expected_gain)
        # check all in interval
        self.assertEqual(ins.datalogger.response_stages.stages[5].description, expected_descr)
        self.assertEqual(ins.datalogger.response_stages.stages[6].description, expected_descr)
        self.assertEqual(ins.datalogger.response_stages.stages[7].description, expected_descr)
        self.assertEqual(ins.datalogger.response_stages.stages[8].description, expected_descr)
        
        ins = inst.channels[1].instrument 
        
        self.assertEqual(ins.sample_rate, expected_sample_rate)
        
        self.assertEqual(ins.datalogger.response_stages.stages[3].gain, expected_gain)
        
        self.assertEqual(ins.datalogger.response_stages.stages[4].filter.symmetry, 
                         expected_symm_1)
        self.assertEqual(ins.datalogger.response_stages.stages[4].filter.coefficients, 
                         expected_coeff_1)
        self.assertEqual(ins.datalogger.response_stages.stages[5].filter.symmetry, 
                         expected_symm_2)
        self.assertEqual(ins.datalogger.response_stages.stages[5].filter.coefficients, 
                         expected_coeff_2)
        self.assertEqual(ins.datalogger.response_stages.stages[6].filter.symmetry, 
                         expected_symm_2)
        self.assertEqual(ins.datalogger.response_stages.stages[6].filter.coefficients, 
                         expected_coeff_2)
        
        
        
    def _create_test_network(self, network_file):
        """
        Read an information file for a network and return the corresponding dictionary
        
        :param network_file: file name to read and create
        :type network_file: str
        :returns: object of :class:`Network`
        
        """      
        
        network_dir = Path(os.getcwd()).joinpath("obsinfo", "tests", "data", 
                "Information_Files", "network")
        
        network_file = str(network_dir.joinpath(network_file))
                
        info_dict = ObsMetadata.read_info_file(network_file, self.infofiles_path)
        
        return Network(ObsMetadata(info_dict.get('network', None)))
        
    
def run_suite_yaml():
    """
    Create and run test suite for jsonref
    
    """
    
    suite_yaml = unittest.TestSuite()
    suite_yaml.addTests(unittest.makeSuite(JsonRefTest))
     
    result = unittest.TextTestRunner(verbosity=1).run(suite_yaml)
    
    report_result_summary(result)
    
    return suite_yaml
    
def run_suite_info_files():
    """
    Create all test suites for information files
    
    """
    
    print("This program checks all test cases in all of test data and all examples in _examples/Information_Files")
    print("WARNING: The following are not checked and should be checked visually:")
    print("\t* Comments, extras, including Processing")
    print("\t* Attributes of Operator")
    print("\t* Adequacy of seed code")
    print("\t* Sensitivity")
    print("\tOnly 10 locations are provided to test channels, '00' to '09'. Please check that your ")
    print("\texamples and test cases do not exceed this number of locations")
        
    args = retrieve_test_arguments()
    
    def suite(args):
        """
        test suite
        
        :param args: dictionary of command.line options
        :type args: dict of strings
        
        """
              
        suite_info_files = unittest.TestSuite()
        
        if args.all or args.filters:
            suite_info_files.addTest(TestObsinfo('test_all_filters'))
        if args.all or args.stages:
            suite_info_files.addTest(TestObsinfo('test_all_stages'))
        if args.all or args.components:
            suite_info_files.addTest(TestObsinfo('test_all_components'))
        if args.all or args.instrumentations:
            suite_info_files.addTest(TestObsinfo('test_sensor_configurations'))
        if args.all or args.networks:
            suite_info_files.addTest(TestObsinfo('test_all_networks'))
        if args.all or args.configurations:
            suite_info_files.addTest(TestObsinfo('test_sensor_configurations'))
            suite_info_files.addTest(TestObsinfo('test_preamp_configurations'))
            suite_info_files.addTest(TestObsinfo('test_datalogger_configurations'))
            suite_info_files.addTest(TestObsinfo('test_change_modifications'))
         
        return suite_info_files
        
    
    result = unittest.TextTestRunner(verbosity=1).run(suite(args))
      
    report_result_summary(result)
        
    
def report_result_summary(result):
    """
    Report a summary of errors and failures
    
    :param: result - Contains result stats, errors and failures.
    :type result: object returned by unittest TextTestRunner
    
    """
    
    n_errors = len(result.errors)
    n_failures = len(result.failures)

    if n_errors or n_failures:
        print('\n\nSummary: %d errors and %d failures reported\n'%\
            (n_errors, n_failures))
        
def retrieve_test_arguments(): 
    """
    Retrieve arguments from command line for obsinfo-test. Setup several status variables and get information file name
      
    :returns: dictionary object with all status variables and information file name.
    
    """
    
    # Parse the arguments
    parser_args = ArgumentParser(prog="obsinfo-print")
    
    #flags
    
    parser_args.add_argument("-a", "--all", action='store_true', default=False,
                             help="Runs all information file test methods."
                            ) 
    parser_args.add_argument("-f", "--filters", action='store_true', default=False,
                             help="Runs filter information file test methods."
                            ) 
    parser_args.add_argument("-s", "--stages", action='store_true', default=False,
                             help="Runs stage information file test methods."
                            ) 
    parser_args.add_argument("-c", "--components", action='store_true', default=False,
                             help="Runs components information file test methods."
                            ) 
    parser_args.add_argument("-i", "--instrumentations", action='store_true', default=False,
                             help="Runs instrumentation information file test methods."
                            )
    parser_args.add_argument("-n", "--networks", action='store_true', default=False,
                             help="Runs network information file test methods."
                            )
    parser_args.add_argument("-g", "--configurations", action='store_true', default=False,
                             help="Runs configuration test methods for all components."
                            )
    
    args = parser_args.parse_args()
    
    return args        


def print_obs():
    """
    Entry point for obsinfo-print. Print an information file according to its type, 
    and levels below up to the specified level.
    
     Captures all exceptions
    
    """

    args = retrieve_arguments()
    tst = TestObsinfo()
    tst.setUp(test=False, print_output=True, level=args.level) 
    dp = Datapath()
    logger = init_logging()
        
    try:               
        
        type = ObsMetadata.get_information_file_type(args.input_filename)
         
        print(f'Printing {type} file: {args.input_filename}')
            
        if type == "filter":
            tst._test_filter(tst.infofiles_path.build_datapath(args.input_filename))
        elif type == "stage":
            tst._test_stage(tst.infofiles_path.build_datapath(args.input_filename))
        elif type == "datalogger":
            tst._test_datalogger(tst.infofiles_path.build_datapath(args.input_filename))
        elif type == "preamplifier":
            tst._test_preamplifier(tst.infofiles_path.build_datapath(args.input_filename))
        elif type == "sensor":
            tst._test_sensor(tst.infofiles_path.build_datapath(args.input_filename))
        elif type == "instrumentation":
            tst._test_instrumentation(tst.infofiles_path.build_datapath(args.input_filename))
        elif type == "station":
            tst._test_station(tst.infofiles_path.build_datapath(args.input_filename))
        elif type == "network":
            tst._test_network(tst.infofiles_path.build_datapath(args.input_filename))
    
    except TypeError:
        print("Illegal format: fields may be missing or with wrong format in input file, or there is a programming error")
        logger.error("TypeError: Illegal format: fields may be missing or with wrong format in input file, or there is a programming error")
        if args.debug:
            raise
        
        sys.exit(EXIT_DATAERR)
    except (KeyError, IndexError):
        print("Illegal value in dictionary key or list index")
        logger.error("KeyError, IndexError: Illegal value in dictionary key or list index")
        if args.debug:
            raise
        sys.exit(EXIT_SOFTWARE)
    except ValueError:
        print("An illegal value was detected")
        logger.error("ValueError: An illegal value was detected")
        if args.debug:
            raise
        sys.exit(EXIT_DATAERR)
    except FileNotFoundError:
        if args.debug:
            raise
        print("File could not be found")
        logger.error("FileNotFoundError: File could not be found")
        sys.exit(EXIT_NOINPUT)
    except JSONDecodeError:
        print("File and/or subfiles have an illegal format. Probably indentation or missing quotes/parentheses/brackets")
        logger.error("JSONDecodeError: File and/or subfiles have an illegal format. Probably indentation or missing quotes/parentheses/brackets")
        if args.debug:
            raise 
        sys.exit(EXIT_DATAERR)
    except (IOError, OSError, LookupError):
        print("File could not be opened or read")
        logger.error("IOError, OSError, LookupError: File could not be opened or read")
        if args.debug:
            raise
        sys.exit(EXIT_UNAVAILABLE)
    except AttributeError:
        print("Programming error: an object in code had a wrong attribute")
        logger.debug("AttributeError: Programming error: an object in code had a wrong attribute")
        if args.debug:
            raise
        sys.exit(EXIT_SOFTWARE)
    except:
        print("General exception")
        logger.debug("General exception")
        if args.debug:
            raise
        sys.exit(EXIT_FAILURE)
                      
    sys.exit(EXIT_SUCCESS)
    

def retrieve_arguments():
    """
    Retrieve arguments from command line. Setup several status variables and get information file name
      
    :returns: dictionary object with all status variables and information file name.
    
    """
    
    # Parse the arguments
    parser_args = ArgumentParser(prog="obsinfo-print")
    
    #flags
    
    parser_args.add_argument("-l", "--level", nargs="?", default="all",
                             choices=[
                                      'all', 'filter', 'response', 'component', 
                                      'instrumentation', 'channel',
                                      'station', 'network'
                                      ],
                             help="Prints up to LEVEL. 'filter' and 'all' are synonims"
                            ) 
    
    parser_args.add_argument("-d", "--debug",  action='store_true', default=False,
                             help="Print traceback for exceptions"
                            )  
    # positional arguments
    parser_args.add_argument("input_filename", type=str,  nargs=1, 
                             help="Information file to be validated.",
                            )
    
    args = parser_args.parse_args()
     
    if not Path(args.input_filename[0]).is_absolute():
        args.input_filename = str(Path(os.getcwd()).joinpath(args.input_filename[0]).resolve())
             
    return args  


def init_logging():
    """
    Create or open a rotating logging file and add it to ObsinfoConfiguration
    
    :returns: object of Logger class 
    """
    
    logfile = Path.home().joinpath('.obsinfo', 'obsinfolog-validate')
    
    
    logger = logging.getLogger("obsinfo")
    
    logger.setLevel(logging.DEBUG)
    # add a rotating handler with 200K (approx) files and just two files
    handler = RotatingFileHandler(logfile, maxBytes=200000,
                                  backupCount=2)
    frmt = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(frmt)
    logger.addHandler(handler)  
    
    return logger 
   
    