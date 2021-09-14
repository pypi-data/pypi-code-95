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

import subprocess
import os

def return_string(arg):
    '''
    Converts subprocess return as string
    '''
    return arg.decode('utf-8')

def split_return(arg):
    '''
    Converts subprocess return to list
    '''
    return arg.split('\n')

def find_matches(comparitors, arg):
    '''
    Compares list of match IDs to entries
    in a list and returns entries that match
    '''

    matches = []

    for i in arg:

        if len(matches) >= 3:
                break

        for j in comparitors:

            if j in i:
                matches.append(i.strip())

    return matches

def build_command(vendor, product, alias):
    '''
    Takes Linux command and user inputs and converts
    them to list form
    '''
    return 'SUBSYSTEM=="tty", %s, %s,, SYMLINK+="%s"' % (vendor, product, alias)

if __name__ == '__main__':

    IDs = ['ATTRS{idVendor}', 'ATTRS{idProduct}']
    variables = {
    'BAY_NO':    ['', 'BAY_1', 0],
    'DATA_PATH': ['', '/home/pi/CLT_DATA/', 1],
    'LOG_PATH':  ['', '/home/pi/CLT_LOGS/', 1],
    }

    file = '/etc/udev/rules.d/99-usb-serial.rules'
    os.system('sudo touch %s' % file)


    ARDO_info = split_return(return_string\
        (subprocess.check_output(['udevadm', 'info', '-a', '-n',
            input('Enter Arduino Path: ')])))
    ard_match = find_matches(IDs, ARDO_info)
    ard_line = build_command(ard_match[0], ard_match[1], 'Arduino')

    FTDI_info = split_return(return_string\
        (subprocess.check_output(['udevadm', 'info', '-a', '-n',
            input('Enter FTDI Path: ')])))
    ftdi_match = find_matches(IDs, FTDI_info)
    ftdi_line = build_command(ftdi_match[0], ftdi_match[1], 'FTDI')

    SCLE_info = split_return(return_string\
        (subprocess.check_output(['udevadm', 'info', '-a', '-n',
            input('Enter Scale Path: ')])))
    scle_match = find_matches(IDs, SCLE_info)
    scle_line = build_command(scle_match[0], scle_match[1], 'Scale')

    for var in variables.keys():
        if variables[var][0] == '':
            print(f'Ex. {variables[var][1]}')
            val = input(f'Enter value for {var}: ')
            variables[var][0] = val
        if variables[var][-1] == 1:
            os.system('mkdir %s' % variables[var][0])

    print('''
AUTO GENERATED INSTRUCTIONS:

    Open a new terminal and complete the following instructions:

        1. Copy and paste the following command:


            sudo nano %s


        2. Copy the following text and paste it in the file:


            %s
            %s
            %s

        
        3. Retrieve the AWS credentials and environment variables and paste them in
            the same format as the previous step.

        4. Press Ctrl+x, y, [Enter] to save the changes.

        5. Enter the following commands into the terminal:


            sudo udevadm control --reload
            sudo service udev restart


READ BEFORE STEP 6:

After rebooting you need to check the /dev/ folder for new device names. You should see

/dev/Arduino
/dev/FTDI

somewhere in the list. You should try using pyserial to communicate with the devices to confirm
that they were setup correctly. If there is any confusion or any issues contact the software manager.
They will correct the configuration.


        7. Reboot the Pi.


THANK YOU!!!!

    ''' % (file, ard_line, ftdi_line, scle_line))
        
    print(
'''
The following instructions will aid the user in setting the environment variables
for the operating system to run the CLTF software. The output commands will be put
in the profile of the user pi. This profile is loaded each time at login so the
variables will be automatically set for the software to start running.


1. Open a separate terminal and enter the following command:

    
    sudo nano /home/pi/.profile


2. Scroll to the bottom by pressing Ctrl+v serveral time.

3. Copy and paste the following output into the bottom of the file:

'''
)            
    for key in variables.keys():
        print(f'export {key}={variables[key][0]}')
            
    print('\n\n')
    print(
'''

4. Get the AWS Credentials from the system admin and add them to ~/.profile in
    the format provided.

5. Press Ctrl+x -> y -> [Enter] to save the changes.

6. Finally, enter the last command to implement the environment variables.


    source ~/.profile
'''
)
