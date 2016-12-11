import unicodedata

class Entity:
    
    def __init__(self, object_dependency, name):
        self.m_object_dependency = object_dependency
        self.m_name = name
        
    def __str__(self):
        if self.m_name == None:
            return None
        else:
            return self.m_name.lower()
        
    def get_name(self):
        try:
            return unicodedata.normalize('NFKD', self.m_name).encode('ascii', 'ignore').lower()
        except:
#             print 'In exception: Entity getname'
            return None