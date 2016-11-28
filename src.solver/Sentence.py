from corenlp import StanfordCoreNLP
import json
import re
from QuantifiedEntity import QuantifiedEntity
from Entity import Entity
from collections import OrderedDict
from PublicKeys import PublicKeys
from nltk.corpus import wordnet as wn
from LemmatizerModule import LemmatizerModule
from spacy.en import English
from subject_object_extraction import findSVOs
import unicodedata
import unirest

class Sentence:

    SCORENLP = StanfordCoreNLP("stanford-corenlp-full-2016-10-31/")
    TEXT_LEMMA_PATTERN = re.compile('(\[{1})([a-zA-Z0-9.= $_<>\"\/?]+)(\]{1})')
    PARTS_OF_SPEECH_PATTERN = re.compile('(\({1})([a-zA-Z0-9.= $_<>\"\/?]+)(\){1})')
    
    STRING_TO_DICT_PATTERN = re.compile(r'(\S+)=(".*?"|\S+)')
    SINGULAR_PRONOUN = ['he', 'she', 'it', 'him', 'her', 'his']
    SINGULAR_SUBJECT_PRONOUN = ['he', 'she', 'him', 'her', 'his']
    SINGULAR_OBJECT_PRONOUN = ['it']
    PLURAL_PRONOUN = ['they', 'them']
    LEMMATIZER_MODULE = LemmatizerModule()
    SPACY_PARSER = English()

    def __init__(self, sentence_json, question, sentence_index):
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
        self.m_pobj = None
        self.m_has_a_pobj = False
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
        self.m_sentence_index = sentence_index
        self.m_is_pronoun_noun_found = False
        self.m_current_pronoun = None
        self.temp_transfer_entity = None
        self.temp_dobj = None
        self.m_has_an_unknown_quantity = False
        self.m_possible_evaluating_subjects = None
        self.m_possible_evaluating_object = None
        
        print self.m_predicted_label
        if self.m_predicted_label == '?':
            self.m_question.m_evaluating_sentence = self
        
    def __str__(self):
        return self.m_sentence_text
    
    def parse_sentence(self):
        self.extract_dependencies()
#         self.process_pronouns()
        if self.m_predicted_label == '?':
            self.extract_evaluation_entities()
        else:
            self.extract_entities()

    def extract_dependencies(self):
        print 'in extract dep'
        #print self.m_sentence_text
        corenlp_result = json.loads(Sentence.SCORENLP.parse(self.m_sentence_text))
        current_sentence = corenlp_result["sentences"][0]
        parse_tree = current_sentence["parsetree"]
#         print parse_tree
        self.m_dependencies = current_sentence["dependencies"]
#         self.m_matched_tuples = Sentence.TEXT_LEMMA_PATTERN.findall(parse_tree)
#         print self.m_matched_tuples
#         print self.m_dependencies
        self.m_matched_pos = Sentence.PARTS_OF_SPEECH_PATTERN.findall(parse_tree)
        
        for matched_pos in self.m_matched_pos:
            word_pos = matched_pos[1].split(" ")
            parts_of_speech = word_pos[0]
            word = word_pos[1].lower()
            self.m_words_pos[word] = parts_of_speech
            print word + ":" + parts_of_speech         
            if parts_of_speech in PublicKeys.NOUN_POS:
                lemma = Sentence.LEMMATIZER_MODULE.lemmatize(word)
                self.m_all_noun_lemmas.append(lemma)
                self.m_all_nouns.append(word)
                if parts_of_speech == 'NNP':
                    self.m_question.add_proper_noun(word)
            if parts_of_speech == 'CD':
                self.m_has_a_cardinal = True
                self.m_cardinal = int(word)
                if self.m_predicted_label == '-':
                    self.m_cardinal = -self.m_cardinal
            elif parts_of_speech == 'PRP' or parts_of_speech == 'PRP$':
                print 'found pronoun'
                self.m_has_a_pronoun = True
                self.m_all_pronouns.append(word)
                print self.m_is_pronoun_noun_found
                if self.m_is_pronoun_noun_found == False:
                    print 'In sentence'
                    print self.m_sentence_index
                    print self.m_question.m_coref_dict
                    print self.m_question.m_coref_dict[self.m_sentence_index]
                    current_sentence_coref_dict = self.m_question.m_coref_dict[self.m_sentence_index]
                    
                    print 'pronoun not found yet' + word
                    print current_sentence_coref_dict
                    if word in current_sentence_coref_dict:
                        print 'word in dict true'
                        current_pronoun_noun = current_sentence_coref_dict[word]
                        print 'current_pronoun_noun' + current_pronoun_noun
                        print self.m_question.m_proper_nouns
                        if current_pronoun_noun.lower() in self.m_question.m_proper_nouns:
                            self.m_processed_pronoun = current_pronoun_noun
                            self.m_is_pronoun_noun_found = True
                            self.m_current_pronoun = word
                            print "Pronoun Noun :" + self.m_processed_pronoun
        
        if (self.m_predicted_label == '-' or self.m_predicted_label == '+' or self.m_predicted_label == '=') and self.m_has_a_cardinal == False:
            self.m_has_a_cardinal = True
            self.m_cardinal = 'X'
            self.m_has_an_unknown_quantity = True
        
    def extract_entities(self):
        print 'in extract entities'
        sentence_parse = Sentence.SPACY_PARSER(self.m_sentence_text)
        spacy_subj = None
        temp_pobj = None
        for token in sentence_parse:
            print(token.orth_, token.dep_, token.head.orth_, [t.orth_ for t in token.lefts], [t.orth_ for t in token.rights])
            if token.dep_ == 'pobj':
                print 'found pobj'
                temp_pobj = token
#                 self.assign_pobj(token)
            elif token.dep_ == 'nsubj':
                spacy_subj = token.orth_.lower()
            elif token.dep_ == 'poss':
                self.assign_poss_entities(token)
        
        sentence_svos = findSVOs(sentence_parse)
        print spacy_subj
        print self.m_has_a_pobj
        print sentence_svos
        if len(sentence_svos) > 0 :
            transfer_entity_relation = None
            if self.m_is_first_word_an_expletive == False:
                                
                print sentence_svos[0][0]
                print sentence_svos[0][2]
                
                #trying to assign subj and obj from svo
                self.assign_nsubj(sentence_svos[0][0])
                self.assign_dobj(sentence_svos[0][2])
                
                print 'after trying to assign dobj:'
                print  self.m_has_a_dobj
                print self.temp_dobj
                
                if self.m_has_a_dobj == False:
                    if self.temp_dobj != None:
                        self.assign_dobj(self.temp_dobj)
                        if self.temp_transfer_entity != None:
                            self.assign_transfer_entity(self.temp_transfer_entity, 'dobj')
                    elif temp_pobj != None:
                        self.assign_dobj(temp_pobj.orth_.lower())
                        #self.assign_dobj(self.m_pobj, 'pobj')
                        self.assign_transfer_entity(sentence_svos[0][2], 'dobj')
                elif temp_pobj != None:
                    self.assign_transfer_entity(temp_pobj.orth_.lower(), 'pobj')
                elif self.temp_transfer_entity != None:
                    self.assign_transfer_entity(self.temp_transfer_entity, 'poss')
            else:
                self.assign_dobj(sentence_svos[0][2])
                
                if temp_pobj != None:
                    self.assign_nsubj(temp_pobj.orth_.lower())
            print 'before calling extract quantified'
            self.extract_quantified_entities(True, transfer_entity_relation)
        elif spacy_subj != None and temp_pobj != None:
            self.temp_dobj = temp_pobj.orth_
            print 'In spacy' + spacy_subj
            print self.temp_dobj
            self.assign_nsubj(spacy_subj)
            self.assign_dobj(self.temp_dobj)
            self.extract_quantified_entities(False, None)
            

    def assign_nsubj(self, subj):
        self.m_has_a_nsubj  = True
        self.m_nsubj = subj
        if self.m_nsubj in self.m_all_pronouns:
            self.m_nsubj = self.m_processed_pronoun
        self.m_owner_entity = Entity('nsubj', self.m_nsubj)
        
    def assign_dobj(self, dobj):
        if self.is_integer(dobj) == False and dobj not in self.m_question.m_proper_nouns:
            self.m_has_a_dobj = True
            self.m_dobj = dobj
        elif dobj in self.m_question.m_proper_nouns:
            self.temp_transfer_entity = dobj
            if self.temp_transfer_entity in self.m_all_pronouns:
                self.temp_transfer_entity = self.m_processed_pronoun

    def assign_pobj(self, token):
        token_orth = token.orth_.lower()
        print token_orth
        print self.m_question.get_quantified_entities()
        print self.m_question.get_quantified_entity_objects()
        if token_orth in self.m_question.get_quantified_entities():
            print 'assigning pobj'
            self.m_pobj = token_orth
            if self.m_pobj in self.m_all_pronouns:
                self.m_pobj = self.m_processed_pronoun
                        
            self.m_has_a_pobj = True
        #elif token_orth in self.m_question.get_quantified_entity_objects():
        else:
            self.temp_dobj = token_orth
        
    def assign_poss_entities(self, token):
        self.temp_transfer_entity = token.orth_.lower()
        self.temp_dobj = token.head.orth_.lower()
    
    def assign_transfer_entity(self, val, pos):
        if val != None:
            val = val.lower()
            print 'in assign transfer entity:' + val
            if val in self.m_all_pronouns:
                val = self.m_processed_pronoun
            
            self.m_transfer_entity = Entity(pos, val)
        
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
        print self.m_transfer_entity
#         print self.m_owner_entity
        
        if self.m_cardinal != None:
            lemmatized_dobj = Sentence.LEMMATIZER_MODULE.lemmatize(self.m_dobj)
            if self.m_owner_entity != None:
                print self.m_dobj
                print type(self.m_dobj)
                print self.m_dobj.lower()
                
                owner_modified_cardinal = self.m_cardinal
                if self.m_has_an_unknown_quantity:
                    if self.m_predicted_label == '-':
                        owner_modified_cardinal = "-" + self.m_cardinal
                    else:
                        owner_modified_cardinal = self.m_cardinal
                
                temp_quantified_entity = QuantifiedEntity(owner_modified_cardinal, 'dobj', lemmatized_dobj, False)
                temp_quantified_entity.set_owner_entity(self.m_owner_entity)
                merge_entities = self.get_or_merge_entity(temp_quantified_entity)                                                    
                self.m_quantified_entity = temp_quantified_entity if merge_entities == True else None
            else:
                self.m_owner_entity = Entity("global", u"global")
                global_modified_cardinal = self.m_cardinal
                if self.m_has_an_unknown_quantity:
                    if self.m_predicted_label == '-':
                        global_modified_cardinal = "-" + self.m_cardinal
                    else:
                        global_modified_cardinal = self.m_cardinal
                
                temp_quantified_entity = QuantifiedEntity(global_modified_cardinal, 'dobj', lemmatized_dobj, False)
                temp_quantified_entity.set_owner_entity(self.m_owner_entity)
                merge_entities = self.get_or_merge_entity(temp_quantified_entity)                                                    
                self.m_quantified_entity = temp_quantified_entity if merge_entities == True else None
                
                
            if to_create_transfer_entity and self.m_transfer_entity != None:
                print 'creating transfer entity'
                
                transfer_modified_cardinal = self.m_cardinal
                if self.m_has_an_unknown_quantity:
                    if self.m_predicted_label == '+':
                        transfer_modified_cardinal = "-" + self.m_cardinal
                    else:
                        transfer_modified_cardinal = self.m_cardinal
                else:
                    transfer_modified_cardinal = -self.m_cardinal
                
                print transfer_modified_cardinal
                temp_transfer_quantified_entity = QuantifiedEntity(transfer_modified_cardinal, transfer_entity_relation, lemmatized_dobj, True)
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
        noun_chunks = self.get_noun_chunks()
        print noun_chunks
        print noun_chunks[0]
        if self.m_is_pronoun_noun_found == True:
            print self.m_processed_pronoun
        
        for index, val in enumerate(noun_chunks):            
            if val == self.m_current_pronoun:
                noun_chunks[index] = self.m_processed_pronoun
            noun_chunks[index] = Sentence.LEMMATIZER_MODULE.lemmatize(unicode(noun_chunks[index])).lower()
        print 'After lemmatizing and pronoun replacement'
        print noun_chunks
        
        for noun in noun_chunks:
            if noun in self.m_question.get_quantified_entities():
                self.m_possible_evaluating_subjects.append(noun)
            elif self.m_possible_evaluating_object == None:
                self.m_possible_evaluating_object = noun
        print 'possible subjects'
        print self.m_possible_evaluating_subjects
        print 'possible object'
        print self.m_possible_evaluating_object
        
#         for dependency in self.m_dependencies:
#             if dependency[0] == 'nsubj':
#                 self.m_has_a_nsubj  = True
#                 self.m_nsubj = dependency[2]
#                 self.m_evaluating_subject = Entity('nsubj', self.m_nsubj)
#             elif dependency[0] == 'dobj':
#                 # extract parts of speech of the relation dep and gov
#                 # if none of them is noun. apply some logic to find the evaluating object
#                 print self.m_words_pos    
#                 temp_dobj = dependency[2]
#                 temp_dobj_pos = self.m_words_pos[temp_dobj]
#                 if temp_dobj_pos != None and temp_dobj_pos in PublicKeys.NOUN_POS:        
#                     self.m_has_a_dobj = True
#                     self.m_dobj = dependency[2]
#                     self.m_evaluating_object = Entity('dobj', self.m_dobj)
#                 else:
#                     print 'Couldn\'t find a dobj noun'
#                     max = 0
#                     matching_noun = None
#                     for noun in self.m_all_noun_lemmas:
#                         for qes in self.m_question.get_quantified_entities().values():
#                             for qe in qes:
#                                 wup_similarity = self.word_similarity(noun, qe.get_name())
#                                 if max < wup_similarity:
#                                     max = wup_similarity
#                                     matching_noun = qe
#                                     
#                     self.m_evaluating_object = Entity('dobj', matching_noun.get_name())
                           
    def get_noun_chunks(self):
        response = unirest.post("https://textanalysis.p.mashape.com/spacy-noun-chunks-extraction",
          headers={
            "X-Mashape-Key": "9rHNYPNXpOmshUXLsLxtJJ8Qabkdp1DkjSsjsnAHic8vw9yrP7",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
          },
          params={
            "text": self.m_sentence_text
          }
        )
        print response.body
        print response.raw_body
        response_json = json.loads(response.raw_body)
        print response_json["result"]
        return response_json["result"]
     
    def word_similarity(self, word1, word2):
        xx = wn.synsets(word1, pos=wn.NOUN)
        yy = wn.synsets(word2, pos=wn.NOUN)
        max = 0
        for x in xx:
            for y in yy:
                wup_similarity = x.wup_similarity(y)
                max = wup_similarity if max < wup_similarity else max
        return max           
           
    def is_integer(self, val):
        is_integer = True
        try:
            dummy = int(val)
        except:
            is_integer = False
        return is_integer

    def extract_result(self):
        print 'In extract result'
        quantified_entities = self.m_question.get_quantified_entities()
        result = None
        if len(self.m_possible_evaluating_subjects) == 1:
            subject = self.m_possible_evaluating_subjects.get(0)
            if subject in quantified_entities:
                subjects_object_entities = quantified_entities[subject]
                
                for subjects_object_entity in subjects_object_entities:
                    print subjects_object_entity
                    print self.m_evaluating_object
                    if subjects_object_entity.get_name() == self.m_possible_evaluating_object:
                        result = subjects_object_entity
                        break
        return result

#         subjects_object_entities = quantified_entities[self.m_evaluating_subject.get_name()]
#         result = None
#         print subjects_object_entities
#         for subjects_object_entity in subjects_object_entities:
#             print subjects_object_entity
#             print self.m_evaluating_object
#             if subjects_object_entity.get_name() == self.m_evaluating_object.get_name():
#                 result = subjects_object_entity
#                 break
#         return result
    
    def merge_entities(self, temp_quantified_entity):
        print "in merge"
        quantified_entities = self.m_question.get_quantified_entities()
        subject = temp_quantified_entity.get_owner_entity().get_name()
        #sentence_output = self.output(True)
        sentence_output = temp_quantified_entity.get_cardinal()
        subject_quantified_entities = quantified_entities[subject]
        for subject_quantified_entity in subject_quantified_entities:
            if subject_quantified_entity.get_name() == temp_quantified_entity.get_name():
                if self.m_predicted_label == '=':
                    subject_quantified_entity.set_equal_to_state(sentence_output)
                else:
                    subject_quantified_entity.perform_operation(sentence_output, self.m_has_an_unknown_quantity)
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
        