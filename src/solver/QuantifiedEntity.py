class QuantifiedEntity:
    
    def __init__(self, cardinal, object_dependency, object):
        self.m_cardinal = cardinal
        self.m_object_dependecy = object_dependency
        self.m_object = object
        self.m_transactions = []

    def __str__(self):
        return "{} -> {} {}".format(self.m_owner_entity.get_name(), self.m_cardinal, self.m_object)
    
    def set_owner_entity(self, owner_entity):
        self.m_owner_entity = owner_entity
        
    def get_owner_entity(self):
        return self.m_owner_entity
        
    def perform_operation(self, value):
        self.m_cardinal = self.m_cardinal + value
        self.m_transactions.append(value)
        
    def get_name(self):
        return self.m_object