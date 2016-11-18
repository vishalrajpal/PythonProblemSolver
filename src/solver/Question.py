from Sentence import Sentence

class Question:
    
    def __init__(self, question_json):
        print 'In constructor'
        self.m_question_json = question_json        
        self.m_entities = []
        self.m_quantified_entities = {}
        self.m_evaluating_sentence = None
        print self.m_evaluating_sentence
        self.read_sentences()
        
    def read_sentences(self):
        self.m_sentences = []
        sentences = self.m_question_json["Sentences"]
        for sentence in sentences:
            simplified_sentences = sentence["SimplifiedSentences"]
            for simplified_sentence in simplified_sentences:
                new_sentence = Sentence(simplified_sentence, self)
                self.m_sentences.append(new_sentence)

    def add_entity(self, entity):
        self.m_entities.append(entity)

    def add_quantified_entity(self, quantified_entity):
        quantity_exists = self.quantified_entity_exists(quantified_entity)
        if not quantity_exists:
            owner_entity = quantified_entity.get_owner_entity()
            self.m_quantified_entities[owner_entity.get_name()] = quantified_entity
        return quantity_exists
        
    def quantified_entity_exists(self, quantified_entity):
        owner_entity = quantified_entity.get_owner_entity()
        return owner_entity.get_name() in self.m_quantified_entities

    def set_evaluating_sentence(self, sentence):
        print 'In set evaluating sentence'
        self.m_evaluating_sentence = sentence
        print 'evaluating sentence'
        print self.m_evaluating_sentence

    def get_entities(self):
        return self.m_entities

    def get_quantified_entities(self):
        return self.m_quantified_entities

    def solve(self):
        print "In Solve"
        print self.m_evaluating_sentence
        for sentence in self.m_sentences:
            sentence.parse_sentence()
        
        if (self.m_evaluating_sentence != None):
            print self.m_evaluating_sentence.extract_result()
        else:
            print 'I don\'t have an evaluating sentence!'