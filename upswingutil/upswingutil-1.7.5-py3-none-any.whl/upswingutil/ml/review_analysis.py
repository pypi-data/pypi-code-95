# from textblob import TextBlob
# from rake_nltk import Rake
#
#
# class ReviewAnalysis:
#
#     def __init__(self, text):
#         self.text = text
#
#     def sentiment(self):
#         edu = TextBlob(self.text)
#         x = edu.sentiment.polarity
#         if x < 0:
#             return 'Negative'
#         elif x == 0:
#             return 'Neutral'
#         elif x > 0 and x <= 1:
#             return 'Positive'
#
#     def keywords(self):
#         r = Rake(min_length=2, max_length=4)
#         r.extract_keywords_from_text(self.text)
#         return r.get_ranked_phrases()
#
#