

PAD = '' + 75 * '*' + ''
PADL = '' + 75 * '-' + ''
(CRED, CYEL, CBMA, CBRE, CBBL, CWHT, CEND) = (
        '\033[91m', '\u001b[33m', '\u001b[35;1m',
        '\u001b[31;1m', '\u001b[34;1m', '\u001b[37m',
        '\033[0m'
    )


def printExperimentHead(PATH_I, PATH_O, time, title):
    # print(monet.PAD)
    (cred, cwht, cend) = (CRED, CWHT, CEND)
    print(cwht + cwht + '* ['+ str(time) + '] ' + 'MoNeT ' + title + cend)
    # print(monet.PAD)
    print('{}* I: {}{}'.format(cred, PATH_I, cend))
    print('{}* O: {}{}'.format(cred, PATH_O, cend))
    # print(monet.PAD)


def printProgress(i, total, pad=3):
    pStr = '{}* Processing {}/{} {}'
    print(
        pStr.format(CBBL, str(i).zfill(pad), str(total).zfill(pad), CEND),
        end='\r'
    )