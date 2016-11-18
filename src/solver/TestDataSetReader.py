import json
from Question import Question

class TestDataSetReader:
        
    def __init__(self):
        self.m_test_dataset_file = "Test.json"
        #self.m_test_dataset_file = "/Users/rajpav/git/ArithmeticProblemSolver/target/classes/dataset/TestDataPredicted.json"
        
    def read_test_dataset(self):
        
        with open(self.m_test_dataset_file) as test_data_file:    
            test_data = json.load(test_data_file)
        
        print 'In test data set reader'
        questions = []
        for question in test_data:
            print 'reading json'
            new_question = Question(question)
            questions.append(new_question)
            
        for question in questions:
            question.solve()
            
#         print questions