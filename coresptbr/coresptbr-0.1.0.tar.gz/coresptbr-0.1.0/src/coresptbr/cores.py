def colorir(n='', c1='', c2='', c3='', fechar=True):
    '''
    Função que formata um valor (string ou não) para sequência de escape ANSI.
    n: Valor a ser formatado.
    c1, c2, c3: Códigos ANSI a serem formatados.
    fechar: parâmetro que determina se a sequência de escape vale somente para
    o valor n.
    '''
    s1, s2 = str(), str()
    try:
        c1, c2, c3 = cores[c1], cores[c2], cores[c3]
    except KeyError:
        c1 = c2 = c3 = ''
    if c1 == '' == c2 == '' == c3:
        return n
    if c1 != '' != c2 or c2 != '' != c3 or c1 != '' != c3:
        s1 = ';'
    if c1 != '' != c2 and c3 != '':
        s2 = ';'
    try:
        res = f'\033[{c1}{s1}{c2}{s2}{c3}m{n}'
        if fechar:
            res += '\033[m'
    except KeyError:
        return n
    return res


'''
    É possível deduzir o nome das cores, basta colocar as primeiras três letras.
    Branco -> 'bra', Amarelo -> 'ama' e assim por diante.
    Vermelho e Verde são 'vm' e 'vd' por terem as mesmas três letras iniciais,
    e Azul é 'azul' por ter poucas letras.
    Para cores claras basta adicionar um 'c' na frente do nome da cor
    (Amarelo-claro -> 'amac').
    Para colocar o fundo de uma cor basta adicionar um 'f' antes.
    (Fundo verde -> 'fvd', Fundo preto-claro -> fprec)
'''

cores = {
    '': '',
    'neg': '1',      # Negrito
    'fraco': '2',    # Fraco
    'ita': '3',      # Itálico
    'sub': '4',      # Sublinhado
    'pis': '5',      # Piscar
    'inv': '7',      # Inverter
    'pre': '30',     # Preto
    'vm': '31',      # Vermelho
    'vd': '32',      # Verde
    'ama': '33',     # Amarelo
    'azu': '34',     # Azul
    'mag': '35',     # Magenta
    'cia': '36',     # Ciano
    'bra': '37',     # Branco
    'prec': '90',    # Preto-claro
    'vmc': '91',     # Vermelho-claro
    'vdc': '92',     # Verde-claro
    'amac': '93',    # Amarelo-claro
    'azuc': '94',    # Azul-claro
    'magc': '95',    # Magenta-claro
    'ciac': '96',    # Ciano-claro
    'brac': '97',    # Branco-claro, (existe)
    'fpre': '40',    # Fundo preto
    'fvm': '41',     # Fundo vermelho
    'fvd': '42',     # Fundo verde
    'fama': '43',    # Fundo amarelo
    'fazu': '44',    # Fundo azul
    'fmag': '45',    # Fundo magenta
    'fcia': '46',    # Fundo ciano
    'fbra': '47',    # Fundo branco
    'fprec': '100',  # Fundo preto-claro
    'fvmc': '101',   # Fundo vermelho-claro
    'fvdc': '102',   # Fundo verde-claro
    'famac': '103',  # Fundo amarelo-claro
    'fazuc': '104',  # Fundo azul-claro
    'fmagc': '105',  # Fundo magenta-claro
    'fciac': '106',  # Fundo ciano-claro
    'fbrac': '107'   # Fundo branco-claro
}
