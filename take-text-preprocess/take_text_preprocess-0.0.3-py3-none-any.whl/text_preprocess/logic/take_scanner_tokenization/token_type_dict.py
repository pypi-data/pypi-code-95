from scanner.lexycal.token_type import TokenType

TOKEN_TYPES = {
    TokenType.CPF: 'DOC',
    TokenType.CNPJ: 'DOC',
    TokenType.CEP: 'CEP',
    TokenType.PHONE1: 'PHONE',
    TokenType.INTEGER: 'NUMBER',
    TokenType.NUMBER: 'NUMBER',
    TokenType.NUMBERWITHDOT: 'NUMBER',
    TokenType.ORDINAL: 'NUMBER',
    TokenType.CODE: 'CODE',
}
