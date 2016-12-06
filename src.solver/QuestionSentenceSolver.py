from symbol import comparison
class QuestionSentenceSolver:
    
    @staticmethod
    def solve_for_all_label(sentence):
        sentence_split = sentence.m_sentence_text.split()
        lemma_sentence = ''
        for sentence_split_word in sentence_split:
            lemma_sentence = lemma_sentence + ' ' + sentence.LEMMATIZER_MODULE.lemmatize(sentence_split_word)
        ##print lemma_sentence
        noun_chunks = sentence.get_noun_chunks(lemma_sentence)    

        ##print noun_chunks
        ##print 'In solve for all labels'
        possible_subjects = []
        possible_object = None
        quantified_entities = sentence.m_question.get_quantified_entities()
        for noun in noun_chunks:
            noun = noun.lower()
            noun_split = noun.split()
            if len(noun_split) > 1:
                ##print 'noun greater than 1'
                for non_allowed in sentence.NON_ALLOWED_NOUN_CHUNKS:
                    noun = noun.replace(non_allowed, '')
                noun = noun.strip()
                ##print 'replaced noun'
                ##print noun
            ##print noun
            noun_split = noun.split()
            ##print noun_split
            if noun in quantified_entities:
                possible_subjects.append(noun)
            elif possible_object == None and len(noun_split) == 1 and QuestionSentenceSolver.is_in_objects(quantified_entities, noun, False):
                ##print possible_object
                possible_object = noun
            elif QuestionSentenceSolver.is_a_complex_noun(sentence.m_complex_nouns, noun) and QuestionSentenceSolver.is_in_objects(quantified_entities, noun, True):
                ##print possible_object
                possible_object = noun

        ##print possible_object
        result = 0
        
#         for k,v in quantified_entities.items():
#             for e in v:
                #print k,":",e
        
        if possible_object == None:
            possible_object = QuestionSentenceSolver.process_noun_chunks(sentence, sentence.m_sentence_text, quantified_entities)
            #print 'possible object was none: now:', possible_object
        
        #string-matching
        if possible_object == None:
            if len(sentence.m_complex_nouns) > 0:
                possible_object = QuestionSentenceSolver.find_match_from_quantified_entities(sentence, quantified_entities)
            
        if possible_object != None:
            for subject in quantified_entities:
                all_objects_for_subject =  quantified_entities[subject]
                for object_for_subject in all_objects_for_subject:
                    try:
                        if object_for_subject.get_name() in possible_object:
                        # if possible_object == object_for_subject.get_name():
                            for transfer_transaction in object_for_subject.m_transfer_transactions:
                                if transfer_transaction.m_transferred_by_to != None and transfer_transaction.m_quantity > 0:
                                    ##print 'adding for ' + subject + str(transfer_transaction.m_quantity)
                                    result = result + transfer_transaction.m_quantity
                                elif transfer_transaction.m_transferred_by_to == None:
                                    ##print 'adding for ' + subject + str(-transfer_transaction.m_quantity)
                                    result = result + -transfer_transaction.m_quantity
                    except:
                        #print 'In exception line 45'
                        result = 0
        else:
            #add all quantities
            for k,v in quantified_entities.items():
                for e in v:
                    for transfer_transaction in e.m_transfer_transactions:
                        if transfer_transaction.m_transferred_by_to != None and transfer_transaction.m_quantity > 0:
                            ##print 'adding for ' + subject + str(transfer_transaction.m_quantity)
                            result = result + transfer_transaction.m_quantity
                        elif transfer_transaction.m_transferred_by_to == None:
                            ##print 'adding for ' + subject + str(-transfer_transaction.m_quantity)
                            result = result + -transfer_transaction.m_quantity
        return result
    
    @staticmethod
    def find_match_from_quantified_entities(sentence, quantified_entities):
        possible_object = None
        complex_nouns = sentence.m_complex_nouns
        for k,v in quantified_entities.items():
            for e in v:
                for complex_noun in complex_nouns:
                    quantity_name = e.get_name()
                    if complex_noun in quantity_name or quantity_name in complex_noun:
                        possible_object = complex_noun
                        break
        return possible_object
    
    @staticmethod
    def process_noun_chunks(sentence, text, quantified_entities):
        #print 'In process noun c'
        possible_object = None
        noun_chunks = sentence.get_noun_chunks(text)
        #print noun_chunks
        for noun in noun_chunks:
            noun = noun.lower()
            noun_split = noun.split()
            
                
            if len(noun_split) > 1:
                ##print 'noun greater than 1'
                for non_allowed in sentence.NON_ALLOWED_NOUN_CHUNKS:
                    noun = noun.replace(non_allowed, '')
                
                #print 'after non allowed:', noun
                
                noun = noun.strip()
                noun_split = noun.split()                
                lemmatized_chunk = ''
                if len(noun_split) > 1:
                    for n in noun_split:
                        lemmatized_chunk = sentence.LEMMATIZER_MODULE.lemmatize(n) + ' '
                    noun = lemmatized_chunk
                else:
                    noun = sentence.LEMMATIZER_MODULE.lemmatize(noun)
                #print 'final:', noun
                noun = noun.strip()
            else:
                noun = sentence.LEMMATIZER_MODULE.lemmatize(noun)
                #print 'replaced noun'
                ##print noun
            ##print noun
            noun_split = noun.split()
            ##print noun_split
            
            if possible_object == None and len(noun_split) == 1 and QuestionSentenceSolver.is_in_objects(quantified_entities, noun, False):
                ##print possible_object
                possible_object = noun
            elif QuestionSentenceSolver.is_a_complex_noun(sentence.m_complex_nouns, noun) and QuestionSentenceSolver.is_in_objects(quantified_entities, noun, True):
                ##print possible_object
                possible_object = noun
        return possible_object
    
    @staticmethod
    def is_in_objects(quantified_entities, ex_object, is_complex_noun):
        ##print "in is in objects"
        ##print ex_object
        ##print quantified_entities.values()
        for v in quantified_entities.values():
            for subjects_object in v:
                if not is_complex_noun and subjects_object.get_name() == ex_object:
                    return True
                elif is_complex_noun and subjects_object.get_name() in ex_object:
                    return True
        return False

    @staticmethod
    def is_a_complex_noun(complex_nouns, ex_object):
        ##print "in is complex noun"
        ##print complex_nouns
        for v in complex_nouns:
            if v == ex_object:
                return True
        return False

    @staticmethod
    def solve_for_plus_label(sentence):

        quantified_entities = sentence.m_question.get_quantified_entities()
        possible_subjects = []
        possible_object = None
        # sentence_split = sentence.m_sentence_text.split()
        for word in sentence.m_sentece_words:
            word = word.lower()
            pos = sentence.m_words_pos[word]
            #print pos
            word = sentence.LEMMATIZER_MODULE.lemmatize(word)
            if pos == 'NNP':
                if word in quantified_entities:
                    possible_subjects.append(word)
            elif pos == 'PRP':
                print 'in prp'
                print sentence.m_processed_pronoun
                word = sentence.m_processed_pronoun
                print word
                if word in quantified_entities:
                    possible_subjects.append(word)
            elif pos == 'NN' or pos == 'NNS':
                if possible_object == None and QuestionSentenceSolver.is_in_objects(quantified_entities, word, False):
                    possible_object = word
    
        result = 0
        
        print 'possible object',possible_object
        print 'possible subjects',possible_subjects
        # if len(possible_subjects) == 1:
        if possible_object != None:
#             compound_quantity_found = QuestionSentenceSolver.compound_modifier_exists(sentence, possible_object)
            compound_quantity_found = None
            if compound_quantity_found != None:
                return compound_quantity_found
            else:
                if len(possible_subjects) > 0:
                    subject = possible_subjects[0]
                    if subject in quantified_entities:
                        subjects_object_entities = quantified_entities[subject]
        
                        for subjects_object_entity in subjects_object_entities:
    #                         #print 'during comparison'
    #                         #print subjects_object_entity
    #                         #print possible_object
                            if subjects_object_entity.get_name() == possible_object:
                                result = subjects_object_entity.get_final_cardinal()
                                break
                    for k,v in quantified_entities.items():
                        if k == 'global':
                            for e in v:
                                if e.get_name() in possible_object or possible_object in e.get_name():
                                    #print 'In global entity'
                                    result = e.get_final_cardinal() - result                                
                                    result = -result if result < 0 else result
                    result = -result if result < 0 else result
                else:
                    for k,v in quantified_entities.items():
                        for e in v:
                            if e.get_name() in possible_object or possible_object in e.get_name():
                                if e.m_equal_to_state != None:
                                    return e.get_final_cardinal()
                                print e
                                result = result + e.get_final_cardinal()
                                print result
                    print 'result from only possible object,',result
        else:
    #             #print 'in all'
            # add all quantities
            global_entity_exists = None
            equal_to_quantity = None
            for k, v in quantified_entities.items():
                if k == 'global':
                    global_entity_exists = True                        
                else:
                    for e in v:
                        if e.m_equal_to_state != None and equal_to_quantity == None:
                            equal_to_quantity = e.m_equal_to_state
                        for transfer_transaction in e.m_transfer_transactions:
                            if transfer_transaction.m_transferred_by_to != None and transfer_transaction.m_quantity > 0:
                                # #print 'adding for ' + subject + str(transfer_transaction.m_quantity)
                                try:
                                    result = result + transfer_transaction.m_quantity
                                except:
                                    result = 0
    #                                 #print 'ERROR: transfer entity issue'
                            elif transfer_transaction.m_transferred_by_to == None:
                                # #print 'adding for ' + subject + str(-transfer_transaction.m_quantity)
                                try:
                                    result = result + -transfer_transaction.m_quantity
                                except:
                                    result = 0
                    
            if equal_to_quantity != None:
                result = equal_to_quantity - result                                
                result = -result if result < 0 else result
    #                                 #print 'ERROR: transfer entity issue'
            if global_entity_exists == True:
                for e in quantified_entities['global']:                    
                    #print 'In global entity'
                    result = e.get_final_cardinal() - result                                
                    result = -result if result < 0 else result
            
        return result

    @staticmethod
    def compound_modifier_exists(sentence, possible_object):
        quantity_found = None
        
        sentence_object_cm = None
        for sentence_m in sentence.m_compound_modifiers:
            if sentence_m.m_dobj == possible_object:
                sentence_object_cm = sentence_m
        
        print 'in compound modifier exists'
        if sentence_object_cm != None:
            quantified_entities = sentence.m_question.m_quantified_entities
            for k,v in quantified_entities.items():
                print 'key',k
                for e in v:
                    print 'q entity:', e.get_name()
                    quantity_compound_modifiers = e.m_compound_modifiers
                    for quantity_compound_modifier in quantity_compound_modifiers:
                        print 'quantity',quantity_compound_modifier
                        if e.get_name() == sentence_object_cm.m_dobj and sentence_object_cm.m_modifier == quantity_compound_modifier.m_modifier:
                            print 'match found'
                            quantity_found = quantity_compound_modifier.m_quantity
                            return quantity_found
                        
        return quantity_found