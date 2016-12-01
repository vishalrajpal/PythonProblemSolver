class QuantifiedEntity:
    
    def __init__(self, cardinal, object_dependency, q_object, is_transfer_entity):
        self.m_cardinal = cardinal
        self.m_object_dependecy = object_dependency
        self.m_object = q_object.lower()
        self.m_transactions = []
        self.m_transfer_transactions = []
        self.m_is_transfer_entity = is_transfer_entity
        self.m_owner_entity = None
        self.m_equal_to_state = None
        #print self.__str__()

    def __str__(self):
        if self.m_equal_to_state != None:
            return "{} -> {} = {} {}".format(self.m_owner_entity.get_name(), self.m_cardinal, self.m_equal_to_state, self.m_object)
        else:
            return "{} -> {} {}".format(self.m_owner_entity.get_name(), self.m_cardinal, self.m_object)
    
    def set_owner_entity(self, owner_entity):
        self.m_owner_entity = owner_entity
        
    def get_owner_entity(self):
        return self.m_owner_entity
        
    def perform_operation(self, value, has_an_unknown_entity, transfer_transaction):
        if (has_an_unknown_entity or type(self.m_cardinal) is str):
            self.m_cardinal = str(self.m_cardinal) + " + " + str(value)
        else:
            self.m_cardinal = self.m_cardinal + value
            self.m_transfer_transactions.append(transfer_transaction)
        self.m_transactions.append(value)
        
    def add_transfer_transaction(self, transfer_transaction):
        self.m_transfer_transactions.append(transfer_transaction)

    def get_name(self):
        return self.m_object
    
    def is_transfer_entity(self):
        return self.m_is_transfer_entity
    
    def get_cardinal(self):
        return self.m_cardinal
    
    def set_equal_to_state(self, value):
        self.m_equal_to_state = value
        
    def get_str_rep(self):
        if self.m_equal_to_state != None:
            return self.m_owner_entity.get_name() + " -> " + str(self.m_cardinal) + " = " + str(self.m_equal_to_state) + " " + self.m_object 
        else:
            return self.m_owner_entity.get_name() + " -> " + str(self.m_cardinal) + " " + self.m_object