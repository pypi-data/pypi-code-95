ATTACK = '-'
SUPPORT = '+'
NEUTRAL = '0'

CRITICAL_SUPPORT = '+!'
CRITICAL_ATTACK = '-!'

WEAK_SUPPORT = '+*'
WEAK_ATTACK = '-*'

NON_SUPPORT = '+~'
NON_ATTACK = '-~'

TRIPOLAR_RELATIONS = [ATTACK, SUPPORT, NEUTRAL]
QUADPOLAR_RELATIONS = [ATTACK, SUPPORT, NEUTRAL, CRITICAL_SUPPORT]


def get_type(val):
    if val > 0:
        return SUPPORT
    elif val < 0:
        return ATTACK
    else:
        return NEUTRAL


def get_relations_set(G, rel=None):
    return set([edge for edge in G.edges if rel is None or G.edges[edge]['type'] == rel])