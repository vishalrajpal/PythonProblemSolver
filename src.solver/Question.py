from Sentence import Sentence
import json
from collections import OrderedDict
from corenlp import StanfordCoreNLP
from collections import OrderedDict


class Question:

    SCORENLP = StanfordCoreNLP("/Users/rajpav/anaconda2/lib/python2.7/stanford-corenlp-full-2016-10-31")    
    
    def __init__(self, question_json):
        self.m_question_json = question_json    
        self.m_question = self.m_question_json["sQuestion"]    
        self.m_entities = []
        self.m_quantified_entities = OrderedDict()
        self.m_evaluating_sentence = None
        self.m_simplified_question = ""
        self.m_coref_dict = {}
        self.m_proper_nouns = set()
        self.read_sentences()
        
    def extract_corefs(self):
        question_parse = json.loads(Question.SCORENLP.parse(self.m_simplified_question))
#         print question_parse
        if "coref" in question_parse:
            corefs = question_parse["coref"]
            for coref_mappings in corefs:
                print 'coref_mappings'
                print coref_mappings
                for coref_mapping in coref_mappings:
                    print 'coref mapping:'
                    print coref_mapping
                    print coref_mapping[0]
                    print coref_mapping[1]
                    sentence_index = coref_mapping[0][1]
                    print sentence_index
                    src_word = coref_mapping[0][0].lower()
                    print src_word
                    sink_word = coref_mapping[1][0].lower()
                    print sink_word
                    
                    self.m_coref_dict[sentence_index][src_word] = sink_word
            print self.m_coref_dict
        else:
            print 'no corefs'
         
        
    def read_sentences(self):
        
        self.m_sentences = []
        sentences = self.m_question_json["Sentences"]
        sentence_counter = 0;
        for sentence in sentences:
            simplified_sentences = sentence["SimplifiedSentences"]
            for simplified_sentence in simplified_sentences:
                self.m_simplified_question = self.m_simplified_question + simplified_sentence["Sentence"]
                self.m_coref_dict[sentence_counter] = {}
                sentence_counter = sentence_counter + 1;
        self.extract_corefs()
        
        sentence_counter = 0
        for sentence in sentences:
            simplified_sentences = sentence["SimplifiedSentences"]
            for simplified_sentence in simplified_sentences:
#                 print simplified_sentence
                new_sentence = Sentence(simplified_sentence, self, sentence_counter)
                self.m_sentences.append(new_sentence)
                sentence_counter = sentence_counter + 1


    def add_entity(self, entity):
        self.m_entities.append(entity)

    def add_proper_noun(self, noun):
        self.m_proper_nouns.add(noun.lower())

    def add_quantified_entity(self, quantified_entity):
        quantity_exists = self.quantified_entity_exists(quantified_entity)
        print 'quantity_exists?'
        print quantity_exists
        if not quantity_exists:
            owner_entity = quantified_entity.get_owner_entity()
            self.m_quantified_entities[owner_entity.get_name()].append(quantified_entity)            
        return quantity_exists
        
    def quantified_entity_exists(self, quantified_entity):
        print quantified_entity
        print 'existing qes'
        for k, v in self.m_quantified_entities.items():
                for e in v:
                    print "{} -> {} {}".format(k, e.m_cardinal, e.m_object)
        owner_entity = quantified_entity.get_owner_entity()
        quantified_entity_exists = False
        owner_entity_name = owner_entity.get_name()
        print owner_entity_name
        if owner_entity_name in self.m_quantified_entities:
            owner_quantified_entities = self.m_quantified_entities[owner_entity_name]
            print owner_quantified_entities
            for owner_quantified_entity in owner_quantified_entities:
                print owner_quantified_entity
                print quantified_entity
                print quantified_entity.get_name()
                if owner_quantified_entity.get_name() == quantified_entity.get_name():
                    quantified_entity_exists = True
        else:
            self.m_quantified_entities[owner_entity_name] = []
        return quantified_entity_exists

    def set_evaluating_sentence(self, sentence):
        print 'In set evaluating sentence'
        self.m_evaluating_sentence = sentence

    def get_entities(self):
        return self.m_entities

    def get_quantified_entities(self):
        return self.m_quantified_entities

    def get_quantified_entity_objects(self):
        qe_objects = set()
        for v in self.m_quantified_entities.values():
            for e in v:
                qe_objects.add(e.m_object)
        return qe_objects

    def solve(self):
        print "In Solve"
        for sentence in self.m_sentences:
            sentence.parse_sentence()
        
        if (self.m_evaluating_sentence != None):
            print self.m_quantified_entities.keys()
            print self.m_quantified_entities.values()
            for k, v in self.m_quantified_entities.items():
                for e in v:
                    print e         
#             print self.m_evaluating_sentence.extract_result()
        else:
            print 'I don\'t have an evaluating sentence!'