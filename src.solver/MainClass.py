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
        # question_sentences_labeler = QuestionSentencesLabeler()
        # question_sentences_labeler.relabel_questions([163, 168, 179, 183, 184, 185, 186, 188, 191, 192, 195, 196, 197, 199, 200, 201, 203, 204, 205, 206, 207, 210, 211, 212, 213, 214, 215, 217, 218, 219, 220, 221, 222, 223, 224, 225, 230, 231, 232, 233, 235, 236, 237, 238, 239, 244, 245, 246, 247, 249, 250, 251, 252, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 271, 272, 273, 274, 194])
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
