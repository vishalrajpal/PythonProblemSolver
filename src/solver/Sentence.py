from corenlp import StanfordCoreNLP
import json
import re
from QuantifiedEntity import QuantifiedEntity
from Entity import Entity

class Sentence:

    SCORENLP = StanfordCoreNLP("stanford-corenlp-full-2016-10-31/")
    PATTERN = re.compile('(\[{1})([a-zA-Z0-9.= ]+)(\]{1})')
    STRING_TO_DICT_PATTERN = re.compile(r'(\S+)=(".*?"|\S+)')
 
    def __init__(self, sentence_json, question):
        self.m_predicted_label = sentence_json["PredictedLabel"]
        self.m_sentence_text = sentence_json["Sentence"]
        self.m_has_a_cardinal = False
        self.m_cardinal = None
        self.m_has_a_dobj = False
        self.m_dobj = None
        self.m_has_a_nsubj = False
        self.m_nsubj = None
        self.m_quantified_entity = None
        self.m_owner_entity = None
        self.m_object_entity = None
        self.m_evaluating_subject = None
        self.m_evaluating_object = None
        self.m_question = question
        print self.m_predicted_label
        if self.m_predicted_label == '?':
            self.m_question.m_evaluating_sentence = self
        print self.m_question.m_evaluating_sentence
        
    def __str__(self):
        return self.m_sentence_text
    
    def parse_sentence(self):
        self.extract_dependencies()
        if self.m_predicted_label == '?':
            self.extract_evaluation_entities()
        else:
            self.extract_entities()

    def extract_dependencies(self):
        print 'in extract dep'
        corenlp_result = json.loads(Sentence.SCORENLP.parse(self.m_sentence_text))
        current_sentence = corenlp_result["sentences"][0]
        parse_tree = current_sentence["parsetree"]
        matched_tuples = Sentence.PATTERN.findall(parse_tree)
        for matched_tuple in matched_tuples:
            matched_tuple_dict = dict(Sentence.STRING_TO_DICT_PATTERN.findall(matched_tuple[1]))
            part_of_speech = matched_tuple_dict["PartOfSpeech"]
            if part_of_speech == 'CD':
                self.m_has_a_cardinal = True
                self.m_cardinal = int(matched_tuple_dict["Text"])
        self.m_dependencies = current_sentence["dependencies"]

    def extract_entities(self):
        print 'in extract entities'
        for dependency in self.m_dependencies:
            if dependency[0] == 'nsubj':
                self.m_has_a_nsubj  = True
                self.m_nsubj = dependency[2]
                self.m_owner_entity = Entity('nsubj', self.m_nsubj)
            elif dependency[0] == 'dobj':
                self.m_has_a_dobj = True
                self.m_dobj = dependency[2]
                if self.m_cardinal != None:                    
                    if self.m_owner_entity != None:
                        temp_quantified_entity = QuantifiedEntity(self.m_cardinal, 'dobj', self.m_dobj)
                        temp_quantified_entity.set_owner_entity(self.m_owner_entity)                                                    
                        to_merge_entities = self.m_question.add_quantified_entity(temp_quantified_entity)
                        print 'to merge?' 
                        print to_merge_entities
                        if to_merge_entities:
                            self.merge_entities(temp_quantified_entity)
                        else:
                            self.m_quantified_entity = temp_quantified_entity
                else:
                    self.m_object_entity = Entity('dobj', self.m_dobj)
                    
    def extract_evaluation_entities(self):
        print 'In extract evaluating entities'
        for dependency in self.m_dependencies:
            if dependency[0] == 'nsubj':
                self.m_has_a_nsubj  = True
                self.m_nsubj = dependency[2]
                self.m_evaluating_subject = Entity('nsubj', self.m_nsubj)
            elif dependency[0] == 'dobj':
                self.m_has_a_dobj = True
                self.m_dobj = dependency[2]
                self.m_evaluating_object = Entity('dobj', self.m_dobj)
                
    def extract_result(self):
        quantified_entities = self.m_question.get_quantified_entities()
        subjects_object_entity = quantified_entities[self.m_evaluating_subject.get_name()]
        if subjects_object_entity.get_name() == self.m_evaluating_object.get_name():
            result = subjects_object_entity
        return result
    
    def merge_entities(self, temp_quantified_entity):
        print "in merge"
        quantified_entities = self.m_question.get_quantified_entities()
        subject = temp_quantified_entity.get_owner_entity().get_name()
        sentence_output = self.output(True)
        print sentence_output
        quantified_entities[subject].perform_operation(sentence_output)
        print self.m_question.get_quantified_entities()[subject]
        
    def output(self, ret_math_value):
        if ret_math_value:
            print 'in ret'
            if self.m_cardinal != None:
                sign = 1;
                if self.m_predicted_label == '-':
                    sign = -1
            print sign
            print self.m_cardinal
            print sign * self.m_cardinal
            output = sign * self.m_cardinal
            print output
        else:    
            if self.m_predicted_label == '+' or self.m_predicted_label == '-':
                if self.m_cardinal != None:
                    output = self.m_predicted_label + ' ' + self.m_quantified_entity
                else:
                    output = self.m_predicted_label + ' ' + 'X'
        print 'final out'
        print output
        return output
        