from corenlp import StanfordCoreNLP
from TestDataSetReader import TestDataSetReader
import json

corenlp_dir = "stanford-corenlp-full-2016-10-31/"

class MainClass:
    
    if __name__ == '__main__':
        test_dataset_reader = TestDataSetReader()
        test_dataset_reader.read_test_dataset()
#         corenlp = StanfordCoreNLP(corenlp_dir) # wait a few minutes...
#         test = corenlp.parse("How many apples does Joan have?")
#         print test
#         print json.loads(test)["sentences"][0]["parsetree"]
