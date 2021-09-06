import json
import logging

class Diff:

    sittings = ('StartTime', 'FinishTime', 'SittingTypeName', 'DisplayName', 'CourtName', 'MeetingDate',
                               'SittingActivityStatusName')

    decisions = ('CourtName', 'DecisionName', 'DecisionStatusChangeDate')
    verdicts = decisions

    spec = {'sittings': sittings, 'decisions': decisions, 'verdicts': verdicts}

    def __init__(self):
        self.logger = logging.getLogger('diff')

    def canonicalize_obj(self, obj, spec_name):
        assert spec_name in Diff.spec.keys()
        o = {}
        for f in self.spec[spec_name]:
            o[f] = obj[f]
        return json.dumps(o)

    def canonicalize_list_of_obj(self, list_of_objects, spec_name):
        assert spec_name in Diff.spec.keys()
        l = []
        for obj in list_of_objects:
            o = self.canonicalize_obj(obj, spec_name)
            l.append(o)

        l.sort()
        return json.dumps(l)

    def has_changed(self, list1, list2, spec_name):
        assert spec_name in Diff.spec.keys()
        c1 = self.canonicalize_list_of_obj(list1, spec_name)
        c2 = self.canonicalize_list_of_obj(list2, spec_name)
        return c1 != c2

    def detect_changes(self, old_list, new_list, spec_name):
        assert spec_name in Diff.spec.keys()
        old_map = {}
        new_map = {}
        old_set = set()
        new_set = set()

        for i, o in enumerate(old_list):
            canonicalized = self.canonicalize_obj(o, spec_name)
            old_map[canonicalized] = i
            old_set.add(canonicalized)

        for i, o in enumerate(new_list):
            canonicalized = self.canonicalize_obj(o, spec_name)
            new_map[canonicalized] = i
            new_set.add(canonicalized)

        removed = old_set.difference(new_set)
        added = new_set.difference(old_set)

        number_of_removed = len(removed)

        added_indices = []
        for m in added:
            index = new_map[m]
            self.logger.info('Added %s of %s', index, len(new_list))
            added_indices.append(index)
        added_indices.sort()

        continuous = True
        for i in range(0, len(added_indices)-1):
            continuous = continuous and added_indices[i] + 1 == added_indices[i+1]
        mx = added_indices[-1]
        mn = added_indices[0]
        self.logger.info('Added. min index %s, max index %s, length %s, all %s', mn, mx, len(new_list), added_indices)
        if not added:
            self.logger.info('No added')

        is_end = mx == len(new_list) - 1

        delta_scrape = {'can': len(removed) == 0 and continuous and is_end, 'range': (mn, mx+1)}
        return delta_scrape

    def copy_extra_data(self, oldlist, newlist, specname):
        assert specname in Diff.spec.keys()
        shortest = min(len(oldlist), len(newlist))
        fields = Diff.spec[specname]
        for i in range(shortest):
            old = oldlist[i]
            new = newlist[i]

            for k, v in old.items():
                if k not in fields:
                    new[k] = v

