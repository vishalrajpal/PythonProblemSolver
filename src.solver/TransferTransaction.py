class TransferTransaction:
    
    def __init__(self, is_it_a_transfer, transferred_by_to, transferred_obj, quantity):
        self.m_is_it_a_transfer = is_it_a_transfer
        self.m_transferred_by_to = transferred_by_to
        self.m_transferred_obj = transferred_obj
        self.m_quantity = quantity
        
    def __str__(self):
        if self.m_transferred_by_to == None:
            return "Is this a Transfer: {} TransferedObj:{} {}".format(self.m_is_it_a_transfer, self.m_quantity, self.m_transferred_obj)
        else:
            return "Is this a Transfer: {} Transfered By: {} TransferedObj:{} {}".format(self.m_is_it_a_transfer, self.m_transferred_by_to, self.m_quantity,
                                                                       self.m_transferred_obj)