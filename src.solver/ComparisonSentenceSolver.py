class ComparisonSentenceSolver:

    @staticmethod
    def solve_for_c_label(sentence):
        result = 0
        quantified_entities = sentence.m_question.get_quantified_entities()
        global_entity_found = False
        exclude_quantities = []
        for k, v in quantified_entities.items():
            if k == 'global':
                global_entity_found = True
            for e in v:
                for transfer_transaction in e.m_transfer_transactions:
                    current_quant = transfer_transaction.m_quantity if transfer_transaction.m_quantity > 0 else -transfer_transaction.m_quantity
                    if current_quant in exclude_quantities:
                        exclude_quantities.remove(current_quant)
                        continue
                    result = current_quant - result
                    if transfer_transaction.m_transferred_by_to != None:
                        exclude_quantities.append(current_quant)

        result = -result if result < 0 else result

        for non_quantified_entity in sentence.m_question.m_quantified_non_entities:
            current_quant = non_quantified_entity.m_quantity if non_quantified_entity.m_quantity > 0 else -non_quantified_entity.m_quantity
            print 'quantified non quantitiy:',current_quant
            result = current_quant - result

        result = -result if result < 0 else result

        if global_entity_found:
            global_entity = quantified_entities['global']
            for e in global_entity:
                result = e.get_final_cardinal() - result

        result = -result if result < 0 else result

        return result



        possible_subjects = []
        possible_object = None
        found_comparator = False
        # sentence_split = sentence.m_sentence_text.split()
        for word in sentence.m_sentece_words:
            word = word.lower()
            pos = sentence.m_words_pos[word]
            # print pos
            word = sentence.LEMMATIZER_MODULE.lemmatize(word)
            if pos == 'NNP':
                if word in quantified_entities:
                    possible_subjects.append(word)
            elif pos == 'JJR':
                # print "found comparator"
                found_comparator = True
            elif pos == 'NN' or pos == 'NNS':
                possible_object = word

        if found_comparator == True and len(possible_subjects) > 0 and possible_object != None:
            print possible_subjects
            print possible_object
            if len(possible_subjects) == 2:
                # print 'compare object in two subjects'
                object_count_for_subject_1 = None
                object_count_for_subject_2 = None

                for k,v in quantified_entities.items():
                    if k == possible_subjects[0]:
                        for e in v:
                            if e.get_name() == possible_object:
                                object_count_for_subject_1 = e.get_final_cardinal()
                    elif k == possible_subjects[1]:
                        for e in v:
                            if e.get_name() == possible_object:
                                object_count_for_subject_2 = e.get_final_cardinal()

                result = object_count_for_subject_1 - object_count_for_subject_2
                return -result if result < 0 else result



        return 0