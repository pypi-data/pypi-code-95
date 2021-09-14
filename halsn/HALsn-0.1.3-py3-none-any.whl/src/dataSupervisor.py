#!/usr/bin/env python3

'''
MIT License

Copyright (c) 2021 Mikhail Hyde & Cole Crescas

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import pandas as pd
import numpy as np
import time
import os
import boto3
from botocore.exceptions import NoCredentialsError

class dataSupervisor():
    def __init__(self, headers, s3_enable=True):
        
        self.s3_enable = s3_enable

        if self.s3_enable:
            self.ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
            self.SECRET_KEY = os.environ['AWS_SECRET_KEY']
            self.bucket = os.environ['BUCKET']

            self.s3 = boto3.client('s3', aws_access_key_id=self.ACCESS_KEY,
                                aws_secret_access_key=self.SECRET_KEY)

        self.HEADERS = headers
       
        self.df = pd.DataFrame()
        
        self.product_map = None

        self.lst = []
        self.clean_list = []
       
        ### UGLY ###
        self.sw_ver =  ''
        self.SKU = ''
        self.build = ''
        self.test_desc = ''
        ### UGLY ###

        self.defaultname = self._gen_filename()
        self.filename = ''
        self.localfile = ''

    def _gen_filename(self):
        '''
        Generates a TimeStamp (string) to be appended
        to CSV file for export

        ::returns:: String
        '''  
        return '%s-%s' % (os.environ['BAY_NO'], time.strftime('%m-%d-%Y_%H%M', time.localtime()))


    def _convertHex(self, value):
        '''
        Converts a HEX number to a Decimal
        value. 

        ::returns:: Int
        '''
        return int(value, 16)


    def _convertBDP(self, data):
        '''
        Univsersal function for converting BDP
        responses into readable data. References
        the query hash map of the device it is
        interpretting.

        ::returns:: List -> converted BDP value(s)
        '''

        if type(data) == int or type(data) == float:
            return [data]
        if type(data) == str:

            for inst in self.product_map.values():
                key = data[1:inst[2]]
                match = inst[0][1:inst[2]]
                if key == 'KC':
                    basket = int(data[3])
                    size   = self._convertHex(data[4])
                    style  = int(data[5])
                    ounces = self._convertHex(data[6:8])
                    block  = self._convertHex(data[8:10])
                    temp   = self._convertHex(data[10:12])
                    volume = self._convertHex(data[12:16])
                    time   = self._convertHex(data[16:18])

                    return [basket, size, style, ounces, block, temp, volume, time]
                
                if key == match:
                    if inst[-1] == 1:
                        return [int(self._convertHex(data[inst[2]:inst[3]]))]
                    else:
                        return [int(data[inst[2]:inst[3]])]
    

    def init_frames(self):
        '''
        Initializes class members for new cycle.
        '''
        self.df = pd.DataFrame()

        self.lst = []
        self.clean_list = []


    def set_product_map(self, prod_map):
        '''
        Called when initialized. Sets the product map
        for conversion functions to reference. 
        '''
        self.product_map = prod_map
    

    def parse(self):
        """
        takes in query command list & parses

        ::returns:: parsed dataframe
        """

        for row in self.lst:

            self.clean_list = []

            for data in row:
                conversion = self._convertBDP(data)
                for idx in conversion:
                    self.clean_list.append(idx)

            self.df = self.df.append(
                pd.DataFrame(((np.asarray(self.clean_list)).reshape(1, -1)), columns=self.HEADERS))

        return self.df.reset_index()


    def report_maker(self, current_run):
        """
        creates report of visualizations & exports to html
        calls in markdown extension of pandas
        :return: report in html form
        """

        self.filename = self.defaultname + ('-Cycle%s.csv' % current_run)
        self.localfile = os.environ['DATA_PATH'] + self.filename

        ### UGLY ###
        self.df['Cycle_ID']         = current_run
        self.df['Test_ID']          = self.test_id
        self.df['File_Name']        = self.filename
        self.df['SKU_Build']        = '%s-%s' % (self.SKU, self.build)
        self.df['Test_Description'] = self.test_desc
        self.df['Software_Version'] = self.sw_ver
        ### UGLY ###
        
    def export_csv(self):
        '''
        Exports the parsed and formatted Dataframe as a CSV
        file to the predetermined directory.
        '''
        self.df.to_csv(self.localfile, index=False)
        print(f'Created Report {self.filename}')
    
    def upload_to_s3(self):
        '''
        Uploads a single file to the AWS s3 bucket.
        '''
        if self.s3_enable:
            try:
                self.s3.upload_file(Filename=self.localfile, Bucket=self.bucket, Key=self.filename)
                print("Upload Successful")
                return True
            except FileNotFoundError:
                print("The file was not found")
                return False
            except NoCredentialsError:
                print("Credentials not available")
                return False
        

if __name__ == '__main__':
    
    pass