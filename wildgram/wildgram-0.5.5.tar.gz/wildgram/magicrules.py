from wildgram import wildgram
import connect_umls as um
import itertools
import numpy as np
import json


def getSubset(tokens, i, startOffset, endOffset):
    start = i+startOffset
    end = i+endOffset
    if start < 0:
        start = 0
    if end > len(tokens):
        end = len(tokens)
    subset = tokens[start:i]
    if i != len(tokens)-1:
        subset = subset + tokens[i+1:end]
    return subset

def findMatching(token, predictions):
    found = []
    for pred in predictions:
        if token["startIndex"] < pred["startIndex"]:
            continue
        if token["endIndex"] > pred["endIndex"]:
            continue
        found.append(convertCodeDictToString(pred))
    return found

def convertCodeDictToString(code):
    ret = code["unit"]+"|||"+code["value"]
    if "children" not in code or len(code["children"]) == 0:
        return ret
    children = []
    for cod in code["children"]:
        children.append(convertCodeDictToString(cod))
    ret = ret + "[" + "||".join(sorted(children)) +"]"
    return ret

def getAllNodes(code):
    ret = [code["unit"]+"|||"+code["value"]]
    if "children" not in code or len(code["children"]) == 0:
        return ret
    for cod in code["children"]:
        ret = ret + getAllNodes(cod)
    return ret

class MagicRules:
    def __init__(self):
        self.W = {}
        self.Triggers = {}
        self.Codes = {}

    def add_umls_cui(self, cui_code, apikey):
        umls = um.UMLS(apikey)
        cui = um.CUI(apikey, cui_code, "")
        triggers = cui.synonyms()
        for trigger in triggers:
            self.add_trigger(trigger, {"unit": "UMLS", "value":cui_code, "children": []})

    def add_trigger(self, trigger, codeDict, givens=[]):
        code =convertCodeDictToString(codeDict)
        self.Codes[code] = codeDict
        tokens = [tok["token"] for tok in wildgram(trigger, returnNoise=False)]
        given_tokens = []
        for given in givens:
            given_tokens = given_tokens + [giv["token"] for giv in wildgram(given, returnNoise=False)]
        tokenMod = 5
        ## this ensures that there must be the nearby spans to trigger
        if len(givens) > 0 or len(tokens) > 1:
            tokenMod = 3
        givenMod = 5
        if len(given_tokens) > 0:
            givenMod = 5/(len(given_tokens) + len(tokens)-1)

        for tok in tokens:
            self.W[tok] = 5
            if tok not in self.Triggers:
                self.Triggers[tok] = {}
            if code not in self.Triggers[tok]:
                self.Triggers[tok][code] = {}
            self.Triggers[tok][code][tok] = tokenMod
            for given in given_tokens:
                self.Triggers[tok][code][given] = givenMod

        combos = itertools.combinations(tokens, 2)
        for combo in combos:
            self.Triggers[combo[0]][code][combo[1]] = givenMod
            self.Triggers[combo[1]][code][combo[0]] = givenMod

    def predict(self, text):
        tokens = wildgram(text, returnNoise=False)
        assignments = {}
        for i in range(len(tokens)):
            snippet = tokens[i]["token"]
            if snippet not in self.Triggers:
                continue
            subset = list(set([tok["token"] for tok in getSubset(tokens, i, -10, 10)]))
            for code in self.Triggers[snippet]:
                sums = []
                for token in subset:
                    if token in self.Triggers[snippet][code] and token != snippet:
                        sums.append(self.Triggers[snippet][code][token])
                base = self.Triggers[snippet][code][snippet]/self.W[snippet]
                givens = 0
                tot = np.sum([np.abs(x) for x in sums])
                if tot >= 5:
                    givens = 0.5*np.sum(sums)/tot
                probability = base + givens
                if probability > 0.8:
                    if code not in assignments:
                        assignments[code] = []
                    assignments[code].append(i)
        ret = []
        for code in assignments:
            prevIndex = -2
            for index in sorted(assignments[code]):
                if prevIndex >=0 and (tokens[prevIndex]["endIndex"] +1 >= tokens[index]["startIndex"] or prevIndex+1 == index):
                    ret[-1]["endIndex"] = tokens[index]["endIndex"]
                    ret[-1]["snippet"] = text[ret[-1]["startIndex"]:ret[-1]["endIndex"]]
                    prevIndex = index
                    continue
                codeDict = json.loads(json.dumps(self.Codes[code]))
                codeDict["startIndex"] = tokens[index]["startIndex"]
                codeDict["endIndex"] = tokens[index]["endIndex"]
                codeDict["snippet"] = text[tokens[index]["startIndex"]:tokens[index]["endIndex"]]
                ret.append(codeDict)
                prevIndex = index
        ## check for nested codes
        all = []
        for trial in ret:
            found = False
            for tri in ret:
                if len(set(getAllNodes(trial)).intersection(getAllNodes(tri))) != len(getAllNodes(trial)):
                    continue
                if len(getAllNodes(trial)) == len(getAllNodes(tri)):
                    continue
                if tri["startIndex"] > trial["endIndex"]:
                    continue
                if tri["endIndex"] < trial["startIndex"]:
                    continue
                found = True
            if not found:
                all.append(trial)
        return all

    def update_trigger(self, tokens, i, code, modifier=0.5):
        snippet = tokens[i]["token"]
        if snippet not in self.Triggers:
            self.Triggers[snippet] = {}
        if code not in self.Triggers[snippet]:
            self.Triggers[snippet][code] = {}
        subset = getSubset(tokens, i, -10, 10) + [tokens[i]]
        for token in subset:
            if token["token"] not in self.Triggers[snippet][code]:
                self.Triggers[snippet][code][token["token"]] = 0
            self.Triggers[snippet][code][token["token"]] = self.Triggers[snippet][code][token["token"]] + modifier

    def train_one_document(self, text, correct):
        predicted = self.predict(text)
        tokens = wildgram(text, returnNoise=False)
        ## add any codes that don't exist already...
        for code in correct:
            newcode = json.loads(json.dumps(code))
            del newcode["startIndex"]
            del newcode["endIndex"]
            del newcode["snippet"]
            if "children" not in newcode:
                newcode["children"] = []
            if convertCodeDictToString(code) not in self.Codes:
                self.Codes[convertCodeDictToString(code)] = newcode
        ### for each token in wildgram'd version
        for i in range(len(tokens)):
            if tokens[i]["token"] not in self.W:
                self.W[tokens[i]["token"]] = 0
            self.W[tokens[i]["token"]] = self.W[tokens[i]["token"]] + 1
            corr = findMatching(tokens[i], correct)
            pred = findMatching(tokens[i], predicted)
            for code in corr:
                self.update_trigger(tokens, i, code, 1)
            for code in pred:
                if code not in corr:
                    self.update_trigger(tokens, i, code, -2)
        ## pruning
        for trigger in self.Triggers:
            for code in self.Triggers[trigger]:
                if self.Triggers[trigger][code][trigger] == 0:
                    continue
                for given in list(self.Triggers[trigger][code].keys()):
                    if np.abs(self.Triggers[trigger][code][given]/self.Triggers[trigger][code][trigger])< 0.05:
                        del self.Triggers[trigger][code][given]
