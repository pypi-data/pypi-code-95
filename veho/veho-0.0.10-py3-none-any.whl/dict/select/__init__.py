def select_values(lex, *keys):
    return [lex[k] if k in lex else None for k in keys]
