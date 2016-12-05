class QuantifiedNonEntity:
    
    
    def __init__(self, quantity):
        self.m_quantity = quantity
        self.m_owner_entity = None
        
    def set_owner_entity(self, entity):
        self.m_owner_entity = entity