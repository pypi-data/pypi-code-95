from itertools import product
from pandas import DataFrame, Index, MultiIndex
from pgmpy.factors.discrete import TabularCPD

from probability.discrete._old.cpt import CPT
from probability.discrete._old.joint import Joint

grades_data = [[0.1, 0.1, 0.1, 0.2, 0.2, 0.2],
               [0.1, 0.2, 0.3, 0.2, 0.3, 0.4],
               [0.8, 0.7, 0.6, 0.6, 0.5, 0.4]]

p = Joint.from_dict({
    ('blue', 'apple'): 1 / 4,
    ('blue', 'orange'): 1 / 6,
    ('red', 'apple'): 1 / 12,
    ('red', 'orange'): 1 / 2
}, variables=['box', 'fruit'])
jpd = p.jpd
x = jpd.conditional_distribution([('box', 0)], inplace=False)
y = jpd.conditional_distribution([('box', 1)], inplace=False)

difficulty_cpd = TabularCPD('difficulty', 2, [[0.2], [0.8]])
intelligence_cpd = TabularCPD('intelligence', 3, [[0.5], [0.3], [0.2]])
grade_cpd = TabularCPD(
    variable='grade', variable_card=3,
    values=grades_data,
    evidence=['difficulty', 'intelligence'],
    evidence_card=[2, 3]
)

grade_data = DataFrame(
    data=grades_data,
    columns=MultiIndex.from_tuples(
        tuples=product(['easy', 'hard'], ['low', 'medium', 'high']),
        names=['difficulty', 'intelligence']
    ),
    index=Index(data=['C', 'B', 'A'], name='grade')
)

grade_cpt = CPT.from_data_frame(grade_data)
