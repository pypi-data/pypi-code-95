from .QuestionElement import QuestionElement


# Abstraction - base element can be only answer or question;
# 'base' means that users can write comments to that element.
class BaseQuestionElement(QuestionElement):
    Header = 'Answer'
    Comments = []

    # Constructor
    def __init__(self, header, comments, rating):
        self.Header = header
        self.Comments = comments