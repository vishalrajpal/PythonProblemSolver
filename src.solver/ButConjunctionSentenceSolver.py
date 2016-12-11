from QuestionSentenceSolver import QuestionSentenceSolver

class ButConjunctionSentenceSolver:
    
    @staticmethod
    def solve_for_but_label(sentence):
        quantified_entities = sentence.m_question.get_quantified_entities()
        possible_subjects = []
        possible_object = None
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
        
        
        result = ButConjunctionSentenceSolver.get_result_for_subject_and_object(possible_subjects, possible_object, sentence)
        return result
    
    
    @staticmethod
    def get_result_for_subject_and_object(possible_subjects, possible_object, sentence):
        result = 0
        print 'possible object',possible_object
        print 'possible subjects',possible_subjects
        if possible_object != None:
            if len(possible_subjects) > 0:
                result = ButConjunctionSentenceSolver.result_with_possible_object_and_subjects(possible_subjects, possible_object, sentence)                
            else:
                result = ButConjunctionSentenceSolver.result_with_possible_object(possible_object, sentence)
                print 'result from only possible object,',result
        else:
            result = ButConjunctionSentenceSolver.result_with_no_possible_object(sentence)
            
        return result
    
    @staticmethod
    def result_with_possible_object_and_subjects(possible_subjects, possible_object, sentence):
        quantified_entities = sentence.m_question.get_quantified_entities()
        subject = possible_subjects[0]
        if subject in quantified_entities:
            subjects_object_entities = quantified_entities[subject]

            for subjects_object_entity in subjects_object_entities:
                if subjects_object_entity.get_name() == possible_object:
                    result = subjects_object_entity.get_final_cardinal()
                    break
        for k,v in quantified_entities.items():
            if k == 'global':
                for e in v:
                    if e.get_name() in possible_object or possible_object in e.get_name():
                        result = e.get_final_cardinal() - result                                
                        result = -result if result < 0 else result
        result = -result if result < 0 else result
        return result
    
    @staticmethod
    def result_with_possible_object(possible_object, sentence):
        result = 0
        quantified_entities = sentence.m_question.get_quantified_entities()
        for k,v in quantified_entities.items():
            for e in v:
                if e.get_name() in possible_object or possible_object in e.get_name():
                    if e.m_equal_to_state != None:
                        return e.get_final_cardinal()
                    result = result + e.get_final_cardinal()
        return result
    
    @staticmethod
    def result_with_no_possible_object(sentence):
        result = 0
        quantified_entities = sentence.m_question.get_quantified_entities()
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
                            try:
                                result = result + transfer_transaction.m_quantity
                            except:
                                result = 0
                        elif transfer_transaction.m_transferred_by_to == None:
                            try:
                                result = result + -transfer_transaction.m_quantity
                            except:
                                result = 0
                
        if equal_to_quantity != None:
            result = equal_to_quantity - result                                
            result = -result if result < 0 else result
            
        if global_entity_exists == True:
            for e in quantified_entities['global']:                    
                result = e.get_final_cardinal() - result                                
            result = -result if result < 0 else result
        return result
                
                