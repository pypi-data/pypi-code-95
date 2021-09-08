from wildgram import wildgram
import connect_umls as um
import itertools
import numpy as np

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
        code = pred["unit"] + "|||" + pred["value"]
        if token["startIndex"] < pred["startIndex"]:
            continue
        if token["endIndex"] > pred["endIndex"]:
            continue
        found.append(code)
    return found
    
class MagicRules:
    def __init__(self):
        self.W = {}
        self.Triggers = {}

    def add_umls_cui(self, cui_code, apikey):
        umls = um.UMLS(apikey)
        cui = um.CUI(apikey, cui_code, "")
        triggers = cui.synonyms()
        for trigger in triggers:
            self.add_trigger(trigger, "UMLS", cui_code)

    def add_trigger(self, trigger, unit, value):
        code = unit +"|||"+value
        tokens = wildgram(trigger, returnNoise=False)
        for token in tokens:
            tok = token["token"]
            self.W[tok] = 5
            self.Triggers[tok] = {}
            self.Triggers[tok][code] = {}
            self.Triggers[tok][code][tok] = 5
            continue
        combos = itertools.combinations(tokens, 2)
        for combo in combos:
            self.Triggers[combo[0]["token"]][code][combo[1]["token"]] = 5
            self.Triggers[combo[1]["token"]][code][combo[0]["token"]] = 5

    def predict(self, text):
        tokens = wildgram(text, returnNoise=False)
        assignments = {}
        for i in range(len(tokens)):
            snippet = tokens[i]["token"]
            if snippet not in self.Triggers:
                continue
            subset = getSubset(tokens, i, -10, 10)
            for code in self.Triggers[snippet]:
                sums = []
                for token in subset:
                    if token["token"] in self.Triggers[snippet][code]:
                        sums.append(self.Triggers[snippet][code][token["token"]])
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
                if index == prevIndex + 1:
                    ret[-1]["endIndex"] = tokens[index]["endIndex"]
                    ret[-1]["snippet"] = text[ret[-1]["startIndex"]:ret[-1]["endIndex"]]
                    prevIndex = index
                    continue
                ret.append({"unit":code.split("|||")[0], "value":code.split("|||")[1], "startIndex": tokens[index]["startIndex"], "endIndex": tokens[index]["endIndex"], "snippet": text[tokens[index]["startIndex"]:tokens[index]["endIndex"]]})
                prevIndex = index
        return ret

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
