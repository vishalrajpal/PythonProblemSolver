import json
import csv

class QuestionSentencesLabeler:
    
    def __init__(self):
        self.m_question_label_map = {}
        self.m_question_count_map = {}
        self.initializeLabelQuestionMap()
        for k,v in self.m_question_label_map.items():
            if v == 'c':
                print k + ' --Count:' + str(self.m_question_count_map[k])
        self.labelQuestionSentences()
    
    def initializeLabelQuestionMap(self):
        with open('QuestionTestData.csv', 'rb') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                if row[1] not in self.m_question_label_map:
                    self.m_question_label_map[row[1]] = row[0]
                    self.m_question_count_map[row[1]] = 1
                elif self.m_question_label_map[row[1]] != row[0]:
                    print 'error'
                    print row[1]
                    print 'current' + self.m_question_label_map[row[1]]
                    print 'new' + row[0]
                else:
                    self.m_question_count_map[row[1]] = self.m_question_count_map[row[1]] + 1
                    
            
        
    def labelQuestionSentences(self):
        self.m_test_dataset_file = "/Users/acharya.n/Desktop/ArithmeticProblemSolver/target/classes/dataset/TestDataPredicted.json"
        with open(self.m_test_dataset_file) as data_file:
            data = json.load(data_file)
            
        question_label_data = []
        for question in data:
            sentences = question["Sentences"]
            for sentence in sentences:
                simplified_sentences = sentence["SimplifiedSentences"]
                for simplified_sentence in simplified_sentences:
                    current_sentence_label = simplified_sentence["label"]
                    # simplified_sentence["PredictedLabel"] = current_sentence_label
                    if current_sentence_label == '?':
                        current_sentence_text = simplified_sentence["Sentence"]
                        simplified_sentence["QuestionLabel"] = self.m_question_label_map[current_sentence_text]
                        # if simplified_sentence["QuestionLabel"] == 'c':
                        question_label_data.append(question)
        with open("TestDataQuestionLabeled.json", 'w') as data_file:
            data = json.dump(question_label_data, data_file)
            
    def extract_faulters(self):
        all_faulters = [25,26,29,34,35,45,51,53,88,111,112,126,127,138,140,144,146,152,156,158,161,163,168,170,172,183,187,194,198,200,206,211,233,234,243,245,261,262,264,267,269,271,279,297,301,314,316,320,326,338,356,359,360,363,390,422,425,426,432,445,455,461,464,472,481,482,486,487,515,517,531,532,538,549,557,579,580,599,620,636,677,702,703,719,720,735,741,742,743,746,749,750,753,775,779,783,785,790,796,807,817,829,830,838,839,841,857,858,863,864,865,867,905,906,907,909,1068,1070,1075,1081,1082,1083,1089,1123,1125,1153,1161,1166,1194,1200,1212,1216,1217]
        with open("/Users/rajpav/git/ArithmeticProblemSolver/target/classes/dataset/TrainingDataQuestionLabeled_All.json") as data_file:
            data = json.load(data_file)
        
        total_count = 0
        count_map = {}
        for question in data:
            parentIndex = int(question["ParentIndex"])
            sentences = question["Sentences"]
            if parentIndex in all_faulters:
                for sentence in sentences:
                    simplified_sentences = sentence["SimplifiedSentences"]
                    for simplified_sentence in simplified_sentences:
                        current_sentence_label = simplified_sentence["label"]                        
                        if current_sentence_label == '?':
                            current_sentence_text = simplified_sentence["Sentence"]
                            if current_sentence_text in count_map:
                                count_map[current_sentence_text] = count_map[current_sentence_text] + 1
                            else:
                                count_map[current_sentence_text] = 1
            
        for k,v in count_map.items():
            total_count = total_count + int(v)
            print k,":",v
        
        print "Total:",total_count