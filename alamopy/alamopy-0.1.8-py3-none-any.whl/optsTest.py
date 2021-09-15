'''
Necessary testing for all functions from almutils.py
'''

# import functions from testing from almutils
import almopts
import numpy as np

# prepare_default_opts test


def testPrepareDefaultOpts():
    print('Testing prepareDefaultOpts...', end='')
    opts = almopts.prepare_default_opts()

    for key in opts.keys():
        if (key == "keep_alm_file" or key == "keep_lst_file" or key == "print_alm_output"):
            assert(opts[key] == False)
        elif key == "alm_file_name":
            assert(opts[key] == "temp.alm")
        elif key == "entry_names" or key == "section_names":
            pass
        elif key == "return":
            for returnKey in opts["return"]:
                assert(opts["return"][returnKey] == {})
        else:
            assert(opts[key] == None)
    print('Passed.')


# data setup for tests
opts = almopts.prepare_default_opts()
xdata = np.random.rand(100, 3)
xdata[:, 0] *= 10  # Make x1 go from 0 to 10
xdata[:, 1] *= 5   # Make x2 go from 0 to 5
zdata = xdata[:, 0]**2 + xdata[:, 1]**2
inputs = {}
inputs["xdata"] = xdata
inputs["zdata"] = zdata
inputs["noutput"] = 1
inputs["keep_alm_file"] = True
inputs["keep_lst_file"] = True
inputs["print_alm_output"] = True
inputs["monomialpower"] = [2, 3]
inputs["crncustom"] = 1
inputs["zlabels"] = ["z"]
inputs["customcon"] = ["1 -z"]
for key, value in inputs.items():
    opts[key] = value
opts["xdata"] = xdata
opts["zdata"] = zdata
opts["noutputs"] = None
opts["xmin"] = None
opts["xmax"] = None
opts["simulator"] = None

# validate_opts test


def testValidateOpts():
    print('Testing prepareValidateOpts...', end='')
    almopts.validate_opts(opts)

    assert((opts["xdata"] is not None and opts["zdata"] is not None) or (
        opts["simulator"] is not None))
    assert(len(opts["alm_file_name"]) <= 1000)

    almopts.complete_opts(opts)
    print('Passed.')

# complete_opts test


def testCompleteOpts():
    print('Testing prepareDefaultOpts...', end='')
    almopts.validate_opts(opts)
    if opts["xdata"] is not None and opts["zdata"] is not None:
        assert(opts["ninputs"] is not None and opts["noutputs"] is not None)
        assert(opts["ndata"] is not None and opts["data"] is not None)
        assert(opts["xmin"] is not None and opts["xmax"] is not None)
    else:
        assert(opts["ninputs"] is not None)
    print('Passed.')


def testAll():
    testPrepareDefaultOpts()
    testValidateOpts()
    testCompleteOpts()


def main():
    testAll()


if __name__ == '__main__':
    main()
