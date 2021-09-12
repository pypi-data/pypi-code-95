"""
Common mappings for MYSTRAN and FEMAP
for each self.flavor, describe vectors in terms of (<vector>, <axis>)
"""
import logging
from collections import defaultdict

from femap_neutral_parser.utils import CaseInsensitiveDict

FLAVORS = CaseInsensitiveDict(
    {
        "MYSTRAN": {
            "RSS translation": ("disp", "t_total"),
            "T1 translation": ("disp", "t1"),
            "T2 translation": ("disp", "t2"),
            "T3 translation": ("disp", "t3"),
            "RSS rotation": ("disp", "r_total"),
            "R1 rotation": ("disp", "r1"),
            "R2 rotation": ("disp", "r2"),
            "R3 rotation": ("disp", "r3"),
            "RSS applied force": ("force_applied", "f_total"),
            "T1 applied force": ("force_applied", "f1"),
            "T2 applied force": ("force_applied", "f2"),
            "T3 applied force": ("force_applied", "f3"),
            "RSS applied moment": ("force_applied", "m_total"),
            "R1 applied moment": ("force_applied", "m1"),
            "R2 applied moment": ("force_applied", "m2"),
            "R3 applied moment": ("force_applied", "m3"),
            "RSS SPC force": ("force_reac", "f_total"),
            "T1 SPC force": ("force_reac", "f1"),
            "T2 SPC force": ("force_reac", "f2"),
            "T3 SPC force": ("force_reac", "f3"),
            "RSS SPC moment": ("force_reac", "m_total"),
            "R1 SPC moment": ("force_reac", "m1"),
            "R2 SPC moment": ("force_reac", "m2"),
            "R3 SPC moment": ("force_reac", "m3"),
            "BAR EndA Plane1 Moment": ("force_cbar", "bending_moment_a1"),
            "BAR EndB Plane1 Moment": ("force_cbar", "bending_moment_b1"),
            "BAR EndA Plane2 Moment": ("force_cbar", "bending_moment_a2"),
            "BAR EndB Plane2 Moment": ("force_cbar", "bending_moment_b2"),
            "BAR EndA Pl1 Shear Force": ("force_cbar", "shear_a1"),
            "BAR EndB Pl1 Shear Force": ("force_cbar", "shear_b1"),
            "BAR EndA Pl2 Shear Force": ("force_cbar", "shear_a2"),
            "BAR EndB Pl2 Shear Force": ("force_cbar", "shear_b2"),
            "BAR EndA Axial Force": ("force_cbar", "axial_a"),
            "BAR EndB Axial Force": ("force_cbar", "axial_b"),
            "BAR EndA Torque": ("force_cbar", "torque_a"),
            "BAR EndB Torque": ("force_cbar", "torque_b"),
            "BUSH Force XE": ("force_cbush", "f1"),
            "BUSH Force YE": ("force_cbush", "f2"),
            "BUSH Force ZE": ("force_cbush", "f3"),
            "BUSH Moment XE": ("force_cbush", "m1"),
            "BUSH Moment YE": ("force_cbush", "m2"),
            "BUSH Moment ZE": ("force_cbush", "m3"),
            "BAR EndA Pt1 Comb Stress": ("stress_cbar", "comb_a1"),
            "BAR EndB Pt1 Comb Stress": ("stress_cbar", "comb_b1"),
            "BAR EndA Pt2 Comb Stress": ("stress_cbar", "comb_a2"),
            "BAR EndB Pt2 Comb Stress": ("stress_cbar", "comb_b2"),
            "BAR EndA Pt3 Comb Stress": ("stress_cbar", "comb_a3"),
            "BAR EndB Pt3 Comb Stress": ("stress_cbar", "comb_b3"),
            "BAR EndA Pt4 Comb Stress": ("stress_cbar", "comb_a4"),
            "BAR EndB Pt4 Comb Stress": ("stress_cbar", "comb_b4"),
            "BAR EndA Max Stress": ("stress_cbar", "max_comb_a"),
            "BAR EndB Max Stress": ("stress_cbar", "max_comb_b"),
            "BAR EndA Min Stress": ("stress_cbar", "min_comb_a"),
            "BAR EndB Min Stress": ("stress_cbar", "min_comb_b"),
        },
        "FEMAP": {
            "Total Translation": ("disp", "t_total"),
            "T1 Translation": ("disp", "t1"),
            "T2 Translation": ("disp", "t2"),
            "T3 Translation": ("disp", "t3"),
            "Total Rotation": ("disp", "r_total"),
            "R1 Rotation": ("disp", "r1"),
            "R2 Rotation": ("disp", "r2"),
            "R3 Rotation": ("disp", "r3"),
            "Total Applied Force": ("force_applied", "f_total"),
            "T1 Applied Force": ("force_applied", "f1"),
            "T2 Applied Force": ("force_applied", "f2"),
            "T3 Applied Force": ("force_applied", "f3"),
            "Total Applied Moment": ("force_applied", "m_total"),
            "R1 Applied Moment": ("force_applied", "m1"),
            "R2 Applied Moment": ("force_applied", "m2"),
            "R3 Applied Moment": ("force_applied", "m3"),
            "Total Constraint Force": ("force_reac", "f_total"),
            "T1 Constraint Force": ("force_reac", "f1"),
            "T2 Constraint Force": ("force_reac", "f2"),
            "T3 Constraint Force": ("force_reac", "f3"),
            "Total Constraint Moment": ("force_reac", "m_total"),
            "R1 Constraint Moment": ("force_reac", "m1"),
            "R2 Constraint Moment": ("force_reac", "m2"),
            "R3 Constraint Moment": ("force_reac", "m3"),
            "Total MultiPoint Force": ("multi_point_force", "f_total"),
            "T1 MultiPoint Force": ("multi_point_force", "f1"),
            "T2 MultiPoint Force": ("multi_point_force", "f2"),
            "T3 MultiPoint Force": ("multi_point_force", "f3"),
            "Total MultiPoint Moment": ("multi_point_force", "m_total"),
            "R1 MultiPoint Moment": ("multi_point_force", "m1"),
            "R2 MultiPoint Moment": ("multi_point_force", "m2"),
            "R3 MultiPoint Moment": ("multi_point_force", "m3"),
            "Total Summed GPForce": ("summed_gpf", "f_total"),
            "T1 Summed GPForce": ("summed_gpf", "f1"),
            "T2 Summed GPForce": ("summed_gpf", "f2"),
            "T3 Summed GPForce": ("summed_gpf", "f3"),
            "Total Summed GPMoment": ("summed_gpf", "m_total"),
            "R1 Summed GPMoment": ("summed_gpf", "m1"),
            "R2 Summed GPMoment": ("summed_gpf", "m2"),
            "R3 Summed GPMoment": ("summed_gpf", "m3"),
            "Total Applied GPForce": ("applied_gpf", "f_total"),
            "T1 Applied GPForce": ("applied_gpf", "f1"),
            "T2 Applied GPForce": ("applied_gpf", "f2"),
            "T3 Applied GPForce": ("applied_gpf", "f3"),
            "Total Applied GPMoment": ("applied_gpf", "m_total"),
            "R1 Applied GPMoment": ("applied_gpf", "m1"),
            "R2 Applied GPMoment": ("applied_gpf", "m2"),
            "R3 Applied GPMoment": ("applied_gpf", "m3"),
            "Total Constraint GPForce": ("constraint_gpf", "f_total"),
            "T1 Constraint GPForce": ("constraint_gpf", "f1"),
            "T2 Constraint GPForce": ("constraint_gpf", "f2"),
            "T3 Constraint GPForce": ("constraint_gpf", "f3"),
            "Total Constraint GPMoment": ("constraint_gpf", "m_total"),
            "R1 Constraint GPMoment": ("constraint_gpf", "m1"),
            "R2 Constraint GPMoment": ("constraint_gpf", "m2"),
            "R3 Constraint GPMoment": ("constraint_gpf", "m3"),
            "Bar EndA Plane1 Moment": ("force_cbar", "bending_moment_a1"),
            "Bar EndA Plane2 Moment": ("force_cbar", "bending_moment_a2"),
            "Bar EndB Plane1 Moment": ("force_cbar", "bending_moment_b1"),
            "Bar EndB Plane2 Moment": ("force_cbar", "bending_moment_b2"),
            "Bar EndA Pl1 Shear Force": ("force_cbar", "shear_a1"),
            "Bar EndA Pl2 Shear Force": ("force_cbar", "shear_a2"),
            "Bar EndA Axial Force": ("force_cbar", "axial_a"),
            "Bar EndA Torque": ("force_cbar", "torque_a"),
            "Bar EndA Pt1 Bend Stress": ("stress_cbar", "bend_a1"),
            "Bar EndA Pt2 Bend Stress": ("stress_cbar", "bend_a2"),
            "Bar EndA Pt3 Bend Stress": ("stress_cbar", "bend_a3"),
            "Bar EndA Pt4 Bend Stress": ("stress_cbar", "bend_a4"),
            "Bar EndB Pt1 Bend Stress": ("stress_cbar", "bend_b1"),
            "Bar EndB Pt2 Bend Stress": ("stress_cbar", "bend_b2"),
            "Bar EndB Pt3 Bend Stress": ("stress_cbar", "bend_b3"),
            "Bar EndB Pt4 Bend Stress": ("stress_cbar", "bend_b4"),
            "Bar EndA Axial Stress": ("stress_cbar", "axial_a"),
            "Bar EndA Max Comb Stress": ("stress_cbar", "max_comb_a"),
            "Bar EndA Min Comb Stress": ("stress_cbar", "min_comb_a"),
            "Bar EndB Max Comb Stress": ("stress_cbar", "max_comb_b"),
            "Bar EndB Min Comb Stress": ("stress_cbar", "min_comb_b"),
            "Bar Tension M.S.": ("cbar_ms", "tension"),
            "Bar Compression M.S.": ("cbar_ms", "compression"),
            "Bush X Force": ("force_cbush", "f1"),
            "Bush Y Force": ("force_cbush", "f2"),
            "Bush Z Force": ("force_cbush", "f3"),
            "Bush X Moment": ("force_cbush", "m1"),
            "Bush Y Moment": ("force_cbush", "m2"),
            "Bush Z Moment": ("force_cbush", "m3"),
            "Bush TX Stress": ("cbush_stress", "tx"),
            "Bush TY Stress": ("cbush_stress", "ty"),
            "Bush TZ Stress": ("cbush_stress", "tz"),
            "Bush RX Stress": ("cbush_stress", "rx"),
            "Bush RY Stress": ("cbush_stress", "ry"),
            "Bush RZ Stress": ("cbush_stress", "rz"),
            "Elem C1 T1 GPForce": ("elem_gpf", "c1_f1"),
            "Elem C1 T2 GPForce": ("elem_gpf", "c1_f2"),
            "Elem C1 T3 GPForce": ("elem_gpf", "c1_f3"),
            "Elem C1 R1 GPMoment": ("elem_gpf", "c1_m1"),
            "Elem C1 R2 GPMoment": ("elem_gpf", "c1_m2"),
            "Elem C1 R3 GPMoment": ("elem_gpf", "c1_m3"),
            "Elem C2 T1 GPForce": ("elem_gpf", "c2_f1"),
            "Elem C2 T2 GPForce": ("elem_gpf", "c2_f2"),
            "Elem C2 T3 GPForce": ("elem_gpf", "c2_f3"),
            "Elem C2 R1 GPMoment": ("elem_gpf", "c2_m1"),
            "Elem C2 R2 GPMoment": ("elem_gpf", "c2_m2"),
            "Elem C2 R3 GPMoment": ("elem_gpf", "c2_m3"),
        },
    }
)


class Flavor:
    """Mixin handling neutral self.flavor

    >>> f = Flavor(); f.flavor = "MYSTRAN"  # mocking `self.flavor` attr from `Parser` class
    >>> f.translate("T1 translation")
    ('disp', 't1')
    """

    def translate(self, key):
        """search for initial Neutral vector title `key` in `self.flavor` dict
        >>> f = Flavor(); f.flavor = "MYSTRAN"  # mocking `self.flavor` attr from `Parser` class
        >>> f.translate("T1 translation")
        ('disp', 't1')
        """
        vector, axis = FLAVORS[self.flavor].get(key, (None, None))
        if vector is None:
            logging.warning(f"{key} not found in {self.flavor} dict")
            vector, axis = "?", key
        return vector, axis

    def reverse_translate(self, key):
        """search for `key` in `self.flavor` dict
        >>> f = Flavor(); f.flavor = "MYSTRAN"
        >>> f.reverse_translate(("disp", "t1"))
        'T1 translation'
        >>> f.reverse_translate("disp::t1")
        'T1 translation'
        """
        dic = {v: k for k, v in FLAVORS[self.flavor].items()}
        if isinstance(key, str):
            vector, axis = key.split("::")
        else:
            # assumed a correct tuple was passed
            vector, axis = key
        return dic[(vector, axis)]

    def get_vectors(self, what=None):
        """
        return a list of relevant vectors
        >>> f = Flavor(); f.flavor = "MYSTRAN"
        >>> f.get_vectors("disp")
        ['disp::t_total', 'disp::t1', ...]

        Ommitting key will give access to available vectors families::
        >>> f.get_vectors() == {
        ...                     'disp',
        ...                     'force_applied',
        ...                     'force_reac',
        ...                     'force_cbar',
        ...                     'force_cbush',
        ...                     'stress_cbar'
        ... }
        True
        """
        dic = defaultdict(list)
        for initial_title, (vector, axis) in FLAVORS[self.flavor].items():
            dic[vector].append(axis)
        dic = dict(dic)
        if what is not None:
            return [f"{what}::{t}" for t in dic[what]]
        return set(dic.keys())


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
