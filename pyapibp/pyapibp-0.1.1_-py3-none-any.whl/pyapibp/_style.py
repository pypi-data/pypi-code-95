from PyInquirer import Token, style_from_dict

STYLE = style_from_dict({
    Token.QuestionMark: '#E91E63 bold',
    Token.Selected: '#673AB7 bold',
    Token.Instruction: '',
    Token.Answer: '#2196F3',
    Token.Question: '#FFB333',
})
