

#### parent function code

def assignParents(tokens):
    commonorder = [";", "\. ", "\n",":\n", "\|", "-", ": "]

    order = [(":\n",["\n", "root"]), ("\n", [":\n", "root"]),
    ("\. ", ["\n", ":\n"]), (";", ["\. ", "\n",":\n"]), (": ", ["\n", "\. ", ";"]),
    (",", commonorder), ("-",commonorder), ("\|",commonorder),
    ("(\s|^)and(\s|^)", commonorder), ("(\s|^)or(\s|^)",commonorder),
    ("(\s|^)by(\s|^)", commonorder), ("(\s|^)in(\s|^)",commonorder),
    ("(\s|^)on(\s|^)", commonorder), ("(\s|^)was(\s|^)",commonorder),
    ("(\s|^)is(\s|^)", commonorder), ("(\s|^)but(\s|^)", commonorder)]

    lastKnown = {}
    lastKnownKeys = [ord[0] for ord in order] + ["root", "newLineAny"]
    for key in lastKnownKeys:
        lastKnown[key] = -1

    for i in range(len(tokens)):
        if tokens[i]["tokenType"] != "noise":
            prev = np.amax(np.array(list(lastKnown.values())))
            tokens[i]["parent"] = prev
            continue
        snip = tokens[i]["token"]
        done = False
        for ord in order:
            if re.search(ord[0], tokens[i]["token"].lower()):
                prev = np.amax(np.array(list([lastKnown[r] for r in ord[1]])))
                ## if its a plain new line, determining if it should return to root.
                if "\n" in snip and ":" not in snip:
                    line = getNoiseProfileLine(tokens, i)
                    line2 = getNoiseProfileLine(tokens, lastKnown["newLineAny"])
                    if line.strip() != line2.strip():
                        prev = -1
                if "\n" in snip:
                    lastKnown["newLineAny"] = i
                tokens[i]["parent"] = prev
                lastKnown[ord[0]] = i
                done = True
                break
        if done:
            continue
        prev = np.amax(np.array(list(lastKnown.values())))
        tokens[i]["parent"] = prev
    return tokens


#### parent tests
    def test_parent(self):
        with self.assertRaises(Exception):
            ranges = wildgram("testing", returnNoise=False, includeParent=True)
        ranges = wildgram("testing\n 123", returnNoise=True, includeParent=True)
        self.assertRangesEqual(ranges, 0, "testing", 0, 7, "token", -1)
        self.assertRangesEqual(ranges, 1, "\n ", 7, 9, "noise", -1)
        self.assertRangesEqual(ranges, 2, "123", 9, 12, "numeric", 1)
        ranges = wildgram("testing:\n 123\n 1234", returnNoise=True, includeParent=True)
        self.assertRangesEqual(ranges, 0, "testing", 0, 7, "token", -1)
        self.assertRangesEqual(ranges, 1, ":\n ", 7, 10, "noise", -1)
        self.assertRangesEqual(ranges, 2, "123", 10, 13, "numeric", 1)
        self.assertRangesEqual(ranges, 3, "\n ", 13, 15, "noise", 1)
        self.assertRangesEqual(ranges, 4, "1234", 15, 19, "numeric", 3)
        ranges = wildgram("testing:\n 123\ntesting:\n 1234", returnNoise=True, includeParent=True)
        trueData = [(0, "testing", 0, 7, "token", -1), (1, ":\n ", 7, 10, "noise", -1),
        (2, "123", 10, 13, "numeric", 1), (3, "\n", 13, 14, "noise", -1),
        (4, "testing", 14, 21, "token", 3), (5, ":\n ", 21, 24, "noise", 3),
        (6, "1234", 24, 28, "numeric", 5)]
        for true in trueData:
            self.assertRangesEqual(ranges,true[0], true[1], true[2], true[3], true[4], true[5])
        ranges = wildgram("testing:\n1. dance\n2. dance \n3. revolution", returnNoise=True, includeParent=True)
        trueData = [ (0, "testing", 0, 7, "token", -1) , (1, ":\n", 7, 9, "noise", -1),
        (2, "1", 9, 10, "numeric", 1), (3, ". ", 10, 12, "noise", 1),
        (4, "dance", 12, 17, "token", 3), ( 5, "\n", 17, 18, "noise", 1),
        (6, "2", 18, 19, "numeric", 5), (7, ". ", 19, 21, "noise", 5),
        (8, "dance", 21, 26, "token", 7) , (9, " \n", 26, 28, "noise", 1),
        (10, "3", 28, 29, "numeric", 9), (11, ". ", 29, 31, "noise", 9),
        (12, "revolution", 31, 41, "token", 11)]
        for true in trueData:
            self.assertRangesEqual(ranges,true[0], true[1], true[2], true[3], true[4], true[5])
        ranges = wildgram("testing: super ) as needed for pain")
        trueData = [(0, "testing", 0, 7, "token", -1), (1, ": ", 7, 9, "noise", -1),
        (2, "super", 9, 14, "token", 1), (3, " ) as ", 14, 20, "noise", 1),
        (4, "needed", 20, 26, "token", 1),(5, " for ", 26, 31, "noise", 1),
        (6, "pain", 31, 35, "token", 1) ]
        for true in trueData:
            self.assertRangesEqual(ranges,true[0], true[1], true[2], true[3], true[4], true[5])


def getNoiseProfileLine(tokens, i):
    if i == -1:
        return ""
    line = tokens[i]["token"]
    if line.find(":") != -1:
        line = line[line.find(":")+1:]
    done = False
    for j in range(i+1, len(tokens)):
        if not done and tokens[j]["tokenType"] != "noise":
            line = line + "<TOKEN>"
        if tokens[j]["tokenType"] == "noise":
            if done and "\n" not in tokens[j]["token"]:
                continue
            done = True
            line = line + tokens[j]["token"]
            if "\n" in tokens[j]["token"]:
                return line
    return line
