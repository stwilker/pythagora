"""
This file implements group structures for markets, including Community objects (groups of buyers) and
CommunitySet objects (groups of communities).
"""


class Community:
    """
    A Community is a group of buyers.
    """

    def __init__(self, list_of_buyers, name):
        """
        Instantiates a community.
        @param list_of_buyers: buyers to add to community
        @param name: name to ID community in results analysis
        """
        self._list_of_buyers = list_of_buyers
        self._name = name

    @property
    def list_of_buyers(self):
        """List of buyers that belong to this community"""
        return self._list_of_buyers

    @list_of_buyers.setter
    def list_of_buyers(self, new_list):
        self._list_of_buyers = new_list

    @property
    def name(self):
        """Community name"""
        return self._name

    def add_buyer(self, buyer):
        self._list_of_buyers.append(buyer)
        buyer.community = self._name

    def __str__(self):
        printer = "Community " + str(self._name) + "\n"
        for b in self._list_of_buyers:
            printer = printer + b.__str__() + "\n"
        return printer


class CommunitySet:
    """
    A CommunitySet is a group of communities.
    """

    def __init__(self, list_of_communities, assemblage):
        """
        Instantiates a CommunitySet.
        @param list_of_communities: communities to add to group
        @param assemblage: items for sale in this market
        """
        self._list_of_communities = list_of_communities
        self._assemblage = assemblage

    @property
    def list_of_communities(self):
        """List of all communities in this group"""
        return self._list_of_communities

    def add_community(self, new_community):
        """
        Add a community to the group.
        @param new_community: community to add
        """
        self._list_of_communities.append(new_community)

    @property
    def assemblage(self):
        """List of pots available in market."""
        return self._assemblage

    def get_all_buyers_in_community_set(self):
        """
        Returns a list of all buyers in all communities in this CommunitySet.
        @return: a list of all buyers in all communities in this CommunitySet
        """
        buyers = []
        for community in self._list_of_communities:
            c_buyers = community.list_of_buyers
            for b in c_buyers:
                buyers.append(b)
        return buyers

    def add_buyer_to_community_by_name(self, buyer, community):
        """
        Adds a specific buyer to a specific community using their name variables.
        @param buyer: name of target buyer
        @param community: name of community to which to add buyer
        """
        for c in self._list_of_communities:
            if c.name == community.name:
                community.add_buyer(buyer)

    def add_buyer_to_community_by_index(self, buyer, index):
        """
        Adds a specific buyer to a specific community using a community index.
        @param buyer: name of target buyer
        @param index: index of community to which to add buyer
        """
        comm = self._list_of_communities[index]
        comm.add_buyer(buyer)

    def number_of_communities(self):
        """
        Returns the number of communities.
        @return: the number of communities.
        """
        return len(self._list_of_communities)

    def more_than_min_communities(self, min_number):
        """
        Checks if the number of communities is above a certain threshold.
        @param min_number: minimum number of communities
        @return: True if number of communities is at least min_number; False otherwise
        """
        if len(self._list_of_communities) >= min_number:
            return True
        else:
            return False

    def __str__(self):
        return_str = "Total number of communities: " + str(
            len(self._list_of_communities)) + "\n" + "Size of each community: \n"
        for comm in self._list_of_communities:
            return_str = return_str + "Community " + str(comm.name) + " size: " + str(len(comm.list_of_buyers)) + "\n"
        return return_str
