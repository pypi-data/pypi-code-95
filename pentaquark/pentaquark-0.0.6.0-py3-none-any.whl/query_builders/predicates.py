import enum

from pentaquark.constants import SEPARATOR, START_NODE_ALIAS
from pentaquark.exceptions import PentaQuarkConfigurationError
from pentaquark.lookups import LOOKUP_REGISTRY
from pentaquark.query_builders.pattern_builder import PatternBuilder


class LogicalOperators(enum.Enum):
    AND = "AND"
    OR = "OR"


class AbsC:
    def __and__(self, other):
        return CompositeC(self, other, LogicalOperators.AND)

    def __or__(self, other):
        return CompositeC(self, other, LogicalOperators.OR)

    def compile(self, model, param_store, variables=None):
        raise NotImplementedError()


class CompositeC(AbsC):
    def __init__(self, c1, c2, operator):
        """
        :param c: a dict with a single first-level key (AND or OR).
        """
        op = LogicalOperators(operator)
        self._conditions = {
            op: [c1, c2]
        }

    def compile(self, model, param_store, variables=None):
        res = ""
        for k, cs in self._conditions.items():
            q = []
            op = k.name
            for c in cs:
                q.append(c.compile(model, param_store, variables))
            res += "(" + f" {op} ".join(q) + ")"
        return res


class C(AbsC):
    """
    Constructors:

        C(x__gt=1)  # C, Exists
        C(x, y)  # Label

    """
    def __init__(self, **kwargs):
        if len(kwargs) > 1:
            raise Exception("only one kwarg accepted in C init (received: %s)", kwargs)
        if len(kwargs) == 1:
            self.variable, self.value = next(iter(kwargs.items()))
            # FIXME: let us filter on variables added to the scope through other means
            #   not necessarily attached to 'this'
            if not self.variable.startswith(START_NODE_ALIAS):
                self.variable = START_NODE_ALIAS + SEPARATOR + self.variable

    def compile(self, model, param_store, variables=None):
        return self.to_cypher(model, param_store, variables)

    def _to_cypher(self, lhs, lookups, value, param_store, variables=None):
        lookup_klasses = list(reversed(lookups))
        for lookup_klass in lookup_klasses[:-1]:
            lookup = lookup_klass()
            lhs = lookup.to_cypher(lhs, None, param_store=param_store)
            value = lookup.convert_value(value)
        lookup = lookup_klasses[-1]()
        lhs = lookup.to_cypher(lhs, value, param_store=param_store)
        return lhs

    def _extract_var_lookup_and_prop(self, variables=None):
        """From the string in self.variable, extract the Cypher alias, property and lookup if any.

        Several configurations are possible:
        - this => only one variable, no prop nor lookup => default to 'eq' lookup
        - this__title => var and prop but no lookup => default to 'eq' lookup
        - this__title__lt => var, prop and lookup
        :param variables:
        :return:
        """
        var, prop = self.variable.rsplit(SEPARATOR, 1)
        lookups = []
        prev_var = var
        while prop in LOOKUP_REGISTRY:
            lookup_kls = LOOKUP_REGISTRY[prop]
            lookups.append(lookup_kls)
            if SEPARATOR in var:
                var, prop = var.rsplit(SEPARATOR, 1)
            else:
                var = prev_var
                prop = ""
            prev_var = var
        if not lookups:
            lookup_kls = LOOKUP_REGISTRY["eq"]
            lookups.append(lookup_kls)
        return var, lookups, prop

    def to_cypher(self, model, param_store, variables=None):
        # this can not happen for now, since we are forcing the this__ prefix
        # if SEPARATOR not in self.variable:
        #     if variables is not None and self.variable not in variables:
        #         raise Exception(f"Can not filter on {self.variable} not in scope {variables}")
        #     eq_lookup = LOOKUP_REGISTRY["eq"]()
        #     return self._to_cypher(self.variable, eq_lookup, self.value, param_store)
        var, lookup_kls, prop = self._extract_var_lookup_and_prop(variables)
        # lookup = lookup_kls()
        if variables is not None and var not in variables:
            raise Exception(f"Can not filter on {var} not in scope {variables}")
        prop = f"{var}.{prop}" if prop else var
        return self._to_cypher(prop, lookup_kls, self.value, param_store)


class Label(C):
    # Label("this", "Movie")
    # value=Movie, variable=this
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value
        if not self.variable.startswith(START_NODE_ALIAS):
            self.variable = START_NODE_ALIAS + SEPARATOR + self.variable
        super().__init__()

    def to_cypher(self, model, param_store, variables=None):
        if variables and self.variable not in variables:
            raise Exception(f"Can not filter on {self.variable} not in scope {variables}")
        lookup = LOOKUP_REGISTRY["label"]()
        return lookup.to_cypher(self.variable, self.value, param_store)


class Exists(C):
    """
    "EXISTS" Cypher predicate function, with pattern argument
    TODO: support for pattern without attributes, ie we need to be able to build the pattern from a string:
        eg: "movies__director" or "attribute_instance__attribute"
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        q = None
        if args and kwargs:
            raise PentaQuarkConfigurationError("Exists predicate only understand either args or kwargs")
        if args:
            if len(args) > 1:
                raise PentaQuarkConfigurationError(
                    "Exists predicate only understand one single argument. "
                    "Use several Exists if several conditions are required."
                )
            q = args[0]
        elif kwargs:
            q = kwargs
        self._queries = q

    def _get_pattern(self, model, param_store, variables):
        pb = PatternBuilder(
            model=model, param_store=param_store,
            variables_in_external_scope=variables,
            append_to_global_scope=False,
        )
        return pb.build(data=self._queries, include_alias=False, include_label=True)

    def to_cypher(self, model, param_store, variables=None):
        pattern = self._get_pattern(model, param_store, variables)
        return f"EXISTS({pattern})"


class Not(C):
    """Predicate Negation"""
    def __init__(self, c):
        super().__init__()
        self._c = c

    def to_cypher(self, model, param_store, variables=None):
        return f"NOT ({self._c.to_cypher(model, param_store, variables)})"
