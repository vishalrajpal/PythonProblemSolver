import unittest
import json
from Question import Question

class SolverTests(unittest.TestCase):
    
    QUESTION_8 = {
        "ParentIndex": 8,
        "iIndex": 8,
        "lEquations": ["X = 4 + 9"],
        "lSolutions": ["13"],
        "sQuestion": "Joan went to 4 football games this year . She went to 9 games last year . How many football games did Joan go to in all ? ",
        "Sentences": [{
            "Sentence": "Joan went to 4 football games this year .",
            "SimplifiedSentences": [{
                "Sentence": "Joan went to 4 football games this year .",
                "label": "+",
                "PredictedLabel": "+",
                "SyntacticPattern": "NVPCNDN"
            }]
        }, {
            "Sentence": "She went to 9 games last year .",
            "SimplifiedSentences": [{
                "Sentence": "She went to 9 games last year .",
                "label": "+",
                "PredictedLabel": "+",
                "SyntacticPattern": "NVPCNAN"
            }]
        }, {
            "Sentence": "How many football games did Joan go to in all ?",
            "SimplifiedSentences": [{
                "Sentence": "How many football games did Joan go to in all ?",
                "label": "?",
                "PredictedLabel": "?",
                "SyntacticPattern": "WANVNVPPD"
            }]
        }]
    }
    
    def test_solver(self):
        question_json = json.dumps(SolverTests.QUESTION_8)  
        question_json_obj = json.loads(question_json)
        print question_json_obj["ParentIndex"] 
        new_question = Question(question_json_obj)
        new_question.solve()
        self.assertEquals(new_question.get_quantified_entities().get(0), "joan -> 13 games", "Joan football question fails.")
        
    if __name__ == '__main__':
        
        unittest.main()