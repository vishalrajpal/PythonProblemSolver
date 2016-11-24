import unicodedata

class Entity:
    
    def __init__(self, object_dependency, name):
        self.m_object_dependency = object_dependency
        self.m_name = name
        
    def __str__(self):
        return self.m_name
        
    def get_name(self):
        return unicodedata.normalize('NFKD', self.m_name).encode('ascii', 'ignore').lower()