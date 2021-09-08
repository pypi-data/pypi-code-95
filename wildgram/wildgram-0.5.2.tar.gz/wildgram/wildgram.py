import regex as re
import string
import os
import numpy as np
from copy import deepcopy

STOPWORDS = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
"you(\'?)re", "you(\'?)ve", "you(\'?)ll", "you(\'?)d", 'your', 'yours', 'yourself', 'yourselves',
'he', 'him', 'his', 'himself', 'she', "she(\'?)s", 'her', 'hers', 'herself', 'it',
"it(\'?)s", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',
'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
'some', 'such', 'only', 'own', 'same', 'so', 'than', 'too', 'very','can', 'just',
'should', "should(\'?)ve", 'now']

TOPICWORDS = [{"token": "no", "tokenType": "negation"},{"token": "negative", "tokenType": "negation"},
{"token": "not", "tokenType": "negation"},{"token": "nor", "tokenType": "negation"}, {"token": "non-*", "suffix": "[A-Za-z]+", "tokenType": "negation"}, "([A-Za-z]+-)+\w+",
{"token": "ain(\'?)t", "tokenType": "negation"},{"token": "aren(\'?)t", "tokenType": "negation"},
{"token": "couldn(\'?)t", "tokenType": "negation"},{"token": "didn(\'?)t", "tokenType": "negation"},
{"token": "doesn(\'?)t", "tokenType": "negation"},{"token": "hadn(\'?)t", "tokenType": "negation"},
{"token": "hasn(\'?)t", "tokenType": "negation"},{"token": "haven(\'?)t", "tokenType": "negation"},
{"token": "isn(\'?)t", "tokenType": "negation"},{"token": "mightn(\'?)t", "tokenType": "negation"},
{"token": "mustn(\'?)t", "tokenType": "negation"},{"token": "needn(\'?)t", "tokenType": "negation"},
{"token": "shan(\'?)t", "tokenType": "negation"},{"token": "shouldn(\'?)t", "tokenType": "negation"},
{"token": "wasn(\'?)t", "tokenType": "negation"},{"token": "weren(\'?)t", "tokenType": "negation"},
{"token": "won(\'?)t", "tokenType": "negation"},{"token": "don(\'?)t", "tokenType": "negation"},
{"token": "wouldn(\'?)t", "tokenType": "negation"},{"token": "denies", "tokenType": "negation"},
{"token": "denied", "tokenType": "negation"},{"token": "\d+\.\d+", "tokenType": "numeric", "suffix": "[^\s\d-]+"},
{"token": "\d+", "tokenType": "numeric","suffix": "[^\s\d-]+"},"([A-Za-z](\.)?){1,2}[A-Za-z]",
{"token": "\d+\.\d+", "tokenType": "numeric"},{"token": "\d+", "tokenType": "numeric"},
{"token": "one", "tokenType": "numeric"},{"token": "two", "tokenType": "numeric"},
{"token": "three", "tokenType": "numeric"},{"token": "four", "tokenType": "numeric"},
{"token": "will", "tokenType": "future"}, "reveal", "revealed"]

JOINERWORDS = ["of", "in", "to", "on","than","at"]

'''{"token": "\d{,2}[-/]\d{,2}[-/]\d{4}", "tokenType":"date*%m-%d-%Y|%m/%d/%Y|%d-%m-%Y|%d/%m/%Y"},
{"token": "\d{1,2}[-/]\d{1,2}[-/]\d{2}", "tokenType":"date*%m-%d-%y|%m/%d/%y|%d-%m-%y|%d/%m/%y"},
{"token": "\d{1,2}[-/](\d{2}|\d{4})", "tokenType":"date*%m-%d|%m-%Y|%m-%y|%d-%m"},
{"token": "(january|february|march|april|june|july|august|september|october|november|december)\s+\d{,2}(,|\s)+\d{2,4}", "tokenType":"date*%M %d %Y|%M %d, %Y|%M %d %y|%M %d, %y"},
{"token": "(jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\s+\d{,2}(,|\s)+\d{2,4}", "tokenType":"date*%b %d %Y|%b %d, %Y|%b %d %y|%b %d, %y"},
'''


def pullOutJoiners(merged, text, joinerwords):
    if len(joinerwords) == 0:
        return []
    ret = []
    joiners = "|".join(["(\s|^)"+stop+"(\s|$)" for stop in joinerwords])
    for i in range(len(merged)):
        match = merged[i]
        start = 0
        end = len(text)
        if not re.search("("+joiners+")", text[match[0]:match[1]]):
            continue
        if i > 0:
            start = merged[i-1][0]
        if i < len(merged)-1:
            end = merged[i+1][1]
        if start != merged[i][0] and end != merged[i][1]:
            ret.append((start,end, 'token'))
    return ret

def pullOutNoise(pattern, text, leftovers):
    matches = [(match.start(), match.end(), "noise") for match in pattern.finditer(text.lower(),overlapped=True)]
    matches = sorted(matches, key=lambda x: (x[0], x[1]))
    prev = 0
    noise = []
    for i in range(len(matches)-1):
        if matches[i][1] < matches[i+1][0]:
            leftovers, noise = checkAndRemoveLeftovers(leftovers,matches[prev][0],matches[i][1],noise,"noise" )
            prev = i+1
    if prev < len(matches):
        leftovers, noise = checkAndRemoveLeftovers(leftovers,matches[prev][0],matches[-1][1],noise,"noise" )
    return noise, leftovers

def pullOutTokens(indexes, type="token"):
    indexes = list(indexes)
    if len(indexes) == 0:
        return []
    indexes = sorted(indexes)
    prev = indexes[0]
    ret = []
    for i in range(len(indexes)-1):
        if indexes[i]+1 != indexes[i+1]:
            ret.append((prev,indexes[i]+1,type))
            prev = indexes[i+1]
    ret.append((prev, indexes[-1]+1,type))

    return ret

def pullOutTopics(topics, text, leftovers, noise):
    ret = []
    punc = [x for x in string.punctuation]
    allindexes = set()
    potentialphrases = []
    for topic in topics:
        token = topic
        tokenType = "token"
        suffix = ""
        suffixType = "token"
        if isinstance(topic, dict):
            token = topic["token"]
            tokenType = topic["tokenType"]
            if "suffix" in topic:
                suffix = topic["suffix"]

        ## find all relevant matches
        for match in re.finditer("(\s|"+"|\\".join(punc)+"|^)"+token+suffix+"(\s|"+"|\\".join(punc)+"\s|$)", text.lower(),overlapped=True):
            topicmatches = re.finditer(token, text[match.start():match.end()].lower())
            allindexes = allindexes.union(range(match.start(), match.end()))

            for top in topicmatches:
                potentialphrases.append((match.start()+ top.start(),match.start()+ top.end(), tokenType))
                if suffix == "":
                    continue
                suffixes = re.finditer(suffix, text[match.start()+top.end():match.end()].lower())

                for suff in suffixes:
                    if suff.start() == suff.end():
                        continue
                    potentialphrases.append((match.start()+ top.end()+suff.start(),match.start()+ top.end()+suff.end(), "token"))
    for potential in potentialphrases:
        leftovers, ret = checkAndRemoveLeftovers(leftovers, potential[0], potential[1], ret, potential[2])
    ## what's left is noise
    allindexes = leftovers.intersection(allindexes)
    noise = pullOutTokens(allindexes, "noise") + noise
    leftovers = leftovers.difference(allindexes)

    return ret, leftovers,noise

def isInLeftovers(leftovers, r):
    return len(leftovers.intersection(set(r))) == len(r)

def checkAndRemoveLeftovers(leftovers, start, end, ret, tokenType):
    r = range(start, end)
    if not isInLeftovers(leftovers, r):
        return leftovers, ret
    ret.append((start, end, tokenType))
    leftovers = leftovers.difference(r)
    return leftovers, ret


def figureOutRegex(stopwords, size=2):
    punc = [x for x in string.punctuation]
    regex = '[\s' + "|\\".join(punc)+ ']{'+ str(size)+',}|\n|[\s' + "|\\".join(punc)+ ']+$'
    stops = "|".join(["(\s|^)"+stop+"(\s|$)" for stop in stopwords])
    if len(stops) != 0:
        regex = stops+'|'+regex
    prog = re.compile("("+regex+")")
    return prog

def filterAndSort(matches, returnNoise):
    ret = {}
    for match in matches:
        if match[0] not in ret:
            ret[match[0]] = {}
        if match[1] not in ret[match[0]]:
            ret[match[0]][match[1]] = match[2]
            continue
        curState = ret[match[0]][match[1]]
        ## this allows non tokens to override tokens if they are duplicates
        if match[2] == "token" and curState != "token":
            continue
        ret[match[0]][match[1]] = match[2]
    res = []
    for key in ret:
        for k in ret[key]:
            if not returnNoise and ret[key][k] == "noise":
                continue
            res.append((key, k, ret[key][k]))

    return sorted(res,key=lambda x: (x[0], x[1]) )

def createRangesFromProg(prog, topics, text, joinerwords,ranges=[],leftover=[]):
    newnoise, leftover = pullOutNoise(prog, text, leftover)
    topics, leftover, newnoise = pullOutTopics(topics, text, leftover, newnoise)
    tokens = pullOutTokens(leftover)
    merged = sorted(tokens + topics + newnoise, key=lambda x: (x[0], x[1]))
    ranges = ranges + pullOutJoiners(merged, text, joinerwords) + tokens + topics + newnoise
    return ranges, leftover

def createToken(start, end, type, text, index):
    return {"startIndex": start, "endIndex":end, "token":text[start:end], "tokenType": type, "index": index}

def wildgram(text, stopwords=STOPWORDS, topicwords=TOPICWORDS, include1gram=True, joinerwords=JOINERWORDS, returnNoise=True, includeParent=False):
    # corner case for inappropriate input
    if not isinstance(text, str):
        raise Exception("What you just gave wildgram isn't a string, mate.")
    if not returnNoise and includeParent:
        raise Exception("Parent is based on noise index, you need to set returnNoise to True in order to have includeParent be True. Otherwise set both to False.")

    prog = figureOutRegex(stopwords)
    ranges = []
    leftover = set(range(len(text))) # what characters haven't been marked previously
    ranges, leftover = createRangesFromProg(prog, topicwords, text, joinerwords,ranges, leftover)
    if include1gram:
        prog1gram = figureOutRegex(stopwords, 1)
        ranges, leftover = createRangesFromProg(prog1gram, [], text, joinerwords,ranges, leftover)

    ranges =filterAndSort(ranges, returnNoise)
    ret = []
    for r in ranges:
        app = createToken(r[0], r[1], r[2], text,len(ret))
        ret.append(app)

    return ret
def constructAssignment(token, assignment):
    if isinstance(assignment, str):
        return assignment
    value = token[assignment["spanType"]]
    if "asType" not in assignment:
        return value
    if assignment["asType"] == "float":
        return float(value)
    if assignment["asType"] == "int":
        return int(value)
    return value

# rules in the form [{"topic": topic, "spans":  [span(s)], "spanType": x (eg. tokenType, token, etc.)}]
class WildRules:
    def __init__(self, rules):
        self.rules = rules
        self.spans = {}
        for i in range(len(rules)):
            rule = rules[i]
            if rule["spanType"] not in self.spans:
                self.spans[rule["spanType"]] = {}
            for span in rule["spans"]:
                if span not in self.spans[rule["spanType"]]:
                    self.spans[rule["spanType"]][span] =[]
                self.spans[rule["spanType"]][span].append(i)

    def apply(self, span):
        tokens = wildgram(span, includeParent = False)
        if len(tokens) == 0:
            return []
        applied = {}
        for i in range(len(tokens)):
            tokens[i]["unit"] = "unknown"
            tokens[i]["value"] = "unknown"
            for spanType in self.spans:
                if replaceMeaninglessPunc(tokens[i][spanType]) in self.spans[spanType]:
                    for ruleApplied in self.spans[spanType][replaceMeaninglessPunc(tokens[i][spanType])]:
                        if ruleApplied not in applied:
                            applied[ruleApplied] = []
                        applied[ruleApplied].append(i)

        for i in sorted(list(applied.keys())):
            rule = self.rules[i]
            for j in applied[i]:
                if "nearby" not in rule:
                    tokens[j]["unit"] =  constructAssignment(tokens[j], rule["unit"])
                    tokens[j]["value"] =  constructAssignment(tokens[j], rule["value"])
                    continue
                for nearby in rule["nearby"]:
                    start = j - 10
                    end = j + 10
                    if "startOffset" in nearby:
                        start = j + nearby["startOffset"]
                    if "endOffset" in nearby:
                        end = j + nearby["endOffset"]
                    for k in range(start, end):
                        if k < 0:
                            continue
                        if k >= len(tokens):
                            continue
                        if replaceMeaninglessPunc(tokens[k][nearby["spanType"]]) in nearby["spans"]:
                            tokens[j]["unit"] =  constructAssignment(tokens[j], rule["unit"])
                            tokens[j]["value"] = constructAssignment(tokens[j], rule["value"])
        newtoks = []
        prevUnit = tokens[0]["unit"]
        prevValue = tokens[0]["value"]
        prevToks = [tokens[0]]
        for i in range(1,len(tokens)):
            if len(prevToks) > 0 and tokens[i]["startIndex"] < prevToks[-1]["endIndex"]:
                continue
            if tokens[i]["tokenType"] == "noise" and tokens[i]["unit"] == "unknown" and len(tokens[i]["token"]) >= 2:
                newtoks, prevUnit,prevValue, prevToks = resetNewToks(newtoks, prevUnit,prevValue, prevToks, span)
                continue
            if tokens[i]["tokenType"] == "noise" and tokens[i]["unit"] == "unknown":
                prevToks.append(tokens[i])
                continue
            if prevUnit != tokens[i]["unit"] or prevValue != tokens[i]["value"]:
                newtoks, prevUnit, prevValue, prevToks = resetNewToks(newtoks, prevUnit,prevValue, prevToks, span)
            prevUnit = tokens[i]["unit"]
            prevValue = tokens[i]["value"]
            prevToks.append(tokens[i])

        newtoks,prevUnit,prevValue, prevToks = resetNewToks(newtoks, prevUnit, prevValue, prevToks, span)
        return newtoks

def resetNewToks(newtoks, prevUnit,prevValue, prevToks, span):
    if len(prevToks) == 0:
        return newtoks, "", "", []
    if prevToks[-1]["tokenType"] == "noise" and prevToks[-1]["unit"] == "unknown":
        return resetNewToks(newtoks, prevUnit, prevValue, prevToks[:-1], span)
    snippet = replaceMeaninglessPunc(span[prevToks[0]["startIndex"]:prevToks[-1]["endIndex"]])
    newtoks.append({"unit": prevUnit, "value": prevValue, "token": snippet, "startIndex":prevToks[0]["startIndex"] ,"endIndex":prevToks[-1]["endIndex"]})
    return newtoks, "","", []

def replaceMeaninglessPunc(token):
    return token.replace("(", " ").replace(")", " ").replace(",", " ").strip()

def doesLeafApply(leaf, tokens, i):
    if leaf["unit"] == tokens[i]["unit"]:
        return True
    return False

def checkSharableIntraForm(leaf):
    if len(leaf["children"]) == 0:
        return False
    for child in leaf["children"]:
        if child["unit"] == "EHR" and child["value"] == "META-FORM":
            for ch in child["children"]:
                if ch["unit"] == "EHR" and ch["value"] == "INTRA-FORM-SHARABLE":
                    return True
    return False

def removePartial(filled, partial, key, i, lastI):
    filled.append((key, deepcopy(partial[key])))
    for leafKey in list(partial[key].keys()):
        ## delete any key if past grouping threshold
        if i - lastI >= 3:
            del partial[key][leafKey]
            continue
        if not partial[key][leafKey]["leafKeys"][leafKey]["sharableIntraForm"]:
            del partial[key][leafKey]
    return filled

## class WildForm takes output from wildrules and converts into a form
class WildForm:
    ## forms in the form {unit: b, value: b, displayName: c, children: [...]}
    ## meta information about validation using unit:EHR ...
    def __init__(self):
        self.forms = []
        self.leafToLeafKey = {}
        self.leaves = []
        self.formToLeafKey = {}
    def add_form(self, form):
        self.forms.append(form)
        formKey = str(len(self.forms)-1)
        self.formToLeafKey[formKey] = []
        self.add_leaf(form, formKey)
    def add_leaf(self, node, leafKey):
        if node["value"] == "":
            ind = -1
            if node in self.leaves:
                ind = self.leaves.index(node)

            if node not in self.leaves:
                self.leaves.append(node)
                ind = len(self.leaves) -1
                self.leafToLeafKey[ind] = []
            self.leafToLeafKey[ind].append(leafKey)
            self.formToLeafKey[leafKey.split("-")[0]].append(leafKey)
        for i in range(len(node["children"])):
            newKey = leafKey +"-" + str(i)
            self.add_leaf(node["children"][i], newKey)

    def apply(self, tokens):
        for i in range(len(tokens)):
            tokens[i]["leafKeys"] = []
            for j in range(len(self.leaves)):
                if doesLeafApply(self.leaves[j], tokens, i):
                    tokens[i]["leafKeys"] = {}
                    for key in self.leafToLeafKey[j]:
                        tokens[i]["leafKeys"][key] = {}
                        tokens[i]["leafKeys"][key]["sharableIntraForm"] = checkSharableIntraForm(self.leaves[j])

        ## filling it in, first to last ...
        lastIndex = {}
        partial = {}
        filled = []
        for i in range(len(tokens)):
            for key in tokens[i]["leafKeys"]:
                ## if we haven't started a new form...
                formKey = key.split("-")[0]
                ## reset form if past threshold...
                if formKey not in partial:
                    partial[formKey] = {}
                    lastIndex[formKey] = i
                 ## split off a partial if there is already an existing answer, and continue...
                if key in partial[formKey]:
                    filled = removePartial(filled, partial, formKey, i, lastIndex[formKey])
                    lastIndex[formKey] = i
                ## split off a partial if new answer is past distance threshold
                if i - lastIndex[formKey] >= 3:
                    filled = removePartial(filled, partial, formKey,  i, lastIndex[formKey])
                    lastIndex[formKey] = i
                partial[formKey][key] = tokens[i]
                lastIndex[formKey] = i

        for key in partial:
            filled = removePartial(filled, partial, key, 0, 0)
        for i in range(len(filled)):
            filled[i] = self.fillInForm(filled[i])
        return filled

    def fillInForm(self, filledLeaves):
        formKey = filledLeaves[0]
        leaves = filledLeaves[1]
        form = deepcopy(self.forms[int(formKey)])
        for leafKey in leaves:
            node = form
            keys = leafKey.split("-")[1:]
            for key in keys:
                node = node["children"][int(key)]
            node["unit"] = leaves[leafKey]["unit"]
            node["value"] = leaves[leafKey]["value"]
            node["startIndex"] = leaves[leafKey]["startIndex"]
            node["endIndex"] = leaves[leafKey]["endIndex"]
            node["token"] = leaves[leafKey]["token"]
        return form
