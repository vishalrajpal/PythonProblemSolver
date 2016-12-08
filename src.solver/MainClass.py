# from corenlp import StanfordCoreNLP
from TestDataSetReader import TestDataSetReader
import json
# from practnlptools.tools import Annotator
import nltk
from QuestionSentencesLabeler import QuestionSentencesLabeler
from spacy.en import English
from AnswerTests import AnswerTests
from PublicKeys import PublicKeys

# corenlp_dir = "/home/niyati/.local/lib/python2.7/stanford-corenlp-full-2016-10-31/"

class MainClass:
    
    if __name__ == '__main__':
#         question_sentences_labeler = QuestionSentencesLabeler()
        # question_sentences_labeler.extract_faulters()
#         PublicKeys.text2int("two")
        answer_tests = AnswerTests()
        answer_tests.test_answers()
#         question_sentences_labeler = QuestionSentencesLabeler()
#         test_dataset_reader = TestDataSetReader()
#         test_dataset_reader.read_test_dataset()
        # corenlp = StanfordCoreNLP(corenlp_dir) # wait a few minutes...
#         test = corenlp.parse("There are 7 crayons on the desk .")
# #         print test
#         print json.loads(test)["sentences"][0]["parsetree"]
#         print '\n'
#         print json.loads(test)["sentences"][0]["indexeddependencies"]
        #         test = corenlp.parse("There are 7 crayons on the desk .")
        # #         print test
        #         print json.loads(test)["sentences"][0]["parsetree"]
        #         print '\n'
        #         print json.loads(test)["sentences"][0]["indexeddependencies"]
        # parser = English()
        # example = u"Dan gave her 10 Pokemon cards. Joan had 5 red balloons. He went to 15 football games this year."
        # parsedEx = parser(example)
        # # shown as: original token, dependency tag, head word, left dependents, right dependents
        # for token in parsedEx:
        #     print(token.orth_, token.dep_, token.head.orth_, [t.orth_ for t in token.lefts], [t.orth_ for t in token.rights])

#         annotator=Annotator()
#         print annotator.getAnnotations("He created the robot and broke it after making it.")['srl']
#         print annotator.getAnnotations("How many games did they win ?")['srl']
#         print annotator.getAnnotations("Sally had 27 Pokemon cards .")['srl']
