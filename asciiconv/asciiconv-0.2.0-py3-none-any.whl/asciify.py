# Uppercase

bSerifU = range(119808, 119833)
iSerifU = range(119860, 119885)
biSerifU = range(119912, 119937)
sansSerifU = range(120224, 120249)
bSansSerifU = range(120276, 120301)
iSansSerifU = range(120328, 120353)
biSansSerifU = range(120380, 120405)
scriptU = range(119964, 119989)
bScriptU = range(120016, 120041)
frakturU = range(120068, 120093)
bFrakturU = range(120172, 120197)
monospaceU = range(120432, 120457)
bMonospaceU = range(120120, 120145)

# Lowercase

bSerifL = range(119834, 119859)
iSerifL = range(119886, 119911)
biSerifL = range(119938, 119963)
sansSerifL = range(120250, 120275)
bSansSerifL = range(120302, 120327)
iSansSerifL = range(120354, 120379)
biSansSerifL = range(120406, 120431)
scriptL = range(119990, 120015)
bScriptL = range(120042, 120067)
frakturL = range(120094, 120119)
bFrakturL = range(120198, 120223)
monospaceL = range(120458, 120483)
bMonospaceL = range(120146, 120171)

unicodeUpper = [
    bSerifU,
    iSerifU,
    biSerifU,
    sansSerifU,
    bSansSerifU,
    iSansSerifU,
    biSansSerifU,
    scriptU,
    bScriptU,
    frakturU,
    bFrakturU,
    monospaceU,
    bMonospaceU
]

unicodeLower = [
    bSerifL,
    iSerifL,
    biSerifL,
    sansSerifL,
    bSansSerifL,
    iSansSerifL,
    biSansSerifL,
    scriptL,
    bScriptL,
    frakturL,
    bFrakturL,
    monospaceL,
    bMonospaceL
]

spaces = [8239, 8287, 12288, 5760, 160]
spaces += range(8192, 8203)

def asciify(input):
    print(spaces)
    output = ''
    for char in input:
        num = ord(char)
        out = num
        for group in unicodeUpper:
            if num in group:
                out -= group[0]
                output += chr(out + 65)
        for group in unicodeLower:
            if num in group:
                out -= group[0]
                output += chr(out + 97)
        if num in spaces:
            output += ' '
    return output