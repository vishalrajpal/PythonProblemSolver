import json
from Question import Question
from decimal import Decimal
class AnswerTests():
    TESTED_QUESTIONS_FILE_PATH = "TrainingDataQuestionLabeled_All.json"
#     TESTED_QUESTIONS_FILE_PATH = "TrainingDataQuestionLabeled_Plus.json"
#     TESTED_QUESTIONS_FILE_PATH = "Test.json"
#     TESTED_QUESTIONS_FILE_PATH = "TrainingDataQuestionLabeled_C.json"
#     TESTED_QUESTIONS_FILE_PATH = "TestDataQuestionLabeled.json"
    def __init__(self):
        print 'In init'
    
    def test_answers(self):
        with open(AnswerTests.TESTED_QUESTIONS_FILE_PATH) as test_data_file:    
            tested_questions = json.load(test_data_file)
        incorrect = 0
        incorrects = []
        neg_count = []
        zero_count = []
        for question in tested_questions:
#             print 'reading tested questions json'
            new_question = Question(question)
            answer = Decimal(new_question.solve())
            expected_answer = Decimal(question["lSolutions"][0])
            print 'in tests'
            print "actual answer:", float(answer)
            print "expected answer:", float(expected_answer)
            
            if answer == 0.0:  
                print 'in answer 0'   
                answer = self.get_answer_from_quants(new_question)
                
                print 'new answer', answer
            print float(answer) != float(expected_answer)
            print Decimal(answer) != Decimal(expected_answer)
            print round(answer,2) == round(expected_answer,2)
            if float(answer) == float(expected_answer) or round(answer,2) == round(expected_answer,2):
                'just'
            else:
                parent_index = str(question["ParentIndex"])
                if answer == 0.0:
                    zero_count.append(parent_index)
                elif answer < 0:
                    neg_count.append(parent_index)
                print str(question["ParentIndex"])
                incorrects.append(str(question["ParentIndex"]))
                incorrect = incorrect + 1
#                 print "ParentIndex:" + str(question["ParentIndex"])
#                 print "ERROR:" + " " + new_question.m_question
#                 print "ERROR:" + " Actual Answer " + str(answer)
#                 print "ERROR:" + " Expected Answer " + str(expected_answer)
#             self.assertEquals(str(answer), str(expected_answer), new_question.m_question)
#             else:
#                 print str(question["ParentIndex"])
        print 'Incorrect: ' + str(incorrect)
        print incorrects
        print 'zero count',len(zero_count)
        print 'zero count:', zero_count
        print 'neg count',len(neg_count)
        print 'neg_count:', neg_count
        
        
    def get_answer_from_quants(self, new_question):
        rest_sum = 0
        equal_to_sum = 0
        question_sentences = new_question.m_sentences
        for sentence in question_sentences:
            print sentence.m_cardinal
            if sentence.m_cardinal != None and sentence.m_cardinal != 'X' and sentence.m_cardinal != '-X':
                if sentence.m_predicted_label == '=':
                    equal_to_sum = equal_to_sum + sentence.m_cardinal
                else:
                    rest_sum = rest_sum + sentence.m_cardinal
        
        answer = 0
        if equal_to_sum == 0:
            answer = rest_sum
        else:
            answer = equal_to_sum - rest_sum
            answer = answer if answer > 0 else -answer
        return answer