'''
This module contains the constructors and all methods for agents in the marketplace.
There are currently two types of marketplace agents you can implement:

Agent: Seller
-------------
Sellers can be assigned a pot type (or other item, depending on your use case).
Seller functionality is currently limited as most network methods do not require
the assignment of sellers, only buyers.

Agent: Buyer
------------
Buyers are the primary agent in network models of marketplaces.
Buyers keep track of their purchase history, their currently assigned item,
and their intention on the next iteration of the market.
'''


class Seller:

    def __init__(self, pot_type):
        self._pot_type = pot_type

    def __str__(self):
        return "Seller: " + self.pot_type

    @property
    def pot_type(self):
        return self._pot_type

    @pot_type.setter
    def pot_type(self, new_pot_type):
        self._pot_type = new_pot_type


class Buyer:
    """
    Buyers are the primary agents in network models of marketplaces.
    Buyers keep track of their purchase history, their currently assigned item,
    and their intention on the next iteration of the market.

    Although the variable is labeled for the context of ancient ceramic marketspaces,
    the implementation is general. The items available for purchase in the marketspace
    are set in the `assemblage` variable of the algorithm initialization methods.
    """

    def __init__(self, intention, purchased_pot, community, name):
        """
        Creates a new buyer to be added to the marketspace.
        Note that buyers are created with fresh intention and purchase histories;
        on instantiation, the buyer histories contain only the intention and purchased_pot
        set in the constructor.

        @param intention: the item the buyer intends to purchase in the next epoch
        @param purchased_pot: the item the buyer most recently purchased
        @param community: the community to which the buyer belongs
        @param name: name assigned to ID buyer in later analysis
        """
        self._intention = intention
        self._purchased_pot = purchased_pot
        self._community = community
        self._intention_history = [intention]
        self._purchase_history = [purchased_pot]
        self._name = name

    def __str__(self):
        return (
                    "Name " + self._name + ", Intent: " + self._intention + ", Pot: " +
                    self._purchased_pot + ", Community: " + self._community)

    @property
    def intention(self):
        """Pot this buyer intends to buy next time."""
        return self._intention

    @intention.setter
    def intention(self, new_intention):
        self._intention_history.append(self._intention)
        self._intention = new_intention

    @property
    def purchased_pot(self):
        """Pot this buyer most recently purchased."""
        return self._purchased_pot

    @purchased_pot.setter
    def purchased_pot(self, new_pot):
        self._purchase_history.append(self._purchased_pot)
        self._purchased_pot = new_pot

    @property
    def community(self):
        """Community this buyer belongs to."""
        return self._community

    @community.setter
    def community(self, new_community):
        self._community = new_community

    @property
    def name(self):
        """Community this buyer belongs to."""
        return self._name

    @property
    def intention_history(self):
        """Buyer's history of intended purchases"""
        return self._intention_history

    @property
    def purchase_history(self):
        """Buyer's history of purchases"""
        return self._purchase_history
