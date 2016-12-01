from corenlp import StanfordCoreNLP
from TestDataSetReader import TestDataSetReader
import json
from practnlptools.tools import Annotator
import nltk
from QuestionSentencesLabeler import QuestionSentencesLabeler

corenlp_dir = "stanford-corenlp-full-2016-10-31/"

class MainClass:
    
    if __name__ == '__main__':
#         question_sentences_labeler = QuestionSentencesLabeler()
        test_dataset_reader = TestDataSetReader()
        test_dataset_reader.read_test_dataset()
#         corenlp = StanfordCoreNLP(corenlp_dir) # wait a few minutes...
#         test = corenlp.parse("There are 7 crayons on the desk .")
# #         print test
#         print json.loads(test)["sentences"][0]["parsetree"]
#         print '\n'
#         print json.loads(test)["sentences"][0]["indexeddependencies"]

#         annotator=Annotator()
#         print annotator.getAnnotations("He created the robot and broke it after making it.")['srl']
#         print annotator.getAnnotations("How many games did they win ?")['srl']
#         print annotator.getAnnotations("Sally had 27 Pokemon cards .")['srl']