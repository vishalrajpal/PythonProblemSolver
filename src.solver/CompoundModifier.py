class CompoundModifier:
    
    def __init__(self, modifier, dobj):
        self.m_modifier = modifier
        self.m_dobj = dobj
        self.m_quantity = None
    
    def __str__(self):
        return str(self.m_quantity) + ' ' +self.m_modifier + ' ' + self.m_dobj

    def set_quantity(self, quantity):
        self.m_quantity = quantity