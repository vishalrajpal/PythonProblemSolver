from corenlp import StanfordCoreNLP
import json
import re
from QuantifiedEntity import QuantifiedEntity
from Entity import Entity
from collections import OrderedDict
from PublicKeys import PublicKeys
from nltk.corpus import wordnet as wn
from LemmatizerModule import LemmatizerModule

class Sentence:

    SCORENLP = StanfordCoreNLP("stanford-corenlp-full-2016-10-31/")
    PATTERN = re.compile('(\[{1})([a-zA-Z0-9.= $_<>\"\/?]+)(\]{1})')
    STRING_TO_DICT_PATTERN = re.compile(r'(\S+)=(".*?"|\S+)')
    SINGULAR_PRONOUN = ['he', 'she', 'it', 'him', 'her', 'his']
    SINGULAR_SUBJECT_PRONOUN = ['he', 'she', 'him', 'her', 'his']
    SINGULAR_OBJECT_PRONOUN = ['it']
    PLURAL_PRONOUN = ['they', 'them']
    LEMMATIZER_MODULE = LemmatizerModule()
 
    def __init__(self, sentence_json, question):
        self.m_predicted_label = sentence_json["PredictedLabel"]
        self.m_sentence_text = sentence_json["Sentence"]
        self.m_syntactic_pattern = sentence_json["SyntacticPattern"]
        print self.m_sentence_text
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
        self.m_has_a_pronoun = False
        self.m_processed_pronoun = None
        self.m_transfer_entity = None
        self.m_transfer_quantified_entity = None
        self.m_all_pronouns = []
        self.m_all_nouns = []
        self.m_all_noun_lemmas = []
        self.m_question = question
        self.m_words_pos = OrderedDict()
        self.m_is_first_word_an_expletive = True if self.m_syntactic_pattern[0] == 'E' else False
        print self.m_predicted_label
        if self.m_predicted_label == '?':
            self.m_question.m_evaluating_sentence = self
        
    def __str__(self):
        return self.m_sentence_text
    
    def parse_sentence(self):
        self.extract_dependencies()
        self.process_pronouns()
        if self.m_predicted_label == '?':
            self.extract_evaluation_entities()
        else:
            self.extract_entities()

    def extract_dependencies(self):
        print 'in extract dep'
        print self.m_sentence_text
        corenlp_result = json.loads(Sentence.SCORENLP.parse(self.m_sentence_text))
        current_sentence = corenlp_result["sentences"][0]
        parse_tree = current_sentence["parsetree"]
        self.m_dependencies = current_sentence["dependencies"]
        self.m_matched_tuples = Sentence.PATTERN.findall(parse_tree)
        for matched_tuple in self.m_matched_tuples:
            matched_tuple_dict = dict(Sentence.STRING_TO_DICT_PATTERN.findall(matched_tuple[1]))
            parts_of_speech = matched_tuple_dict["PartOfSpeech"]
            word = matched_tuple_dict["Text"]
            self.m_words_pos[word] = parts_of_speech            
            if parts_of_speech in PublicKeys.NOUN_POS:
                self.m_all_noun_lemmas.append(matched_tuple_dict["Lemma"])
                self.m_all_nouns.append(word)
            if parts_of_speech == 'CD':
                self.m_has_a_cardinal = True
                self.m_cardinal = int(word)
                if self.m_predicted_label == '-':
                    self.m_cardinal = -self.m_cardinal
            elif parts_of_speech == 'PRP' or parts_of_speech == 'PRP$':
                print 'found pronoun'
                self.m_has_a_pronoun = True
                self.m_all_pronouns.append(matched_tuple_dict)
        
        
        
    def extract_entities(self):
        print 'in extract entities'
        if self.m_is_first_word_an_expletive == True:
            self.extract_entities_based_on_expletive()
        else:
            self.extract_normal_entities()

    def extract_entities_based_on_expletive(self):
        for dependency in self.m_dependencies:
            relation = dependency[0]
            # nsubj-- object either or  nummod-- object , subject nmod:in, nmod:on, nmod:with            
            if relation == 'nsubj':
                self.m_has_a_dobj = True
                self.m_dobj = dependency[2]
            elif relation == 'nummod' and self.m_has_a_dobj == False:
                self.m_has_a_dobj = True
                self.m_dobj = dependency[2]
            elif relation == 'nmod:in' or relation == 'nmod:on' or relation == 'nmod:with':
                self.m_has_a_nsubj  = True
                self.m_nsubj = dependency[2]
                self.m_owner_entity = Entity('nsubj', self.m_nsubj)
        self.extract_quantified_entities(False, None)
            
    def extract_normal_entities(self):
        transfer_entity_relation = None
        for dependency in self.m_dependencies:
            relation = dependency[0]
            if relation == 'nsubj':
                self.m_has_a_nsubj  = True
                self.m_nsubj = dependency[2]
                self.m_owner_entity = Entity('nsubj', self.m_nsubj)
            elif relation == 'dobj':
                self.m_has_a_dobj = True
                self.m_dobj = dependency[2]
            elif relation == 'nmod:to' or relation == 'nmod:from' or relation == 'nmod:poss' or relation == 'iobj':
                transfer_entity_relation = relation                                    
                if self.m_has_a_pronoun:
                    self.m_transfer_entity = Entity(relation, unicode(self.m_processed_pronoun, "utf-8"))
                else:
                    self.m_transfer_entity = Entity(relation, dependency[2])
        self.extract_quantified_entities(True, transfer_entity_relation)
        
    
    def extract_quantified_entities(self, to_create_transfer_entity, transfer_entity_relation):
        if self.m_cardinal != None:
            if self.m_owner_entity != None:
                temp_quantified_entity = QuantifiedEntity(self.m_cardinal, 'dobj', self.m_dobj, False)
                temp_quantified_entity.set_owner_entity(self.m_owner_entity)
                merge_entities = self.get_or_merge_entity(temp_quantified_entity)                                                    
                self.m_quantified_entity = temp_quantified_entity if merge_entities == True else None
            
            if to_create_transfer_entity and self.m_transfer_entity != None:
                print 'creating transfer entity'
                print -self.m_cardinal      
                temp_transfer_quantified_entity = QuantifiedEntity(-self.m_cardinal, transfer_entity_relation, self.m_dobj, True)
                temp_transfer_quantified_entity.set_owner_entity(self.m_transfer_entity)
                to_merge_transfer_entity = self.get_or_merge_entity(temp_transfer_quantified_entity)                                                    
                self.m_transfer_quantified_entity = temp_transfer_quantified_entity if to_merge_transfer_entity == True else None
        else:
            self.m_object_entity = Entity('dobj', self.m_dobj)
        
    def get_or_merge_entity(self, temp_entity):    
        to_merge_entities = self.m_question.add_quantified_entity(temp_entity)
        print 'to merge?' 
        print to_merge_entities
        if to_merge_entities:
            self.merge_entities(temp_entity)
        return to_merge_entities
                    
    def extract_evaluation_entities(self):
        print 'In extract evaluating entities'
        for dependency in self.m_dependencies:
            if dependency[0] == 'nsubj':
                self.m_has_a_nsubj  = True
                self.m_nsubj = dependency[2]
                self.m_evaluating_subject = Entity('nsubj', self.m_nsubj)
            elif dependency[0] == 'dobj':
                # extract parts of speech of the relation dep and gov
                # if none of them is noun. apply some logic to find the evaluating object
                print self.m_words_pos    
                temp_dobj = dependency[2]
                temp_dobj_pos = self.m_words_pos[temp_dobj]
                if temp_dobj_pos != None and temp_dobj_pos in PublicKeys.NOUN_POS:        
                    self.m_has_a_dobj = True
                    self.m_dobj = dependency[2]
                    self.m_evaluating_object = Entity('dobj', self.m_dobj)
                else:
                    print 'Couldn\'t find a dobj noun'
                    max = 0
                    matching_noun = None
                    for noun in self.m_all_noun_lemmas:
                        for qes in self.m_question.get_quantified_entities().values():
                            for qe in qes:
                                wup_similarity = self.word_similarity(noun, Sentence.LEMMATIZER_MODULE.lemmatize(qe.get_name()))
                                if max < wup_similarity:
                                    max = wup_similarity
                                    matching_noun = qe
                                    
                    self.m_evaluating_object = Entity('dobj', matching_noun.get_name())
                            
    def word_similarity(self, word1, word2):
        xx = wn.synsets(word1, pos=wn.NOUN)
        yy = wn.synsets(word2, pos=wn.NOUN)
        max = 0
        for x in xx:
            for y in yy:
                wup_similarity = x.wup_similarity(y)
                max = wup_similarity if max < wup_similarity else max
        return max           
           
    def extract_result(self):
        quantified_entities = self.m_question.get_quantified_entities()
        subjects_object_entities = quantified_entities[self.m_evaluating_subject.get_name()]
        result = None
        print subjects_object_entities
        for subjects_object_entity in subjects_object_entities:
            print subjects_object_entity
            print self.m_evaluating_object
            if subjects_object_entity.get_name() == self.m_evaluating_object.get_name():
                result = subjects_object_entity
                break
        return result
    
    def merge_entities(self, temp_quantified_entity):
        print "in merge"
        quantified_entities = self.m_question.get_quantified_entities()
        subject = temp_quantified_entity.get_owner_entity().get_name()
        #sentence_output = self.output(True)
        sentence_output = temp_quantified_entity.get_cardinal()
        subject_quantified_entities = quantified_entities[subject]
        for subject_quantified_entity in subject_quantified_entities:
            if subject_quantified_entity.get_name() == temp_quantified_entity.get_name():                
                subject_quantified_entity.perform_operation(sentence_output)
                print subject_quantified_entity
    
    def process_pronouns(self):
        print 'process pronouns'
        if self.m_has_a_pronoun == True:
            singular_pronouns = []
            plural_pronouns = []
            nouns = self.m_question.get_quantified_entities().keys()
            for pronoun_tuple in self.m_all_pronouns:
                pronoun = pronoun_tuple["Text"].lower()
                if pronoun in Sentence.SINGULAR_PRONOUN:
                    singular_pronouns.append(pronoun_tuple)                    
                    for noun in reversed(nouns):
                        print 'found' + noun
                        self.m_processed_pronoun = noun
                        break
                elif pronoun in Sentence.PLURAL_PRONOUN:
                    self.sum_all_entities()

    def sum_all_entities(self):
        print "do something"
            
    def output(self, ret_math_value):
        if ret_math_value == True:
            output = self.m_cardinal
        else:    
            if self.m_predicted_label == '+' or self.m_predicted_label == '-':
                if self.m_cardinal != None:
                    output = self.m_quantified_entity
                else:
                    output = self.m_predicted_label + ' ' + 'X'
        return output
        