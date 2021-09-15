from Base import BaseQuestionElement


# Abstraction - question that user have asked.
class Question(BaseQuestionElement):
    BestAnswer = None
    SelectedAnswer = None
    Tags = []
    Answers = []
    Link = ''
