class Seller:

    def __init__(self, pot_type):
        self._pot_type = pot_type
    
    def __str__(self):
        return("Seller: " + self.pot_type)

    @property
    def pot_type(self):
      return self._pot_type
    
    @pot_type.setter
    def pot_type(self, new_pot_type):
        self._pot_type = new_pot_type

class Buyer:

    def __init__(self, intention, purchased_pot, community, name):
      self._intention = intention
      self._purchased_pot = purchased_pot
      self._community = community
      self._intention_history = [intention]
      self._purchase_history = [purchased_pot]
      self._name = name
    
    def __str__ (self):
      return("Name " + self._name + ", Intent: " + self._intention + ", Pot: " + self._purchased_pot + ", Community: " + self._community)
        
    @property
    def intention(self):
      '''Pot this buyer intends to buy next time.'''
      return self._intention
    
    @intention.setter
    def intention(self, new_intention):
      self._intention_history.append(self._intention)
      self._intention = new_intention

    @property
    def purchased_pot(self):
      '''Pot this buyer most recently purchased.'''
      return self._purchased_pot
    
    @purchased_pot.setter
    def purchased_pot(self, new_pot):
      self._purchase_history.append(self._purchased_pot)
      self._purchased_pot = new_pot
    
    @property
    def community(self):
      '''Community this buyer belongs to.'''
      return self._community
    
    @community.setter
    def community(self, new_community):
      self._community = new_community

    @property
    def name(self):
      '''Community this buyer belongs to.'''
      return self._name

    @property
    def intention_history(self):
      '''Buyer's history of intended purchases'''
      return self._intention_history

    @property
    def purchase_history(self):
      '''Buyer's history of purchases'''
      return self._purchase_history