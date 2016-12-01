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
            if noun in quantified_entities:
                possible_subjects.append(noun)
            elif possible_object == None and QuestionSentenceSolver.is_in_objects(quantified_entities, noun):
                possible_object = noun
        
        result = 0
        
        for subject in quantified_entities:
            if subject in sentence.m_question.m_proper_nouns:
                all_objects_for_subject =  quantified_entities[subject]
                for object_for_subject in all_objects_for_subject:
                    if possible_object == object_for_subject.get_name():
                        print 'adding'
                        result = result + object_for_subject.m_cardinal
        print result
        return result
    
    @staticmethod
    def is_in_objects(quantified_entities, ex_object):
        for v in quantified_entities.values():
            for subjects_object in v:
                if subjects_object.get_name() == ex_object:
                    return True
        return False