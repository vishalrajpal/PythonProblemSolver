import json
import csv

class QuestionSentencesLabeler:
    
    def __init__(self):
        self.m_question_label_map = {}
        self.m_question_count_map = {}
        self.initializeLabelQuestionMap()
        for k,v in self.m_question_label_map.items():
            if v == '+':
                print k + ' --Count:' + str(self.m_question_count_map[k])
        #self.labelQuestionSentences()
    
    def initializeLabelQuestionMap(self):
        with open('QuestionTrainingData.csv', 'rb') as csvfile:    
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                if row[2] not in self.m_question_label_map:
                    self.m_question_label_map[row[2]] = row[1]
                    self.m_question_count_map[row[2]] = 1                   
                elif self.m_question_label_map[row[2]] != row[1]:
                    print 'error'
                    print row[2]
                    print 'current' + self.m_question_label_map[row[2]]
                    print 'new' + row[1]
                else:
                    self.m_question_count_map[row[2]] = self.m_question_count_map[row[2]] + 1
                    
            
        
    def labelQuestionSentences(self):
        self.m_test_dataset_file = "/Users/rajpav/git/ArithmeticProblemSolver/target/classes/dataset/TrainingData.json"
        with open("/Users/rajpav/git/ArithmeticProblemSolver/target/classes/dataset/TrainingData.json") as data_file:    
            data = json.load(data_file)
         
        for question in data:
            sentences = question["Sentences"]
            for sentence in sentences:
                simplified_sentences = sentence["SimplifiedSentences"]
                for simplified_sentence in simplified_sentences:
                    current_sentence_label = simplified_sentence["label"]
                    if current_sentence_label == '?':
                        current_sentence_text = simplified_sentence["Sentence"]
                        simplified_sentence["QuestionLabel"] = self.m_question_label_map[current_sentence_text]

        with open("/Users/rajpav/git/ArithmeticProblemSolver/target/classes/dataset/TrainingDataQuestionLabeled.json", 'w') as data_file:    
            data = json.dump(data, data_file)