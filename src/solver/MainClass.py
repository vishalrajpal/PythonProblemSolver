from corenlp import StanfordCoreNLP
corenlp_dir = "stanford-corenlp-full-2016-10-31/"

class MainClass:
    
    if __name__ == '__main__':
        corenlp = StanfordCoreNLP(corenlp_dir) # wait a few minutes...
        print corenlp.raw_parse("Parse it")
