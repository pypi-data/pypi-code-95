#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
copied from x-deepleanring repo
"""

import os
import sys

import collections
import oyaml as yaml
import copy


class FgConfConverter(object):
    def __init__(self, yaml_str):
        self._yaml_obj = yaml.load(yaml_str, Loader=yaml.Loader)
        self._shared_slots = []

        self._slot_2_names = collections.OrderedDict()
        self._output_2_inputs = collections.OrderedDict()
        self._slot_share_dct = collections.OrderedDict()
        self._name_2_iter_dct = collections.OrderedDict()
        self.parse()

    def parse(self):
        last_slot = None
        for key_val in ["shared", "iterable"]:
            for op_iter in self._yaml_obj[key_val]:
                name = op_iter["name"]

                assert name not in self._name_2_iter_dct, (
                    "%s field duplicate in ori yaml" % name
                )
                self._name_2_iter_dct[name] = op_iter

                inputs = op_iter["input"].split(",")
                self._output_2_inputs[name] = inputs

                if "export" in op_iter:
                    slot = op_iter["export"]["slot"]

                    if key_val == "shared":
                        self._shared_slots.append(slot)

                    if slot not in self._slot_2_names:
                        self._slot_2_names[slot] = []
                    else:
                        assert last_slot == slot, "Same slot must be adjacent"
                    self._slot_2_names[slot].append(name)
                    last_slot = slot

    def _get_valid_names(self, export_names):
        valid_names = copy.deepcopy(export_names)

        while True:
            names_cnt = len(valid_names)
            for i in range(names_cnt):
                name = valid_names[i]

                for input_name in self._output_2_inputs[name]:
                    input_name = input_name.strip()
                    if (
                        input_name not in valid_names
                    ) and input_name in self._output_2_inputs:
                        valid_names.append(input_name)

            if names_cnt == len(valid_names):
                break

        return set(valid_names)

    def _build_new_yaml_obj(self, valid_names_set):
        new_yaml_obj = collections.OrderedDict()
        new_yaml_obj["indexer"] = copy.deepcopy(self._yaml_obj["indexer"])

        for key_val in ["shared", "iterable"]:
            new_yaml_obj[key_val] = []
            for op_iter in self._yaml_obj[key_val]:
                name = op_iter["name"]
                if name in valid_names_set:
                    new_yaml_obj[key_val].append(op_iter)

        return new_yaml_obj

    def get_shared_slots(self):
        return self._shared_slots

    def extract_sub_dag(self, valid_slots):
        export_names = []
        for slot in valid_slots:
            assert slot in self._slot_2_names, (
                "ori yaml dosen't export slot %s, \
        which dosen't match with model input"
                % str(slot)
            )

            export_names.extend(self._slot_2_names[slot])

        valid_name_set = self._get_valid_names(export_names)
        new_yaml_obj = self._build_new_yaml_obj(valid_name_set)

        self._shared_slots = [
            slot for slot in self._shared_slots if slot in valid_slots
        ]
        return yaml.dump(new_yaml_obj)
