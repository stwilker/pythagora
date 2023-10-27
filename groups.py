#from agents import Buyer

class Community:

    def __init__(self, list_of_buyers, name):
        self._list_of_buyers = list_of_buyers
        self._name = name
    
    @property
    def list_of_buyers(self):
      '''List of buyers that belong to this community'''
      return self._list_of_buyers

    @list_of_buyers.setter
    def list_of_buyers(self, new_list):
      self._list_of_buyers = new_list
    
    @property
    def name(self):
      '''Community name'''
      return self._name
    
    def add_buyer(self, buyer):
        self._list_of_buyers.append(buyer)
        buyer.community = self._name

    def __str__(self):
      printer = "Community " + str(self._name) + "\n"
      for b in self._list_of_buyers:
        printer = printer + b.__str__() + "\n"
      return printer

class GroupOfCommunities:

    def __init__ (self, list_of_communities, assemblage):
            self._list_of_communities = list_of_communities
            self._assemblage = assemblage
    
    @property
    def list_of_communities(self):
        '''List of all communities in this group'''
        return self._list_of_communities
    
    def add_community(self, new_community):
      self._list_of_communities.append(new_community)

    @property
    def assemblage(self):
      '''List of pots available in marketspace.'''
      return self._assemblage
    
    def get_all_buyers_in_group(self):
      buyers = []
      for community in self._list_of_communities:
        c_buyers = community.list_of_buyers
        for b in c_buyers:
          buyers.append(b)
      return buyers

    def add_buyer_to_community_by_name(self, buyer, community):
      for c in self._list_of_communities:
        if c.name == community.name:
          community.add_buyer(buyer)
    
    def add_buyer_to_community_by_index(self, buyer, index):
      comm = self._list_of_communities[index]
      comm.add_buyer(buyer)
    
    def number_of_communities(self):
        return len(self._list_of_communities)
   
    def more_than_min_communities(self, min_number):
        #is comms more than min number?
        if len(self._list_of_communities) >= min_number:
            return True
        else:
            return False

    def __str__(self):
        return_str = "Total number of communities: " + str(len(self._list_of_communities)) + "\n" + "Size of each community: \n"
        for comm in self._list_of_communities:
            return_str = return_str + "Community " + str(comm.name) + " size: " + str(len(comm.list_of_buyers)) + "\n"  
        return return_str