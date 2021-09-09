import re

def parseTestString(testStr):
    tests = list()
    lines = testStr.strip().split('\n')
    state_level = "Failed"
    state_step = "" #Others are known 
    for line in lines:
        line_type = getTypeOfTestLine(line)
        if line_type:
            if line_type[0] == "Level":
                state_level = line_type[1]
            elif line_type[0] == "Step":
                state_step = line_type[1]
            elif line_type[0] == "Test":
                tests.append((line_type[1], state_step, state_level, line_type[2]))
    return tests

def getTypeOfTestLine(line):
    line = line.strip()
    match = re.match(r'Tests: (\w+)', line)
    if match:
        return ("Level", match.group(1))
    match = re.match(r'Step \((.+)\)', line)
    if match:
        return ("Step", match.group(1))
    match = re.match(r'\d+\. (.+) \((.+)\)', line)
    if match:
        return ("Test", match.group(1), match.group(2))
    return None
