import os
import runmonitor.stat_tools as srd


def check_railing(rd=None,bound_width=0.05, threshold=0.03, parameter="mc"):

    try:
        ##############Open Posterior Sample File (Latest One)#################
        if rd == None: # a simple way to either take an input rundir, and if none is given use cwd
            rd = os.getcwd()

        files = os.listdir()

        samples_scan = srd.scan_samples(rd) # see stat_tools/scan_samples() for how this works, it gives a lot of information about a run directory
        itn = samples_scan[4]

        handler = open(samples_scan[0])

        # Map each column of data from posterior file to the parameter it represents
        # At the same time, skips header line when pulling actual data
        param_to_column = {}
        for (i,p) in enumerate(handler.readline().split()[1:]):
            param_to_column[p] = i

        posterior_lines = handler.readlines()
        handler.close()
        #########################################################

        # Get the current param range from the CIP file
        parameter_range = get_cip(parameter,rd=rd)

        # Pull values of Parameter from Posterior
        param_values = []
        for line in posterior_lines:
            param_values.append(float(line.split()[param_to_column[parameter]]))
        param_values.sort()

        # Find what range on the edges of the Posterior to check for Railing
        cut_off = bound_width * (parameter_range[1] - parameter_range[0])

        # Count how many points lie within the cutoff from each bound

        number_of_values_above_cut_off = 0
        for value in param_values[::-1]:
            if value >= parameter_range[1] - cut_off:
                number_of_values_above_cut_off += 1
            else:
                break

        number_of_values_below_cut_off = 0
        for value in param_values:
            if value <= parameter_range[0] + cut_off:
                number_of_values_below_cut_off += 1
            else:
                break

        # use numbers to identify railing:
        #    return > 1, right railing
        #    return % 2 = 1, left railing

        # Find what percent of values lie within a cutoff of each bound and compare to allowable threshold
        # Run modify function if railing is detected, if not returns 0

        _, right_val = get_cip(parameter,rd=rd)
        if parameter == 'eta' and right_val > 0.249999:
            return 0 

        if number_of_values_above_cut_off / len(param_values) > threshold and number_of_values_below_cut_off / len(
                param_values) > threshold:
            modify_prior(3, param=parameter,rd=rd)  # 3 = railing on both sides
            return 3

        elif number_of_values_above_cut_off / len(param_values) > threshold:
            modify_prior(2, param=parameter,rd=rd)  # 2 = right railing
            return 2

        elif number_of_values_below_cut_off / len(param_values) > threshold:
            modify_prior(1, param=parameter,rd=rd)  # 1 = left railing
            return 1

        else:
            return 0  # 0 = no railing
    
    except:
        print("Could not check railing - make sure the posterior file has contents!!")
        return 0


def modify_prior(rail_code, rd=None, param='mc', adj_list=[0.5, 1.5]):

    # Modifies prior accordingly. Only implemented for cip.
    # Parameters:
    #   param - the parameter to adjust
    #   rail_code - the kind of railing to explore (see above)
    #   adj_list - the amount to adjust the bounds by. Index 0 is left, index 1 is right. If no change needed, index ignored
    #   rd = the run directory, if none default to cwd

    left_val, right_val = get_cip(param,rd=rd)
    if (rail_code % 2 == 1):  # left railing
        left_val *= adj_list[0]
    if (rail_code > 1):  # right railing
        right_val *=  adj_list[1]
        if param == 'eta' and right_val >= 0.25:
            right_val = 0.24999999



    ######## Edit Files #############

    # Edit Cip
    if rd == None:
        rd = os.getcwd()

    files = os.listdir(rd)

    for file in files:
        if "CIP_" in file:
            handler = open(os.path.join(rd,file))
            file_contents = handler.read()
            handler.close()

            # Split file into before param range and after, with middle being the new range to insert between
            first_half = file_contents[:file_contents.find("[", file_contents.find(param + """-range""")) + 1]
            second_half = file_contents[file_contents.find("]", file_contents.find(param + """-range""")):]
            middle = str(left_val) + ", " + str(right_val)

            # Combine each piece back together and write back
            handler = open(os.path.join(rd,file), "w")
            handler.write(first_half+middle+second_half)
            handler.close()


    #Edit PUFF file

    handler = open(os.path.join(rd,"PUFF.sub"))
    puff_contents = handler.read()
    handler.close()

    first_half = puff_contents[:puff_contents.find("[", puff_contents.find("--downselect-parameter " + param + " --downselect-parameter-range")) + 1]
    second_half = puff_contents[puff_contents.find("]", puff_contents.find("--downselect-parameter " + param + " --downselect-parameter-range")):]

    if not puff_contents.find("[", puff_contents.find("--downselect-parameter " + param + " --downselect-parameter-range")) == -1:
        handler = open(os.path.join(rd,"PUFF.sub"), "w")
        handler.write(first_half + middle + second_half)
        handler.close()



def get_cip(parameter,rd=None):
    # helper method to get cip contents
    ##############Open CIP File#################
    if rd == None:
        rd = os.getcwd()
    handler = open(os.path.join(rd,"CIP_0.sub"))
    CIP_file = handler.read()
    handler.close()
    ##############################################

    # Check CIP File for Range of Parameter in Prior

    range_string = CIP_file[CIP_file.find("[", CIP_file.find(parameter + """-range""")) + 1:
                            CIP_file.find("]", CIP_file.find(parameter + """-range"""))]

    # Tuple where first element is lower bound and second is upper bound
    parameter_range = float(range_string.split(",")[0]), float(range_string.split(",")[1])

    return parameter_range
