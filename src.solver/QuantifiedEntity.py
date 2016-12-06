class QuantifiedEntity:
    
    def __init__(self, cardinal, object_dependency, q_object, is_transfer_entity):
        self.m_cardinal = cardinal
        self.m_object_dependecy = object_dependency
        self.m_object = q_object.lower()
        self.m_transactions = []
        self.m_transfer_transactions = []
        self.m_is_transfer_entity = is_transfer_entity
        self.m_has_an_unknown_quantity = False
        self.m_owner_entity = None
        self.m_equal_to_state = None
        self.m_compound_modifiers = []
        self.m_transactions.append(cardinal)
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
    
    def add_compound_modifier(self, compound_modifier):
        modifier_already_found = False
        print compound_modifier
        for a_modifier in self.m_compound_modifiers:
            if a_modifier.m_modifier == compound_modifier.m_modifier:
                print 'modifier has already been found'
                a_modifier_quantity = a_modifier.m_quantity
                c_modifier_quantity = compound_modifier.m_quantity
                a_modifier.m_quantity = a_modifier_quantity + c_modifier_quantity
                print 'a_modifier modified', a_modifier
                modifier_already_found = True
        if modifier_already_found == False:
            self.m_compound_modifiers.append(compound_modifier)
    
    def perform_operation(self, value, has_an_unknown_entity, transfer_transaction):
        if (has_an_unknown_entity or type(self.m_cardinal) is str):
            self.m_cardinal = str(self.m_cardinal) + " + " + str(value)
            self.m_has_an_unknown_quantity = True
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
    
    def get_final_cardinal(self):
#         print self.m_equal_to_state, self.m_has_an_unknown_quantity
        if self.m_equal_to_state == None and self.m_has_an_unknown_quantity == False:
            print 'in normal'
            return self.m_cardinal
        elif self.m_equal_to_state != None and self.m_has_an_unknown_quantity == False:
            print 'in no unknown and has equal:',self.m_equal_to_state - self.m_cardinal
            temp_res = self.m_equal_to_state - self.m_cardinal
            return -temp_res if temp_res < 0 else temp_res
        elif self.m_equal_to_state != None and self.m_has_an_unknown_quantity == True:
            print 'in both'
            all_result = 0
            for v in self.m_transactions:
                if v != 'X' and v!='-X':
                    all_result = all_result + float(v)
                    
            temp_res = self.m_equal_to_state - all_result
            return -temp_res if temp_res < 0 else temp_res
            
    def get_str_rep(self):
        if self.m_equal_to_state != None:
            return self.m_owner_entity.get_name() + " -> " + str(self.m_cardinal) + " = " + str(self.m_equal_to_state) + " " + self.m_object 
        else:
            return self.m_owner_entity.get_name() + " -> " + str(self.m_cardinal) + " " + self.m_object
