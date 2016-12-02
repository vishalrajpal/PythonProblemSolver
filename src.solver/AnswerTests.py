import json
from Question import Question

class AnswerTests():
    
    TESTED_QUESTIONS_FILE_PATH = "/Users/rajpav/git/ArithmeticProblemSolver/target/classes/dataset/error45.json"
    
    def __init__(self):
        print 'In init'
    
    def test_answers(self):
        with open(AnswerTests.TESTED_QUESTIONS_FILE_PATH) as test_data_file:    
            tested_questions = json.load(test_data_file)
        incorrect = 0
        
        for question in tested_questions:
            print 'reading tested questions json'
            new_question = Question(question)
            answer = new_question.solve()
            expected_answer = float(question["lSolutions"][0])
            print 'in tests'
            print "actual answer" + str(answer)
            print "expected answer" + str(expected_answer)

            
            if str(answer) != str(expected_answer):
                incorrect = incorrect + 1
                print "ParentIndex:" + str(question["ParentIndex"])
                print "ERROR:" + " " + new_question.m_question
                print "ERROR:" + " Actual Answer " + str(answer)
                print "ERROR:" + " Expected Answer " + str(expected_answer)
#             self.assertEquals(str(answer), str(expected_answer), new_question.m_question)
        
        print 'Incorrect: ' + str(incorrect)