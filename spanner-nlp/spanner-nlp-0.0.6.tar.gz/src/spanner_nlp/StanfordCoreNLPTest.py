from StanfordCoreNLP import StanfordCoreNLP
import logging
import json

# Annotators wrapper - Simple Usage - Using local files
with StanfordCoreNLP('stanford-corenlp-4.1.0', quiet=False, loggingLevel=logging.DEBUG) as nlp:
    print("------------------------------------------------------------")
    print('Tokenize:', json.dumps(nlp.tokenize("Hello world. Hello world again."), indent=4))
    # print('Cleanxml:', nlp.cleanxml("<xml>Stanford University is located in California. It is a great university.</xml>"))
    # print('Sentence Splitting:', json.dumps(nlp.ssplit("Hello world. Hello world again."), indent = 4))
    # print('Part of Speech:', json.dumps(nlp.pos("Marie was born in Paris."), indent = 4))
    # print('Lemma:', nlp.lemma("Marie was born in Paris."))
    # print('Named Entities:', nlp.ner("Joe Smith lives in California. He used to live in Oregon."))
    # print('Entity Mentions:', nlp.entitymentions("Joe Smith lives in California. He used to live in Oregon."))
    # print('TokensRegexNERAnnotator:', nlp.regexner("Joe Smith lives in California. He used to live in Oregon.", "Oregon", True))
    # print('TokensRegex:', nlp.tokensregex("She has worked at Miller Corp. for 5 years.", '[{word:"Miller"}]'))
    # print('Tregex:', nlp.tregex("Joe Smith lives in California. Joe is going to school. He arrived to the game.", '/[A-Z][A-Za-z]+/', True))
    # print('Semgrex:', nlp.semgrex("Joe Smith lives in California. Joe is going to school. He arrived to the game.", '{tag: NNP}'))
    # print('Constituency Parsing:', nlp.parse("The small red car turned very quickly around the corner."))
    # print('Dependency Parsing:', nlp.dependency_parse("The small red car turned very quickly around the corner."))
    # print('Coreference Resolution:', nlp.coref("Barack Obama was born in Hawaii.  He is the president. Obama was elected in 2008."))
    # print('OpenIE:', nlp.openie("Obama was born in Hawaii. He is our president."))
    # print('KBP:', nlp.kbp("Joe Smith was born in Oregon."))
    # print('Quote Extraction And Attribution:', nlp.quote("In the summer Joe Smith decided to go on vacation.  He said, \"I'm going to Hawaii.\"  That July, vacationer Joe went to Hawaii."))
    # print('Sentiment:', nlp.sentiment("Joe Smith was born in Oregon."))
    # print('TrueCaseAnnotator:', nlp.truecase("lonzo ball talked about kobe bryant after the lakers game."))
    # print('Universal Dependencies:', nlp.udfeats("lonzo ball talked about kobe bryant after the lakers game."))
    print("------------------------------------------------------------")

'''
#Manual Annotators - Using local files
nlp = StanfordCoreNLP('stanford-corenlp-4.1.0', lang = 'en')
text = 'The small red car turned very quickly around the corner.'
#pros = {'annotators' : 'pos', 'pinelineLanguage' : 'en', 'outputFormat' : 'JSON'} #Part of Speech example
pros = {'annotators' : 'ner', 'pinelineLanguage' : 'en', 'outputFormat' : 'XML'} #Named Entity Recognition example
print(nlp.annotate(text, pros))
nlp.close()
'''
# '''
# Manual Annotators - Using existing server
nlp = StanfordCoreNLP('http://corenlp.run', port=80)
text = 'Joe Smith lives in California. He used to live in Oregon.'
# pros = {'annotators' : 'tokenize, ssplit', 'pinelineLanguage' : 'en', 'outputFormat' : 'XML'} #Sentence Splitting example
pros = {'annotators': 'lemma', 'pinelineLanguage': 'en', 'outputFormat': 'JSON'}  # Lemmatization example
print(nlp.annotate(text, pros))
nlp.close()
# '''
'''
#Manual Annotators - Support a number of annotators at the same time - Using local files
nlp = StanfordCoreNLP('stanford-corenlp-4.1.0', lang = 'en')
text = 'Joe Smith lives in California. He used to live in Oregon.'
pros = {'annotators' : 'tokenize, ssplit, pos', 'pinelineLanguage' : 'en', 'outputFormat' : 'JSON'}
print(json.dumps(nlp.annotate(text, pros, True), indent = 4))
nlp.close()
'''
