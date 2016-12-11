from QuestionSentenceSolver import QuestionSentenceSolver

class UnknownSentenceSolver:
    
    @staticmethod
    def solve_for_unknown_label(sentence):
        result = 0
        q = sentence.m_question
        equal_to_val = 0

        for sentence in q.m_sentences:

            if sentence.m_predicted_label == '+' or sentence.m_predicted_label == "-":
                if sentence.m_cardinal == 'X' or sentence.m_cardinal == '-X':
                    continue
                result = result + sentence.m_cardinal
            elif sentence.m_predicted_label == '=':
                if sentence.m_cardinal == 'X' or sentence.m_cardinal == '-X':
                    continue
                equal_to_val = equal_to_val + sentence.m_cardinal

        if equal_to_val != 0:
            result = equal_to_val - result if equal_to_val > result else result - equal_to_val

        return result