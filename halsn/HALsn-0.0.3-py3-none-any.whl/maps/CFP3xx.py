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

import sys
from src.serialSupervisor import serialSupervisor

class CFP(serialSupervisor):
    def __init__(self, device_path='/dev/FTDI', baud=9600, timeout=0.125, sample_freq=1):

        super().__init__(device_path, baud, timeout, sample_freq)

        self.commands = {
            # Disables Debug Mode
            'debug_off':             '*DS0\r',
            # Enables Debug Mode
            'debug_on':              '*DS1\r',
            # Starts 6oz Classic Brew (K-Cup)
            '6_oz_classic_K':        '*LT1\r',
            # Starts 12oz Classic Brew (K-Cup)
            '12_oz_classic_K':       '*LT4\r',
            # Starts 8oz Classic Brew (Grounds)
            '8_oz_classic':           '*LT13\r',
            # Starts 60oz Brew (Hot Water)
            'full_carafe_hot_water': '*LT31\r',
            # Starts 60oz Classic Brew (Grounds)
            'full_carafe_classic':   '*LT39\r',
            # Starts Auto Purge Cycle
            'auto_purge':            '*LT79\r',
            # Starts Clean Cycle
            'clean_cycle':           '*LT80\r',
            # Cancel Current Brew
            'cancel_brew':           '*LC\r'
        }

        #   | CMD | MST QRY EN | STR IDX | END IDX | HEX CONV EN
        self.queries = {
            # Requests Current Debug State
            'debug_state':           ['?DS\r',  0,  3,  4, 0],
            # Requests Current Brew State
            'current_brew':          ['?LT\r',  1,  3,  4, 0],
            # Request Basket|Size|Style|Ounces|Block|Temp|Volume|Time
            'coffee_recipe_status':  ['?KC\r',  1,  3,  4, 1],
            # Requests PWM Value of Water Pump
            'water_pump_pwm':        ['?KM1\r', 1,  4,  6, 1],
            # Requests PWM Value of Air Pump
            'air_pump_pwm':          ['?KM2\r', 1,  4,  6, 1],
            # Requests Boiler Temp (C)
            'boiler_ntc':            ['?KN1\r', 1,  4,  8, 1],
            # Requests Warm Panel Temp (C)
            'warm_panel_ntc':        ['?KN2\r', 1,  4,  8, 1],
            # Requests Pump Temp (C)
            'pump_ntc':              ['?KN3\r', 1,  4,  8, 1],
            # Requests Alt Cal Temp (C)
            'alt_cal_ntc':           ['?KN4\r', 1,  4,  8, 1],
            # Requests Cal Offset Temp (C)
            'fac_cal_ntc':           ['?KN5\r', 1,  4,  8, 1],
            # Returns Boiler PWM
            'boiler_pwm':            ['?KR1\r', 1,  4,  5, 0],
            # Returns Warm Plate PWM
            'warm_panel_pwm':        ['?KR2\r', 1,  4,  5, 0],
            # Returns State of Drip Switch
            'drip_sw':               ['?SW0\r', 1,  4,  5, 0],
            'SW1':                   ['?SW1\r', 1,  4,  5, 0],
            # Returns state of Coffee Basket Switch
            'coffee_basket_sw':      ['?SW2\r', 1,  4,  5, 0],
            # Returns state of KCup Basket Switch
            'kcup_basket_sw':        ['?SW3\r', 1,  4,  5, 0],
            # Returns state of Water Flow Switch
            'flow_path_sw':          ['?SW4\r', 1,  4,  5, 0],
            # Returns state of Coffee Flow Switch
            'coffee_path_sw':        ['?SW5\r', 1,  4,  5, 0],
            # Requests Software Version on MCU
            'sw_version':            ['?WZ0\r', 0,  4, 19, 0]
        }

        self.testType = ''
        self.lifeTestCommand = ''
        self.errorCommand = 'cancel_brew'

    def _assign_brew_command(self, testType):
        '''
        Private method to assign a life test command as
        class member. Simplifies the testInitialize method
        '''

        self.testType = testType

        if self.testType == 'KCUP':
            self.lifeTestCommand = '12_oz_classic_K'
        elif self.testType == 'GROUNDS':
            self.lifeTestCommand = 'full_carafe_classic'
        elif self.testType == 'WATER':
            self.lifeTestCommand = 'full_carafe_hot_water'
        elif self.testType == 'GROUNDS_TEST':
            self.lifeTestCommand = '8_oz_classic'
        else:
            print(f'{self.testType} is not recognized as a test configuration.\
                    Please correct the entry and try again.')
            sys.exit()

    def _check_switch_states(self):
        '''
        Simple function to check the switch state of self.CFP.
        Reads through returned strings and looks at state index
        to determine if machine configured for the test.

        ::returns:: List
        '''

        switch_states = []
        raw_sw = (self.master_query())[-6:]

        for sw in raw_sw:
            switch_states.append(int(sw[-2]))

        print(f'Product Switch States: {switch_states}\nRefer to the\
                product map to identify switches.')
    
        return switch_states

    def confirm_config(self, testType):
        '''
        Compares self.CFP switch values to predetermined configurations
        to verify the test.

        ::returns:: Bool
        '''

        self._assign_brew_command(testType)

        sw_states = self._check_switch_states()

        if self.testType == 'KCUP' and sw_states[0] == 1 and sw_states[3] == 1:
            return True
        elif self.testType == 'GROUNDS' and sw_states[0] == 1 and sw_states[2] == 1:
            return True
        elif self.testType == 'WATER' and sw_states[0] == 1 and sw_states[4] == 1:
            return True
        elif self.testType == 'GROUNDS_TEST' and sw_states[0] == 1 and sw_states[2] == 1:
            return True
        else:
            print(f'Product is not configured for {self.testType}. Please correct the\
                    configuration and try again.')
            return False

    def return_product_functions(self):
        '''
        Returns all available functions for the CFP.
        Neglects unnecessary commands in the commands
        dictionary.

        ::returns:: Formatted String
        '''

        fnc = ''

        for key in self.commands.keys():
            if self.commands[key][1:3] == 'LT':
                fnc += f'{key}\n'

        return fnc
