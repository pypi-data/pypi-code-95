from django.test import TestCase
from questions.models import Question


class QuestionTest(TestCase):
    def setUp(self):
        Question.objects.create(title="fi")
