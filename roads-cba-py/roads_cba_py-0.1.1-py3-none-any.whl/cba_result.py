import json

from numpy import isnan
from schematics import Model
from schematics.types import StringType, FloatType, ListType


class CbaResult(Model):
    orma_way_id = StringType(max_length=20, min_length=1)
    work_class = StringType(required=True, min_length=1)
    work_type = StringType(required=True, min_length=1)
    work_name = StringType(required=True, min_length=1)
    work_cost = FloatType(required=True)
    work_cost_km = FloatType(required=True)
    work_year = FloatType(required=True)
    npv = FloatType(required=True)
    npv_km = FloatType(required=True)
    npv_cost = FloatType(required=True)
    eirr = FloatType(required=True)
    aadt = ListType(FloatType, required=True, min_size=20, max_size=20)
    truck_percent = FloatType(required=True)
    vehicle_utilization = FloatType(required=True)
    esa_loading = FloatType(required=True)
    iri_projection = ListType(FloatType, required=True, min_size=20, max_size=20)
    iri_base = ListType(FloatType, required=True, min_size=20, max_size=20)
    con_projection = ListType(FloatType, required=True, min_size=20, max_size=20)
    con_base = ListType(FloatType, required=True, min_size=20, max_size=20)
    financial_recurrent_cost = ListType(FloatType, required=True, min_size=20, max_size=20)
    net_benefits = ListType(FloatType, required=True, min_size=20, max_size=20)

    def __repr__(self):
        return str(self.to_primitive())

    @classmethod
    def from_file(cls, filename):
        with open(filename) as f:
            return CbaResult(json.load(f))

    def to_dict(self):
        rv = {
            "orma_way_id": self.orma_way_id,
            "work_class": self.work_class,
            "work_type": self.work_type,
            "work_name": self.work_name,
            "work_cost": self.work_cost,
            "work_cost_km": self.work_cost_km,
            "work_year": self.work_year,
            "npv": self.npv,
            "npv_km": self.npv_km,
            "npv_cost": self.npv_cost,
            "eirr": self.eirr,
            "truck_percent": self.truck_percent,
            "vehicle_utilization": self.vehicle_utilization,
            "esa_loading": self.esa_loading,
        }

        rv.update({f"aadt_{i + 1}": self.aadt[i] for i in range(0, len(self.aadt))})
        rv.update({f"iri_base_{i + 1}": self.iri_base[i] for i in range(0, len(self.iri_base))})
        rv.update({f"iri_projection_{i + 1}": self.iri_projection[i] for i in range(0, len(self.iri_projection))})
        rv.update({f"con_projection_{i + 1}": self.con_projection[i] for i in range(0, len(self.con_projection))})
        rv.update({f"con_base_{i + 1}": self.con_base[i] for i in range(0, len(self.con_base))})
        rv.update({f"net_benefits_{i + 1}": self.net_benefits[i] for i in range(0, len(self.net_benefits))})
        rv.update(
            {
                f"financial_recurrent_cost_{i + 1}": self.financial_recurrent_cost[i]
                for i in range(0, len(self.financial_recurrent_cost))
            }
        )

        return rv

    def compare(self, other):
        a = self.to_dict()
        b = other.to_dict()

        def comparison(x, y):
            eq = "==" if x == y else "!="
            if isinstance(x, str) or isinstance(y, str):
                return f"{x: >20} {eq} {y: >20}"
            if isnan(x) and isnan(y):
                return 0
            if abs(x - y) < 0.000001:
                return 0
            return x - y

        keys = set.intersection(set(a.keys()), set(b.keys()))
        return {k: comparison(a[k], b[k]) for k in sorted(list(keys))}
