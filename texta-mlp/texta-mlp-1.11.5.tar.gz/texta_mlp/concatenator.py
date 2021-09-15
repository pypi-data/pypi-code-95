import copy
import json
from typing import List

import numpy as np
import regex as re

from .exceptions import BoundedListEmpty


class Concatenator:
    """
    Class for concatenating BOUNDS across mails.
    """

    ENTITIES_TO_BEAUTIFY = ["ORG", "LOC", "GPE"]  # abbreviations and lemmas are checked when loading the data
    DEFAULT_MLP_OUTPUT_DIR = ""
    DEFAULT_ABBREVIATIONS_DIR = "data/abbreviations.json"


    def __init__(self, resource_dir=DEFAULT_MLP_OUTPUT_DIR, abbr_dir=DEFAULT_ABBREVIATIONS_DIR, logging_level="error"):
        self.resource_dir = resource_dir
        self.abbr_dir = abbr_dir
        self.abbreviations = dict()
        self.get_abbreviations()
        self.bounded = list()

        self.persona_infos = dict()  # {'Anna Puu': {'435432334': 'PHONE', '32793726354': 'PHONE', 'Новороссия': 'LOC', 'annapuu@gmail.com': 'EMAIL'} }
        self.no_personas_infos = list()
        self.unsure_infos = list()
        self.just_pers_infos = list()


    def get_abbreviations(self):
        abbrs = dict()
        with open(self.abbr_dir, 'r') as j:
            abbrs = json.loads(j.read())
        abbrs_ = dict()
        for key in abbrs:
            abbrs_[key.lower()] = abbrs[key].lower()
        self.abbreviations = abbrs_


    def beautify_entity_value(self, entity_value):
        """
        replace abbreviations with it's values
        """
        if entity_value.lower() in self.abbreviations:
            entity_value = self.abbreviations[entity_value.lower()].strip().title()
            return entity_value
        r = re.compile("(^|\s)(" + ".*".join([re.escape(s) for s in entity_value.lower().split()]) + "|" + ".*".join([re.escape(s) for s in entity_value.lower().split()[::-1]]) + ")(\s|$)")
        parts_matched = list(filter(r.match, self.abbreviations.keys()))
        if parts_matched:
            entity_value = self.abbreviations[parts_matched[0]].strip().title()
            return entity_value
        entity_value_ = ""
        for word in entity_value.split():
            word = word.strip()
            if word.lower() in self.abbreviations:
                entity_value_ += " " + self.abbreviations[word.lower()].strip().title()
            else:
                entity_value_ += " " + word.title()
        return entity_value_.strip().strip("»«\*")


    def _abbreviations(self):
        return self.abbreviations


    def _bounded(self):
        return self.bounded


    def _persona_infos(self):
        return self.persona_infos


    def _no_personas_infos(self):
        return self.no_personas_infos


    def _unsure_infos(self):
        return self.unsure_infos


    def _just_pers_infos(self):
        return self.just_pers_infos


    def unique(self, bounded: list) -> list:
        """
        #GET UNIQUE DICTIONARIES, ERASE SUBSETS (WITH SAME KEYS)
        #first one BOUNDED is a subset of another one OR keys are the same {XXX, 'Новороссия': 'LOC'} and {XXX,'Новороссия': 'ORG'} (in this case entity_type is chosen randomly (whichever is first))
        """
        bounded = list(np.unique(np.array(bounded).astype(str)))
        bounds_to_delete_ids = []
        concatenated_bounds = []
        bounded_ = list()

        # Some BOUNDED with only one PER can be a subset of sth with two PERs, first take them out.
        for i, bound1 in enumerate(bounded):
            bound1 = json.loads(re.sub("\'", "\"", str(bound1)))
            per_values = [k for k, v in bound1.items() if v == "PER"]
            if len(per_values) == 1:
                if per_values[0] in self.persona_infos:
                    del bound1[per_values[0]]
                    self.persona_infos[per_values[0]].update(bound1)
                else:
                    del bound1[per_values[0]]
                    self.persona_infos[per_values[0]] = bound1
            else:
                bounded_.append(bound1)
        # Search for subsets
        for i, bound1 in enumerate(bounded_):
            for j, bound2 in enumerate(bounded_):
                if i != j and i not in bounds_to_delete_ids and j not in bounds_to_delete_ids:
                    if bound1.items() < bound2.items() or bound1.keys() <= bound2.keys():
                        bounds_to_delete_ids += [i]
                    elif bound1.items() > bound2.items() or bound1.keys() >= bound2.keys():
                        bounds_to_delete_ids += [j]
                    elif len(set([k for k, v in bound1.items() if v == "PER"])) != 0 and set([k for k, v in bound1.items() if v == "PER"]) == set([k for k, v in bound2.items() if v == "PER"]):
                        bound1.update(bound2)
                        bounds_to_delete_ids += [j]
            concatenated_bounds += [bound1]
        # return filtered BOUNDEDs
        filtered_bounds = []
        for i, bound1 in enumerate(concatenated_bounds):
            if i not in bounds_to_delete_ids:
                filtered_bounds += [bound1]
        return filtered_bounds


    @staticmethod
    def check_matching(parts_matched):
        all_match = True  # ["Tom", "Tom Marvolo", "Tom Marvolo Riddle"] == True, #["Tom", "Tom Marvolo", "Tom Kuusk"] == False
        for p_m1 in parts_matched:
            shortened1 = ""
            if len(p_m1.split()) == 1:
                shortened1 = "(^|\s)" + p_m1[0] + ".*"
            else:
                for k in p_m1.split()[:-1]:
                    shortened1 += k.strip(".") + ".*"
                shortened1 += p_m1.split()[-1]
            for p_m2 in parts_matched:
                shortened2 = ""
                if len(p_m2.split()) == 1:
                    shortened2 = "(^|\s)" + p_m2[0] + ".*"
                else:
                    for k in p_m2.split()[:-1]:
                        shortened2 += k.strip(".") + ".*"
                    shortened2 += p_m2.split()[-1]
                if len(p_m1.split()) == 3 and len(p_m2.split()) == 3:
                    if not (re.search(
                            "(^|\s)(" + ".*".join([re.escape(s) for s in p_m1.split()]) + "|" + ".*".join([re.escape(s) for s in p_m1.split()[::-1]]) + "|" + p_m1.split()[1] + ".*" + p_m1.split()[2] + ".*" + p_m1.split()[0] + "|" + p_m1.split()[0] + ".*" + p_m1.split()[2] + ".*" + p_m1.split()[
                                1] + ")(\s|$)", p_m2) or re.search(
                        "(^|\s)(" + ".*".join([re.escape(s) for s in p_m2.split()]) + "|" + ".*".join([re.escape(s) for s in p_m2.split()[::-1]]) + "|" + p_m2.split()[1] + ".*" + p_m2.split()[2] + ".*" + p_m2.split()[0] + "|" + p_m2.split()[0] + ".*" + p_m2.split()[2] + ".*" + p_m2.split()[
                            1] + ")(\s|$)", p_m1) or re.search(shortened1, shortened2) or re.search(shortened2, shortened1)):
                        return False
                else:
                    if not (re.search("(^|\s)(" + ".*".join([re.escape(s) for s in p_m1.split()]) + "|" + ".*".join([re.escape(s) for s in p_m1.split()[::-1]]) + ")(\s|$)", p_m2) or re.search(
                            "(^|\s)(" + ".*".join([re.escape(s) for s in p_m2.split()]) + "|" + ".*".join([re.escape(s) for s in p_m2.split()[::-1]]) + ")(\s|$)", p_m1) or re.search(shortened1, shortened2) or re.search(shortened2, shortened1)):
                        return False
        return all_match


    def unique_keys(self, pers_dict):
        """
        Concatenate key-value pairs that has similar keys.
        Eg. "Tom Riddle" + "Tom Marvolo Riddle"
        Used in function divide
        """
        keys = copy.deepcopy(list(pers_dict.keys()))
        for key in keys:
            keys_ = copy.deepcopy(list(pers_dict.keys()))
            if key in keys_:
                keys_.remove(key)
                splitted_key = key.split()
                if len(splitted_key) > 1:
                    shortened = ""
                    if "." in key:
                        for name in splitted_key[:-1]:
                            shortened += name[0].strip() + ".*"
                        shortened += splitted_key[-1]
                    else:
                        for name in splitted_key[:-1]:
                            shortened += name[0].strip() + ". "
                        shortened += splitted_key[-1]
                    if len(splitted_key) == 3:
                        if shortened:
                            r = re.compile(
                                "(^|\s)(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + "|" + splitted_key[1] + ".*" + splitted_key[2] + ".*" + splitted_key[0] + "|" + splitted_key[0] + ".*" + splitted_key[2] + ".*" + splitted_key[
                                    1] + "|" + shortened + ")(\s|$)")
                    else:
                        if shortened:
                            r = re.compile("(^|\s)(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + "|" + shortened + ")(\s|$)")
                else:
                    r = re.compile("(^|\s)(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + ")(\s|$)")
                parts_matched = list(filter(r.search, keys_))  # if PER is "Tom Riddle", and there´s already "Tom Marvolo Riddle"
                if len(parts_matched) == 1:
                    if len(parts_matched[0]) >= len(key):
                        pers_dict[parts_matched[0]].update(pers_dict[key])
                        del pers_dict[key]
                    else:
                        pers_dict[key].update(pers_dict[parts_matched[0]])
                        del pers_dict[parts_matched[0]]
                elif len(parts_matched) > 1:
                    all_match = self.check_matching(parts_matched)
                    if all_match:
                        longest = max(parts_matched, key=len)
                        parts_matched.remove(longest)
                        pers_dict[longest].update(pers_dict[key])
                        del pers_dict[key]
                        for p_m in parts_matched:
                            if p_m != longest:
                                pers_dict[longest].update(pers_dict[p_m])
                                del pers_dict[p_m]
                    else:
                        if len(splitted_key) > 1:
                            shortened = ""
                            if "." in key:
                                for name in splitted_key[:-1]:
                                    shortened += name[0].strip() + ".*"
                                shortened += splitted_key[-1]
                            if len(splitted_key) == 3:
                                if shortened:
                                    r = re.compile("^(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + "|" + splitted_key[1] + ".*" + splitted_key[2] + ".*" + splitted_key[0] + "|" + splitted_key[0] + ".*" + splitted_key[2] + ".*" +
                                                   splitted_key[1] + "|" + shortened + ")$")
                                else:
                                    r = re.compile("^(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + "|" + splitted_key[1] + ".*" + splitted_key[2] + ".*" + splitted_key[0] + "|" + splitted_key[0] + ".*" + splitted_key[2] + ".*" +
                                                   splitted_key[1] + ")$")
                            else:
                                if shortened:
                                    r = re.compile("^(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + "|" + shortened + ")$")
                                else:
                                    r = re.compile("^(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + ")$")
                        else:
                            r = re.compile("^(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + ")$")
                        parts_matched = list(filter(r.search, parts_matched))
                        if len(parts_matched) == 1:
                            if len(parts_matched[0]) >= len(key):
                                pers_dict[parts_matched[0]].update(pers_dict[key])
                                del pers_dict[key]
                            else:
                                pers_dict[key].update(pers_dict[parts_matched[0]])
                                del pers_dict[parts_matched[0]]
                        elif len(parts_matched) > 1:
                            all_match = self.check_matching(parts_matched)
                            if all_match:
                                longest = max(parts_matched, key=len)
                                parts_matched.remove(longest)
                                pers_dict[longest].update(pers_dict[key])
                                del pers_dict[key]
                                for p_m in parts_matched:
                                    if p_m != longest:
                                        pers_dict[longest].update(pers_dict[p_m])
                                        del pers_dict[p_m]
        return pers_dict


    def matching_key(self, per_value):
        """
        If there`s no equal key, check, if there`s partly equal keys (per_value is a subset) and those are subsets or superssets of each other.

        Example:
        If persona_infos.keys() = ["Tom", "Tom Marvolo", "Tom Marvolo Riddle", "Tom Kuusk", "Муравьев Леонид Иванович"]
        then:
        per_value = "Tom Marvolo" ==> parts_matched = ["Tom Marvolo", "Tom Marvolo Riddle"] ==> all_match, return the list,
        per_value = "Tom" ==> parts_matched = ["Tom", "Tom Marvolo", "Tom Kuusk"] ==> all_do_not_match, return None,
        per_value = "Леонид Муравьев" ==> partc_matched = ["Муравьев Леонид Иванович"] == all_match, return the list
        """
        splitted_key = per_value.split()
        if len(splitted_key) > 1:
            shortened = ""
            if "." in per_value:
                for name in splitted_key[:-1]:
                    shortened += name[0].strip() + ".*"
                shortened += splitted_key[-1]
            if len(splitted_key) == 3:
                if shortened:
                    r = re.compile(
                        "(^|\s)(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + "|" + splitted_key[1] + ".*" + splitted_key[2] + ".*" + splitted_key[0] + "|" + splitted_key[0] + ".*" + splitted_key[2] + ".*" + splitted_key[
                            1] + "|" + shortened + ")(\s|$)")
                else:
                    r = re.compile(
                        "(^|\s)(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + "|" + splitted_key[1] + ".*" + splitted_key[2] + ".*" + splitted_key[0] + "|" + splitted_key[0] + ".*" + splitted_key[2] + ".*" + splitted_key[
                            1] + ")(\s|$)")
            else:
                if shortened:
                    r = re.compile("(^|\s)(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + "|" + shortened + ")(\s|$)")
                else:
                    r = re.compile("(^|\s)(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + ")(\s|$)")
        else:
            r = re.compile("(^|\s)(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + ")(\s|$)")

        parts_matched = list(filter(r.search, self.persona_infos.keys()))  # if PER is "Tom Riddle", and there´s already "Tom Marvolo Riddle"
        if len(parts_matched) == 1:
            return parts_matched
        elif len(parts_matched) > 1:
            all_match = self.check_matching(parts_matched)
            if all_match:
                return parts_matched
            else:
                if len(splitted_key) > 1:
                    shortened = ""
                    if "." in per_value:
                        for name in splitted_key[:-1]:
                            shortened += name[0].strip() + ".*"
                        shortened += splitted_key[-1]
                    if len(splitted_key) == 3:
                        if shortened:
                            r = re.compile(
                                "^(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + "|" + splitted_key[1] + ".*" + splitted_key[2] + ".*" + splitted_key[0] + "|" + splitted_key[0] + ".*" + splitted_key[2] + ".*" + splitted_key[
                                    1] + "|" + shortened + ")$")
                        else:
                            r = re.compile(
                                "^(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + "|" + splitted_key[1] + ".*" + splitted_key[2] + ".*" + splitted_key[0] + "|" + splitted_key[0] + ".*" + splitted_key[2] + ".*" + splitted_key[
                                    1] + ")$")
                    else:
                        if shortened:
                            r = re.compile("^(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + "|" + shortened + ")$")
                        else:
                            r = re.compile("^(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + ")$")
                else:
                    r = re.compile("^(" + ".*".join([re.escape(s) for s in splitted_key]) + "|" + ".*".join([re.escape(s) for s in splitted_key[::-1]]) + ")$")
                parts_matched = list(filter(r.search, parts_matched))
                all_match = self.check_matching(parts_matched)
                if all_match:
                    return parts_matched
        return None


    def divide(self):
        """
        #divide bounded to persona_infos, no_personas_infos, just_pers_infos and unsure_infos
        """

        for f_bound_ in self.bounded:
            f_bound = copy.deepcopy(f_bound_)
            if len(f_bound.items()) > 1:
                per_values = [k for k, v in f_bound.items() if v == "PER"]
                if len(per_values) == len(f_bound.items()):
                    self.just_pers_infos.append(f_bound)
                elif len(per_values) == 0:
                    self.no_personas_infos.append(f_bound)
                elif len(per_values) == 1:  # Should not exist anymore, but just checking.
                    if per_values[0] in self.persona_infos:
                        del f_bound[per_values[0]]
                        self.persona_infos[per_values[0]].update(f_bound)
                    else:
                        del f_bound[per_values[0]]
                        self.persona_infos[per_values[0]] = f_bound
                else:
                    self.unsure_infos.append(f_bound)


    def entity_per_check(self, new_unsure_infos, entity_pers_dict):
        """
        Check whether some entity occurs only with some certain PER.
        Example:
        entity_pers_dict = {'Gurkhul':[["Terry Pratchett", "Joe Abercrombie"], ["Joe Abercrombie", "J.K. Rowling"]], #NB! We can see that J.A. is always with Gurkhul.
                            'Loss':[["Marten Kuningas", "Martena Kuninganna"], ["Prince", "Queen"]]} #NB! The entity_type doesn´t matter here anymore.
        new_unsure_infos = [{'Joe Abercrombie': 'PER', 'Gurkhul': 'LOC', "J.K. Rowling": 'PER'},
                        {'Joe Abercrombie': 'PER', 'Gurkhul': 'LOC', 'Terry Pratchett': 'PER'},
                        {"Marten Kuningas": 'PER', 'Loss': 'LOC',  "Martena Kuninganna": 'PER'},
                        {"Prince": 'PER', 'Loss': 'LOC', "Queen": 'PER'}]
        persona_infos = {'Aleksander Great': {'76883266': 'PHONE',  'aleksandersuur356eKr@mail.ee': 'EMAIL', 'Vana-Makedoonia': 'LOC'},
                        'Terry Pratchett': {'Discworld': 'LOC', '12345678': 'PHONE', 'Ankh-Morpork': 'LOC'}}

        ==>

        just_pers_infos =  [{'Aleksander Great': 'PER', 'Terry Pratchett': 'PER'},
                            {'Joe Abercrombie': 'PER', 'Terry Pratchett': 'PER'},
                            {'Joe Abercrombie': 'PER', "J.K. Rowling": 'PER'}]
        unsure_infos = [{"Marten Kuningas": 'PER', 'Loss': 'LOC',  "Martena Kuninganna": 'PER'},
                        {"Prince": 'PER', 'Loss': 'LOC', "Queen": 'PER'}]
        persona_infos = {'Aleksander Great': {'76883266': 'PHONE',  'aleksandersuur356eKr@mail.ee': 'EMAIL', 'Vana-Makedoonia': 'LOC'},
                        'Terry Pratchett': {'Discworld': 'LOC', '12345678': 'PHONE', 'Ankh-Morpork': 'LOC'},
                        'Joe Abercrombie': {'Gurkhul': 'LOC'}}

        save unsure_infos.
        """
        actually_has_a_per = dict()  # {"Discworld" : "Terry Pratchett"}
        for entity_value, per_values in entity_pers_dict.items():
            always_with_the_entity_pers = list(set.intersection(*per_values))
            if len(always_with_the_entity_pers) == 1:
                actually_has_a_per[entity_value] = always_with_the_entity_pers[0]

        double_checked_unsure_infos = list()
        for u_bound in new_unsure_infos:
            u_bound_ = dict()
            for entity_value, entity_type in u_bound.items():
                if entity_value not in actually_has_a_per:
                    u_bound_[entity_value] = entity_type
                else:
                    if actually_has_a_per[entity_value] in self.persona_infos:
                        if entity_value not in self.persona_infos[actually_has_a_per[entity_value]]:
                            self.persona_infos[actually_has_a_per[entity_value]].update({entity_value: entity_type})
                    else:
                        self.persona_infos[actually_has_a_per[entity_value]] = {entity_value: entity_type}
            per_values = [k for k, v in u_bound_.items() if v == "PER"]
            if len(per_values) == len(u_bound_.items()):
                self.just_pers_infos.append(u_bound_)
            else:
                double_checked_unsure_infos.append(u_bound_)

        self.unsure_infos = double_checked_unsure_infos
        del new_unsure_infos
        del double_checked_unsure_infos


    def check_unsure_infos(self):
        """
        #check if some entites in BOUNDEDs in unsure_infos are same in persona_infos under the BOUNDED PERs. Delete those as connection found already. Remaining is still unsure (to which PER does the LOC/EMAIL etc belong),
        if no entity is left, add to self.just_pers_infos.

        Example:
        unsure_infos = [{'Aleksander Great': 'PER',  'aleksandersuur356eKr@mail.ee': 'EMAIL', 'Vana-Makedoonia': 'LOC', 'Terry Pratchett': 'PER', 'Discworld': 'LOC', '12345678': 'PHONE', 'Ankh-Morpork': 'LOC'},
        {'Joe Abercrombie': 'PER', 'Gurkhul': 'LOC', 'Terry Pratchett': 'PER', 'Ankh-Morpork': 'LOC'}]
        persona_infos = {'Aleksander Great': {'76883266': 'PHONE',  'aleksandersuur356eKr@mail.ee': 'EMAIL', 'Vana-Makedoonia': 'LOC'},
                        'Terry Pratchett': {'Discworld': 'LOC', '12345678': 'PHONE', 'Ankh-Morpork': 'LOC'}}

        ==>

        just_pers_infos =  [{'Aleksander Great': 'PER', 'Terry Pratchett': 'PER'}]
        new_unsure_infos = [{'Joe Abercrombie': 'PER', 'Gurkhul': 'LOC', 'Terry Pratchett': 'PER'}]
        persona_infos = {'Aleksander Great': {'76883266': 'PHONE',  'aleksandersuur356eKr@mail.ee': 'EMAIL', 'Vana-Makedoonia': 'LOC'},
                        'Terry Pratchett': {'Discworld': 'LOC', '12345678': 'PHONE', 'Ankh-Morpork': 'LOC'}}
        """
        new_unsure_infos = list()
        entity_pers_dict = dict()  # {"Discworld" : [["Terry Pratchett", "Joe Abercrombie"], ["Terry Pratchett", "J.K. Rowling"]]}
        for i, u_bounded_ in enumerate(self.unsure_infos):
            u_bounded = copy.deepcopy(u_bounded_)
            per_values = [k for k, v in u_bounded.items() if v == "PER"]  # PERs in that BOUNDED fact.
            to_delete = list()
            values_to_replace = []
            for per_value in per_values:
                intersections = list()
                if per_value in self.persona_infos:
                    intersection = set(u_bounded) & set(self.persona_infos[per_value])
                    if intersection != set():
                        intersections.append(intersection)
                else:
                    parts_matched = self.matching_key(per_value)
                    if parts_matched:
                        # print(per_value,  max(parts_matched+[per_value], key=len), parts_matched+[per_value])
                        values_to_replace.append((per_value, max(parts_matched + [per_value], key=len)))
                        intersection = set(u_bounded)
                        for part_matched in parts_matched:
                            intersection = intersection & set(self.persona_infos[part_matched])
                        if intersection != set():
                            intersections.append(intersection)
                if intersections != []:
                    to_delete.append(set.intersection(*intersections))

            for delete_set in to_delete:
                for delete in delete_set:
                    if delete in u_bounded and delete not in per_values:
                        del u_bounded[delete]

            for old_per, new_per in values_to_replace:
                del u_bounded[old_per]
                u_bounded[new_per] = "PER"
            if len(per_values) == len(u_bounded.items()):
                self.just_pers_infos.append(u_bounded)
            else:
                per_values = [k for k, v in u_bounded.items() if v == "PER"]  # PERs in that renewed BOUNDED fact.
                for entity_value, entity_type in u_bounded.items():
                    if entity_type != "PER":
                        if entity_value in entity_pers_dict:
                            entity_pers_dict[entity_value] += [set(per_values)]
                        else:
                            entity_pers_dict[entity_value] = [set(per_values)]

                new_unsure_infos.append(u_bounded)

        return new_unsure_infos, entity_pers_dict


    def concatenate(self):
        if not self.bounded:
            raise BoundedListEmpty("The class has no BOUNDED facts loaded yet.")
        self.bounded = self.unique(self.bounded)
        self.divide()
        self.persona_infos = self.unique_keys(self.persona_infos)
        new_unsure_infos, entity_pers_dict = self.check_unsure_infos()
        self.entity_per_check(new_unsure_infos, entity_pers_dict)
        self.persona_infos = self.unique_keys(self.persona_infos)


    def saveable_list(self, dictionary_name, type_name):
        new_list = list()
        for infos_dict in dictionary_name:
            new_dict = {"type": type_name}
            for entity_value in infos_dict:
                if infos_dict[entity_value] in new_dict:
                    new_dict[infos_dict[entity_value]] += [entity_value]
                else:
                    new_dict[infos_dict[entity_value]] = [entity_value]
            new_list.append(new_dict)
        return new_list


    def to_json(self):
        container = []

        for person in self._persona_infos():
            new_dict = {"type": "person_info", "PER": person}
            for key in self._persona_infos()[person]:
                if self._persona_infos()[person][key] in new_dict and self._persona_infos()[person][key] != "PER":
                    new_dict[self._persona_infos()[person][key]] += [key]
                else:
                    new_dict[self._persona_infos()[person][key]] = [key]
            container.append(new_dict)

        no_per = self.saveable_list(self._no_personas_infos(), "no_per_close_entities")
        if no_per: container.append(no_per)

        whose_entities = self.saveable_list(self._unsure_infos(), "unsure_whose_entities")
        if whose_entities: container.append(whose_entities)

        close_pers = self.saveable_list(self._just_pers_infos(), "close_persons")
        if close_pers: container.append(close_pers)

        return container


    def from_json(self, mlp_outputs: List[dict]):
        for output in mlp_outputs:
            for fact in output["texta_facts"]:
                if fact["fact"] == "BOUNDED":
                    bound = {}
                    bounded_facts = json.loads(re.sub("\'", "\"", fact['str_val']))
                    lemmas = json.loads(re.sub("\'", "\"", fact["lemma"]))
                    for entity_type in bounded_facts:
                        if entity_type in self.ENTITIES_TO_BEAUTIFY:
                            for i, entity_value in enumerate(lemmas[entity_type]):
                                if entity_value != "UNK":
                                    bound[self.beautify_entity_value(entity_value)] = entity_type
                                else:
                                    bound[self.beautify_entity_value(bounded_facts[entity_type][i])] = entity_type
                        else:
                            if entity_type != "EMAIL":
                                for entity_value in bounded_facts[entity_type]:
                                    bound[entity_value.strip().strip("»«\*").title()] = entity_type
                            else:
                                for entity_value in bounded_facts[entity_type]:
                                    bound[entity_value.strip("»«\*").strip()] = entity_type
                    self.bounded.append(bound)
