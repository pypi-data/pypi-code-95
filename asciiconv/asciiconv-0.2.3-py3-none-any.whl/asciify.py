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

letterLikeA = [8448, 8449, 8450, 8451, 8452, 8453, 8454, 8455, 8456, 8457, 8458, 8459, 8460, 8461, 8462, 8463, 8464, 8465, 8466, 8467, 8468, 8469, 8470, 8471, 8472, 8473, 8474, 8475, 8476, 8477, 8478, 8479, 8480, 8481, 8482, 8483, 8484, 8485, 8486, 8487, 8488, 8489, 8490, 8491, 8492, 8493, 8494, 8495, 8496, 8497, 8498, 8499, 8500, 8501, 8502, 8503, 8504, 8505, 8506, 8507, 8508, 8509, 
8510, 8511, 8512, 8513, 8514, 8515, 8516, 8517, 8518, 8519, 8520, 8521, 8522, 8523, 8524, 8525, 8526, 8527]
letterLikeB = ['a/c','a/s','C','*C','CL','c/o','c/u','E','3','*F','g','H','H','H','h','h','I','I','L','l','lb','N','N*','(P)','P','P','Q','R','R','R','Rx','R','SM','TEL','TM','V','Z','oz','ohm','siemens','Z','i','K','A','B','C','e','e','E','F','F','M','o','N','bet','gimel','dalet','i','Q','FAX','pi','gamma','Gamma','Pi','sum','G','L','L','Y','D','d','e','i','j','PL','&','P','A/S','F','000']

original = range(0,128)

def asciify(input):
    output = ''
    for char in input:
        num = ord(char)
        out = num
        if num in original:
            output += char
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
        if num in letterLikeA:
            idx = letterLikeA.index(num)
            output += letterLikeB[idx]
    return output