from Base import BaseQuestionElement, QuestionElement

# Abstraction - answer on question
class Answer(BaseQuestionElement):

    # Calculated fields
    GeneralRating = 0
    IsSelectedByUser = False
    ########################

# Abstraction - question that user have asked.
class Question(BaseQuestionElement):
    BestAnswer = None
    SelectedAnswer = None
    Tags = []
    Answers = []
    Link = ''

# Abstraction - comment for question or answer.
class Comment(QuestionElement):
    TargetAnswer = None
