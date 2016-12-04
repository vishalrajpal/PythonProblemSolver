import json
from Question import Question
from decimal import Decimal
class AnswerTests():
    
    TESTED_QUESTIONS_FILE_PATH = "TrainingDataQuestionLabeled_Plus.json"
#     TESTED_QUESTIONS_FILE_PATH = "Test.json"

    def __init__(self):
        print 'In init'
    
    def test_answers(self):
        with open(AnswerTests.TESTED_QUESTIONS_FILE_PATH) as test_data_file:    
            tested_questions = json.load(test_data_file)
        incorrect = 0
        
        for question in tested_questions:
#             print 'reading tested questions json'
            new_question = Question(question)
            answer = Decimal(new_question.solve())
            expected_answer = Decimal(question["lSolutions"][0])
#             print 'in tests'
#             print "actual answer:", float(answer)
#             print "expected answer:", float(expected_answer)

            
            if float(answer) != float(expected_answer):
                print str(question["ParentIndex"])
                incorrect = incorrect + 1
#                 print "ParentIndex:" + str(question["ParentIndex"])
#                 print "ERROR:" + " " + new_question.m_question
#                 print "ERROR:" + " Actual Answer " + str(answer)
#                 print "ERROR:" + " Expected Answer " + str(expected_answer)
#             self.assertEquals(str(answer), str(expected_answer), new_question.m_question)
#             else:
#                 print str(question["ParentIndex"])
        print 'Incorrect: ' + str(incorrect)