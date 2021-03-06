from corenlp import StanfordCoreNLP
import json
import re
from QuantifiedEntity import QuantifiedEntity
from QuantifiedNonEntity import QuantifiedNonEntity
from Entity import Entity
from collections import OrderedDict
from PublicKeys import PublicKeys
from nltk.corpus import wordnet as wn
from LemmatizerModule import LemmatizerModule
from spacy.en import English
from subject_object_extraction import findSVOs
import unicodedata
import unirest
from QuestionSentenceSolver import QuestionSentenceSolver
from ComparisonSentenceSolver import ComparisonSentenceSolver
from TransferTransaction import TransferTransaction
from sympy.polys.groebnertools import Num
from decimal import Decimal
from CompoundModifier import CompoundModifier
from ButConjunctionSentenceSolver import ButConjunctionSentenceSolver
from UnknownSentenceSolver import UnknownSentenceSolver

class Sentence:

    # SCORENLP = StanfordCoreNLP("/Users/rajpav/anaconda2/lib/python2.7/site-packages/stanford-corenlp-full-2016-10-31")
    SCORENLP = StanfordCoreNLP("/Users/acharya.n/anaconda2/lib/python2.7/stanford-corenlp-full-2016-10-31")

    TEXT_LEMMA_PATTERN = re.compile('(\[{1})([a-zA-Z0-9.= $_<>\"\/?]+)(\]{1})')
    PARTS_OF_SPEECH_PATTERN = re.compile('(\({1})([a-zA-Z0-9.= $_<>\-\"\/?]+)(\){1})')
    NON_ALLOWED_NOUN_CHUNKS = ["how", "many", "much"]
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
        ###print self.m_sentence_text
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
        self.m_expletive_index = -1
        if 'E' in self.m_syntactic_pattern:
            self.m_expletive_index = self.m_syntactic_pattern.index('E')
        
        self.m_sentence_index = sentence_index
        self.m_is_pronoun_noun_found = False
        self.m_current_pronoun = None
        self.temp_transfer_entity = None
        self.temp_dobj = None
        self.m_has_an_unknown_quantity = False
        self.m_possible_evaluating_subjects = []
        self.m_possible_evaluating_object = None
        self.m_question_label = None
        self.m_complex_nouns = []
        self.m_sentece_words = []
        self.m_words_index = {}
        self.m_compound_modifiers = []
        question_label_string = "QuestionLabel"
        if self.m_predicted_label == '?' and question_label_string in sentence_json:
            self.m_question.m_evaluating_sentence = self
            self.m_question_label = sentence_json["QuestionLabel"]
        
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
        print self.m_sentence_text
        corenlp_result = json.loads(Sentence.SCORENLP.parse(self.m_sentence_text))
        current_sentence = corenlp_result["sentences"][0]
        parse_tree = current_sentence["parsetree"]
#         print 'parse_tree',parse_tree
        self.m_dependencies = current_sentence["dependencies"]
#         self.m_matched_tuples = Sentence.TEXT_LEMMA_PATTERN.findall(parse_tree)
#         print 'matched tuples',self.m_matched_tuples
#         print self.m_dependencies
        self.m_matched_pos = Sentence.PARTS_OF_SPEECH_PATTERN.findall(parse_tree)
#         print self.m_matched_pos
        index_counter = 0
        for matched_pos in self.m_matched_pos:
            index_counter = index_counter + 1
            word_pos = matched_pos[1].split(" ")
            parts_of_speech = word_pos[0]
            word = word_pos[1].lower()
#             #print word
            self.m_words_index[word] = index_counter
            self.m_sentece_words.append(word)
            self.m_words_pos[word] = parts_of_speech

            if parts_of_speech in PublicKeys.NOUN_POS:
                lemma = Sentence.LEMMATIZER_MODULE.lemmatize(word)
                self.m_all_noun_lemmas.append(lemma)
                self.m_all_nouns.append(word)
                if parts_of_speech == 'NNP':
                    self.m_question.add_proper_noun(word)
            if parts_of_speech == 'CD':
                self.m_has_a_cardinal = True
                if self.m_expletive_index !=-1:
                    self.m_is_first_word_an_expletive = True
                try:
#                     #print 1
#                     #print word
#                     #print 2
#                     #print float(word)
#                     #print 3
#                     #print str(float(word))
                    self.m_cardinal = Decimal(word)
#                     #print self.m_cardinal
                except:
                    self.m_cardinal = PublicKeys.text2int(word)
#                     #print self.m_cardinal
                    self.m_words_index[str(self.m_cardinal)] = index_counter
#                     #print 'insert'
#                     #print self.m_words_index[str(self.m_cardinal)]
                if self.m_predicted_label == '-':
                    self.m_cardinal = -self.m_cardinal
            elif parts_of_speech == 'PRP' or parts_of_speech == 'PRP$':
                ###print 'found pronoun'
                self.m_has_a_pronoun = True
                self.m_all_pronouns.append(word)
                ###print self.m_is_pronoun_noun_found
                if self.m_is_pronoun_noun_found == False:
                    ###print 'In sentence'
                    ###print self.m_sentence_index
                    ###print self.m_question.m_coref_dict
                    ###print self.m_question.m_coref_dict[self.m_sentence_index]
                    current_sentence_coref_dict = self.m_question.m_coref_dict[self.m_sentence_index]
                    
                    ###print 'pronoun not found yet' + word
                    ###print current_sentence_coref_dict
                    if word in current_sentence_coref_dict:
                        ###print 'word in dict true'
                        current_pronoun_noun = current_sentence_coref_dict[word]
                        ###print 'current_pronoun_noun' + current_pronoun_noun
                        ###print self.m_question.m_proper_nouns
                        if current_pronoun_noun.lower() in self.m_question.m_proper_nouns:
                            self.m_processed_pronoun = current_pronoun_noun
                            self.m_is_pronoun_noun_found = True
                            self.m_current_pronoun = word
                            ###print "Pronoun Noun :" + self.m_processed_pronoun
        
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
            token_dep = token.dep_
            print(token.orth_, token.dep_, token.head.orth_, [t.orth_ for t in token.lefts], [t.orth_ for t in token.rights])
            if token_dep == 'pobj':
                temp_pobj = token
            elif token_dep == 'nsubj' or token_dep == 'nsubjpass':
                spacy_subj = token.orth_.lower()
            elif token_dep == 'poss':
                self.assign_poss_entities(token)
            elif token_dep == 'compound' or token_dep == 'amod':
                print 'in compound and amod case'
                modifier = Sentence.LEMMATIZER_MODULE.lemmatize(token.orth_)
                compound_dobj = Sentence.LEMMATIZER_MODULE.lemmatize(token.head.orth_)
                compound_modifier = CompoundModifier(modifier, compound_dobj)
                print 'found compound modifier:',modifier,compound_dobj
                self.m_compound_modifiers.append(compound_modifier)
                self.m_complex_nouns.append(modifier +  " " + compound_dobj)
#                 self.temp_dobj = compound_dobj
            
        
        sentence_svos = findSVOs(sentence_parse)
        print "svos",sentence_svos,len(sentence_svos)
        if len(sentence_svos) > 0 :
            transfer_entity_relation = None
#             #print 'starts with an expl:',self.m_is_first_word_an_expletive
            if self.m_is_first_word_an_expletive == False:
                                
                print 'svo'
                print sentence_svos[0][0]
                print sentence_svos[0][2]
                
#                 trying to assign subj and obj from svo
                self.assign_nsubj(sentence_svos[0][0])
                self.assign_dobj(sentence_svos[0][2])
                
                print 'after trying to assign subj', self.m_nsubj
                print 'after trying to assign dobj:'
                print  'dobj exists?:',self.m_has_a_dobj
                print 'dobj:',self.m_dobj
                print 'temp dobj:',self.temp_dobj
                #print temp_pobj
                
                if self.m_has_a_dobj == False:
                    if self.temp_dobj != None:
                        print 'before temp dobj'
                        self.assign_dobj(self.temp_dobj)
                        if self.temp_transfer_entity != None:
                            self.assign_transfer_entity(self.temp_transfer_entity, 'dobj')
                    elif temp_pobj != None:
                        print 'before temp pobj'
                        self.assign_dobj(temp_pobj.orth_.lower())
                        #self.assign_dobj(self.m_pobj, 'pobj')
                        self.assign_transfer_entity(sentence_svos[0][2], 'dobj')
                elif temp_pobj != None:
                    print 'in temp dobj != None'
                    self.assign_transfer_entity(temp_pobj.orth_.lower(), 'pobj')
                elif self.temp_transfer_entity != None:
                    print 'in temp transfer entity !- None'
                    self.assign_transfer_entity(self.temp_transfer_entity, 'poss')
            else:
#                 #print 'before 2nsd svo'
                self.assign_dobj(sentence_svos[0][2])
                
                if temp_pobj != None:
                    self.assign_nsubj(temp_pobj.orth_.lower())
            ###print 'before calling extract quantified'
            self.extract_quantified_entities(True, transfer_entity_relation)
        elif spacy_subj != None and temp_pobj != None:
            self.temp_dobj = temp_pobj.orth_
            print 'In spacy'
            #print self.temp_dobj
            self.assign_nsubj(spacy_subj)
            self.assign_dobj(self.temp_dobj)
            self.extract_quantified_entities(False, None)
        elif spacy_subj != None and self.m_question.m_question_label != 'c':
            
#             print 'spacy_subj is not none'
            self.assign_dobj(spacy_subj)
            self.extract_quantified_entities(False, None)

        elif self.m_question.m_question_label == 'c':
            if self.m_has_a_cardinal:
                print 'found nothing should do something.'
                quantified_non_entity = QuantifiedNonEntity(self.m_cardinal)
                if spacy_subj != None:
                    self.assign_nsubj(spacy_subj)
                    quantified_non_entity.set_owner_entity(self.m_owner_entity)
                    self.m_question.add_quantified_non_entity(quantified_non_entity)


    def assign_nsubj(self, subj):
        self.m_has_a_nsubj  = True
        self.m_nsubj = subj
        if self.m_nsubj in self.m_all_pronouns:
            self.m_nsubj = self.m_processed_pronoun
        self.m_owner_entity = Entity('nsubj', self.m_nsubj)
        
    def assign_dobj(self, dobj):
#         #print dobj
        #print 'in assigning dobj'
        is_dobj_integer = self.is_integer(dobj)
        if is_dobj_integer == False and dobj not in self.m_question.m_proper_nouns:
            self.m_has_a_dobj = True
            self.m_dobj = dobj
        elif dobj in self.m_question.m_proper_nouns:
            self.temp_transfer_entity = dobj
            if self.temp_transfer_entity in self.m_all_pronouns:
                self.temp_transfer_entity = self.m_processed_pronoun
        elif is_dobj_integer == True:
            for k,v in self.m_question.m_quantified_entities.items():
                if self.m_has_a_dobj:
                    break
                for e in v:
                    print 'assigning cardianl d object'
                    self.m_has_a_dobj = True
                    self.m_dobj = unicode(e.get_name())
                    self.m_words_pos[e.get_name()] = 'NN'
                    self.m_words_index[e.get_name()] = self.m_words_index[dobj]
                    break

    def assign_pobj(self, token):
        token_orth = token.orth_.lower()
        ###print token_orth
        ###print self.m_question.get_quantified_entities()
        ###print self.m_question.get_quantified_entity_objects()
        if token_orth in self.m_question.get_quantified_entities():
            ###print 'assigning pobj'
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
            ##print 'in assign transfer entity:' + val
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
        ##print self.m_transfer_entity
#         ##print self.m_owner_entity
        print 'in extract quantified entities'
        if self.m_cardinal != None and self.m_has_an_unknown_quantity == False:
            self.validate_dobj_index()
            print 'in cardinal case and no unknown quantity'
#             #print self.m_dobj
            
            lemmatized_dobj = Sentence.LEMMATIZER_MODULE.lemmatize(self.m_dobj)
            compound_modifier = self.get_compound_modifier_for_dobj(self.m_dobj)
            
            if self.m_owner_entity != None:
                print 'owner entity not none'
                ##print self.m_dobj
                ##print type(self.m_dobj)
                ##print self.m_dobj.lower()
                
                owner_modified_cardinal = self.m_cardinal
                 
                if self.m_has_an_unknown_quantity:
                    if self.m_predicted_label == '-':
                        owner_modified_cardinal = "-" + self.m_cardinal
                        transfer_transaction_cardinal = self.m_cardinal
                    else:
                        owner_modified_cardinal = self.m_cardinal
                        transfer_transaction_cardinal = "-" + self.m_cardinal
                else:
                    transfer_transaction_cardinal = -self.m_cardinal
                print 'after calc transfer cardinal:', transfer_transaction_cardinal
                temp_quantified_entity = QuantifiedEntity(owner_modified_cardinal, 'dobj', lemmatized_dobj, False)
                temp_quantified_entity.set_owner_entity(self.m_owner_entity)
                
                transfer_transaction = TransferTransaction(to_create_transfer_entity, self.m_transfer_entity, lemmatized_dobj, transfer_transaction_cardinal)
                temp_quantified_entity.add_transfer_transaction(transfer_transaction)
                
                print 'after merging',compound_modifier
                if compound_modifier != None:
                    print 'modifier quantity,'
                    compound_modifier.set_quantity(owner_modified_cardinal)
                    temp_quantified_entity.add_compound_modifier(compound_modifier)
                    for k,v in self.m_question.m_quantified_entities.items():
                        for e in v:
                            print 'comparisons:',e.get_name(), compound_modifier.m_dobj
                            if e.get_name() == compound_modifier.m_dobj:
                                print 'adding compoung modifier'
                            e.add_compound_modifier(compound_modifier)
                merge_entities = self.get_or_merge_entity(temp_quantified_entity, transfer_transaction)
                

                        
                                                                    
#                 self.m_quantified_entity = temp_quantified_entity if merge_entities == True else None
            else:
                self.m_owner_entity = Entity("global", u"global")
                global_modified_cardinal = self.m_cardinal
                if self.m_has_an_unknown_quantity:
                    if self.m_predicted_label == '-':
                        global_modified_cardinal = "-" + self.m_cardinal
                    else:
                        global_modified_cardinal = self.m_cardinal
                elif global_modified_cardinal < 0:
                    global_modified_cardinal = -global_modified_cardinal
                
                temp_quantified_entity = QuantifiedEntity(global_modified_cardinal, 'dobj', lemmatized_dobj, False)
                temp_quantified_entity.set_owner_entity(self.m_owner_entity)
                merge_entities = self.get_or_merge_entity(temp_quantified_entity, None)
                                                                    
#                 self.m_quantified_entity = temp_quantified_entity if merge_entities == True else None
                
                
            if to_create_transfer_entity and self.m_transfer_entity != None:
                ##print 'creating transfer entity'
                
                transfer_modified_cardinal = self.m_cardinal
                if self.m_has_an_unknown_quantity:
                    if self.m_predicted_label == '+':
                        transfer_modified_cardinal = "-" + self.m_cardinal
                        transfer_transaction_cardinal = self.m_cardinal
                    else:
                        transfer_modified_cardinal = self.m_cardinal
                        transfer_transaction_cardinal = "-" + self.m_cardinal
                else:
                    transfer_modified_cardinal = -self.m_cardinal
                    transfer_transaction_cardinal = self.m_cardinal
                
                ##print transfer_modified_cardinal
                temp_transfer_quantified_entity = QuantifiedEntity(transfer_modified_cardinal, transfer_entity_relation, lemmatized_dobj, True)
                temp_transfer_quantified_entity.set_owner_entity(self.m_transfer_entity)
                transfer_transaction = TransferTransaction(to_create_transfer_entity, self.m_owner_entity, lemmatized_dobj, transfer_transaction_cardinal)
                temp_transfer_quantified_entity.add_transfer_transaction(transfer_transaction)
                
                to_merge_transfer_entity = self.get_or_merge_entity(temp_transfer_quantified_entity, transfer_transaction)                                                    
                self.m_transfer_quantified_entity = temp_transfer_quantified_entity if to_merge_transfer_entity == True else None
            
        else:
            self.m_object_entity = Entity('dobj', self.m_dobj)
        
        
    def get_compound_modifier_for_dobj(self, dobj):
        dobj = Sentence.LEMMATIZER_MODULE.lemmatize(dobj)
        print 'In compound modifier for dobj', dobj, len(self.m_compound_modifiers)
        compound_modifier = None
        for modifier in self.m_compound_modifiers:
            print 'modifier dobj',modifier.m_dobj
            if dobj == modifier.m_dobj:
                compound_modifier = modifier
                break
        return compound_modifier
    
    def validate_dobj_index(self):
        num = self.m_cardinal
#         #print self.m_words_index
#         #print num
#         #print self.m_dobj
        if num < 0:
            num = -num
        if self.m_dobj == None:
            dobj_index = 0
        else:
            if self.m_dobj.lower() in self.m_words_index:
                dobj_index = self.m_words_index[self.m_dobj.lower()]
            else:
                dobj_index = 0
        
            dobj_lower = self.m_dobj.lower()
#             print 'pos before prp',self.m_words_pos
#             print 'dobj before prp',self.m_dobj
            if self.m_words_pos[self.m_dobj.lower()] == 'PRP' or self.m_words_pos[dobj_lower] == 'PRP$':
                for k,v in self.m_question.m_quantified_entities.items():
                    if self.m_has_a_dobj:
                        break
                    for e in v:
                        #print 'assigning pronoun object'
                        self.assign_dobj(unicode(e.get_name()))
                        break
        
        cardinal_index = self.m_words_index[str(num)] if str(num) in self.m_words_index else self.m_words_index[str(int(num))]
        if dobj_index < cardinal_index:
            current_possible_obj = None

            to_consider_for_objects = []
            for current_word in self.m_words_index:
                current_word_index = self.m_words_index[current_word]
                if current_word_index > cardinal_index and (current_word in self.m_all_nouns or current_word in self.m_all_pronouns):
                    current_possible_obj = Sentence.LEMMATIZER_MODULE.lemmatize(current_word)
                    break
            if current_possible_obj != None:
                self.assign_dobj(unicode(current_possible_obj))
        
    def get_or_merge_entity(self, temp_entity, transfer_transaction):    
        to_merge_entities = self.m_question.add_quantified_entity(temp_entity)
        print 'to merge?' 
        ##print to_merge_entities
        if to_merge_entities:
            self.merge_entities(temp_entity, transfer_transaction)
        elif self.m_predicted_label == '=':
            temp_entity.flip_equal_to_state()
            
        return to_merge_entities
                    
    def merge_entities(self, temp_quantified_entity, transfer_transaction):
        ##print "in merge"
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
                    subject_quantified_entity.perform_operation(sentence_output, self.m_has_an_unknown_quantity, transfer_transaction)
                ##print subject_quantified_entity
    
    def extract_evaluation_entities(self):
        sentence_parse = Sentence.SPACY_PARSER(self.m_sentence_text)
        # print "in extract evaluating entities"
        # print sentence_parse
        for token in sentence_parse:
            if token.dep_ == 'compound' or token.dep_ == 'amod':
                print 'in compound and amod case'
                modifier = Sentence.LEMMATIZER_MODULE.lemmatize(token.orth_)
                compound_dobj = Sentence.LEMMATIZER_MODULE.lemmatize(token.head.orth_)
                compound_modifier = CompoundModifier(modifier, compound_dobj)
                print 'found compound modifier:',modifier,compound_dobj
                self.m_compound_modifiers.append(compound_modifier)
                self.m_complex_nouns.append(Sentence.LEMMATIZER_MODULE.lemmatize(token.orth_) +  " " + Sentence.LEMMATIZER_MODULE.lemmatize(token.head.orth_))
                

        ##print 'In extract evaluating entities'
#         noun_chunks = self.get_noun_chunks(self.m_sentence_text)
#         if self.m_is_pronoun_noun_found == True:
            ##print self.m_processed_pronoun        
        
#         for index, val in enumerate(noun_chunks):
#             val_lower_unicode = val.lower()
#             for word in Sentence.NON_ALLOWED_NOUN_CHUNKS:
#                 if word in val_lower_unicode:
#                     val_lower_unicode = val_lower_unicode.replace(word,'')
# #                     noun_chunks[index] = val_lower_str.replace(word,'')
#                     ##print noun_chunks
#             ##print 'Before assigning chunk'
#             ##print val_lower_unicode
#             noun_chunks[index] = val_lower_unicode.strip()
        ##print "after removing non allowed chunks: ", noun_chunks
                
#             chunk_split = val.split()
#             if len(chunk_split) > 1:
#                 sentence_split = self.m_sentence_text.split()
#                 lemma_sentence = ''
#                 for sentence_split_word in sentence_split:
#                     lemma_sentence = lemma_sentence + ' ' + Sentence.LEMMATIZER_MODULE.lemmatize(sentence_split_word)
#                 ##print lemma_sentence
#                 noun_chunks = self.get_noun_chunks(lemma_sentence)    
        
                                
#         for index, val in enumerate(noun_chunks):
#             if val == self.m_current_pronoun:
#                 noun_chunks[index] = self.m_processed_pronoun
#             noun_chunks[index] = Sentence.LEMMATIZER_MODULE.lemmatize(unicode(noun_chunks[index])).lower()
        
        ##print 'After lemmatizing and pronoun replacement'
        ##print noun_chunks
        
        
        
#         for noun in noun_chunks:
#             if noun in self.m_question.get_quantified_entities():
#                 self.m_possible_evaluating_subjects.append(noun)
#             elif self.m_possible_evaluating_object == None:
#                 self.m_possible_evaluating_object = noun
        ##print 'possible subjects'
        ##print self.m_possible_evaluating_subjects
        ##print 'possible object'
        ##print self.m_possible_evaluating_object
        
#         for dependency in self.m_dependencies:
#             if dependency[0] == 'nsubj':
#                 self.m_has_a_nsubj  = True
#                 self.m_nsubj = dependency[2]
#                 self.m_evaluating_subject = Entity('nsubj', self.m_nsubj)
#             elif dependency[0] == 'dobj':
#                 # extract parts of speech of the relation dep and gov
#                 # if none of them is noun. apply some logic to find the evaluating object
#                 ##print self.m_words_pos    
#                 temp_dobj = dependency[2]
#                 temp_dobj_pos = self.m_words_pos[temp_dobj]
#                 if temp_dobj_pos != None and temp_dobj_pos in PublicKeys.NOUN_POS:        
#                     self.m_has_a_dobj = True
#                     self.m_dobj = dependency[2]
#                     self.m_evaluating_object = Entity('dobj', self.m_dobj)
#                 else:
#                     ##print 'Couldn\'t find a dobj noun'
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
                           
    def get_noun_chunks(self, text):
        response = unirest.post("https://textanalysis.p.mashape.com/spacy-noun-chunks-extraction",
          headers={
            "X-Mashape-Key": "KRSu5yA8domshWMHNzhofCid2f3fp1aOWWsjsnuS3zN7CYN9Kq",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
          },
          params={
            "text": text
          }
        )
        ##print response.body
        ##print response.raw_body
        response_json = json.loads(response.raw_body)
#         print 'response:',response_json
        ##print response_json["result"]
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
        ##print 'In extract result'
        quantified_entities = self.m_question.get_quantified_entities()
        result = None
        if self.m_question_label == 'all':
            return QuestionSentenceSolver.solve_for_all_label(self)
        elif self.m_question_label == '+':
            return QuestionSentenceSolver.solve_for_plus_label(self)
        elif self.m_question_label == 'c':
            return ComparisonSentenceSolver.solve_for_c_label(self)
        elif self.m_question_label == 'b':
            return ButConjunctionSentenceSolver.solve_for_but_label(self)
        elif self.m_question_label == 'u':
            return UnknownSentenceSolver.solve_for_unknown_label(self)
        else:
            return None
        # if len(self.m_possible_evaluating_subjects) == 1:
        #     subject = self.m_possible_evaluating_subjects[0]
        #     if subject in quantified_entities:
        #         subjects_object_entities = quantified_entities[subject]
        #
        #         for subjects_object_entity in subjects_object_entities:
        #             ##print 'during comparison'
        #             ##print subjects_object_entity
        #             ##print self.m_possible_evaluating_object
        #             if subjects_object_entity.get_name() == self.m_possible_evaluating_object:
        #                 result = subjects_object_entity
        #                 break
#         return result

#         subjects_object_entities = quantified_entities[self.m_evaluating_subject.get_name()]
#         result = None
#         ##print subjects_object_entities
#         for subjects_object_entity in subjects_object_entities:
#             ##print subjects_object_entity
#             ##print self.m_evaluating_object
#             if subjects_object_entity.get_name() == self.m_evaluating_object.get_name():
#                 result = subjects_object_entity
#                 break
#         return result
    
    
    
    def process_pronouns(self):
        ##print 'process pronouns'
        if self.m_has_a_pronoun == True:
            singular_pronouns = []
            plural_pronouns = []
            nouns = self.m_question.get_quantified_entities().keys()
            for pronoun_tuple in self.m_all_pronouns:
                pronoun = pronoun_tuple["Text"].lower()
                if pronoun in Sentence.SINGULAR_PRONOUN:
                    singular_pronouns.append(pronoun_tuple)                    
                    for noun in reversed(nouns):
                        ##print 'found' + noun
                        self.m_processed_pronoun = noun
                        break
                elif pronoun in Sentence.PLURAL_PRONOUN:
                    self.sum_all_entities()

#     def sum_all_entities(self):
        ##print "do something"
            
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
