class QuestionSentenceSolver:
    
    @staticmethod
    def solve_for_all_label(sentence):
        sentence_split = sentence.m_sentence_text.split()
        lemma_sentence = ''
        for sentence_split_word in sentence_split:
            lemma_sentence = lemma_sentence + ' ' + sentence.LEMMATIZER_MODULE.lemmatize(sentence_split_word)
        print lemma_sentence
        noun_chunks = sentence.get_noun_chunks(lemma_sentence)    

        print noun_chunks
        print 'In solve for all labels'
        possible_subjects = []
        possible_object = None
        quantified_entities = sentence.m_question.get_quantified_entities()
        for noun in noun_chunks:
            noun = noun.lower()
            noun_split = noun.split()
            if len(noun_split) > 1:
                print 'noun greater than 1'
                for non_allowed in sentence.NON_ALLOWED_NOUN_CHUNKS:
                    noun = noun.replace(non_allowed, '')
                noun = noun.strip()
                print 'replaced noun'
                print noun
            print noun
            noun_split = noun.split()
            print noun_split
            if noun in quantified_entities:
                possible_subjects.append(noun)
            elif possible_object == None and len(noun_split) == 1 and QuestionSentenceSolver.is_in_objects(quantified_entities, noun, False):
                print possible_object
                possible_object = noun
            elif QuestionSentenceSolver.is_a_complex_noun(sentence.m_complex_nouns, noun) and QuestionSentenceSolver.is_in_objects(quantified_entities, noun, True):
                print possible_object
                possible_object = noun

        print possible_object
        result = 0
        
        for subject in quantified_entities:
            all_objects_for_subject =  quantified_entities[subject]
            for object_for_subject in all_objects_for_subject:
                if object_for_subject.get_name() in possible_object:
                # if possible_object == object_for_subject.get_name():
                    for transfer_transaction in object_for_subject.m_transfer_transactions:
                        if transfer_transaction.m_transferred_by_to != None and transfer_transaction.m_quantity > 0:
                            print 'adding for ' + subject + str(transfer_transaction.m_quantity)
                            result = result + transfer_transaction.m_quantity
                        elif transfer_transaction.m_transferred_by_to == None:
                            print 'adding for ' + subject + str(-transfer_transaction.m_quantity)
                            result = result + -transfer_transaction.m_quantity
                            
        
#         for subject in quantified_entities:
#             all_objects_for_subject =  quantified_entities[subject]
#             for object_for_subject in all_objects_for_subject:
#                 if object_for_subject.is_transfer_entity() == False and possible_object == object_for_subject.get_name():
#                     print 'adding for ' + subject + str(object_for_subject.m_cardinal)
#                     result = result + object_for_subject.m_cardinal
        print result
        return result
    
    @staticmethod
    def is_in_objects(quantified_entities, ex_object, is_complex_noun):
        print "in is in objects"
        print ex_object
        print quantified_entities.values()
        for v in quantified_entities.values():
            for subjects_object in v:
                if not is_complex_noun and subjects_object.get_name() == ex_object:
                    return True
                elif is_complex_noun and subjects_object.get_name() in ex_object:
                    return True
        return False

    @staticmethod
    def is_a_complex_noun(complex_nouns, ex_object):
        print "in is complex noun"
        print complex_nouns
        for v in complex_nouns:
            if v == ex_object:
                return True
        return False

    @staticmethod
    def solve_for_plus_label(sentence):
        # sentence_split = sentence.m_sentence_text.split()
        # lemma_sentence = ''
        # for sentence_split_word in sentence_split:
        #     lemma_sentence = lemma_sentence + ' ' + sentence.LEMMATIZER_MODULE.lemmatize(sentence_split_word)
        # print lemma_sentence
        # noun_chunks = sentence.get_noun_chunks(sentence)
        #
        # print noun_chunks
        # print 'In solve for plus labels'
        # possible_subjects = []
        # possible_object = None
        # quantified_entities = sentence.m_question.get_quantified_entities()
        # for noun in noun_chunks:
        #     noun = noun.lower()
        #     noun_split = noun.split()
        #     if len(noun_split) > 1:
        #         print 'noun greater than 1'
        #         for non_allowed in sentence.NON_ALLOWED_NOUN_CHUNKS:
        #             noun = noun.replace(non_allowed, '')
        #         noun = noun.strip()
        #         print 'replaced noun'
        #         print noun
        #     print noun

        quantified_entities = sentence.m_question.get_quantified_entities()
        possible_subjects = []
        possible_object = None
        sentence_split = sentence.m_sentence_text.split()
        for word in sentence_split:
            word = word.lower()
            pos = sentence.m_words_pos[word]
            print pos
            word = sentence.LEMMATIZER_MODULE.lemmatize(word)
            if pos == 'NNP':
                if word in quantified_entities:
                    possible_subjects.append(word)
            elif pos == 'PRP':
                word = sentence.m_processed_pronoun
                if word in quantified_entities:
                    possible_subjects.append(word)
            elif pos == 'NN' or pos == 'NNS':
                if possible_object == None and QuestionSentenceSolver.is_in_objects(quantified_entities, word, False):
                    possible_object = word

        result = 0
        if len(possible_subjects) == 1:
            subject = possible_subjects[0]
            if subject in quantified_entities:
                subjects_object_entities = quantified_entities[subject]

                for subjects_object_entity in subjects_object_entities:
                    print 'during comparison'
                    print subjects_object_entity
                    print possible_object
                    if subjects_object_entity.get_name() == possible_object:
                        result = subjects_object_entity.m_cardinal
                        break


        return result
